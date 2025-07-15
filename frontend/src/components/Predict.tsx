import React, { useState, useEffect } from "react";
import api from "../services/api";
import { useSearchParams } from "react-router-dom";
import PredictSetter from "./PredictSetter";
import PredictImageDisplayer from "./PredictImageDisplayer";
import JSZip from "jszip";

function Predict() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string>("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<string | null>(null);
  const [overlaidImage, setOverlaidImage] = useState<string | null>(null);
  const [originalImagePreview, setOriginalImagePreview] = useState<string | null>(null);
  const [cdfChart, setCdfChart] = useState<string | null>(null);
  const [isCalibrated, setIsCalibrated] = useState<boolean | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [realRadius, setRealRadius] = useState<string>("50");
  const [unit, setUnit] = useState<string>("cm");
  const [conf, setConf] = useState<number>(0.5);
  const [iou, setIou] = useState<number>(0.5);

  const [searchParams] = useSearchParams();
  const imageFilename = searchParams.get("image");

  useEffect(() => {
    if (imageFilename) {
      const fetchImage = async () => {
        try {
          const token = localStorage.getItem("token");
          const response = await api.get(`/api/fetch_image/${imageFilename}`, {
            responseType: "blob",
            headers: { Authorization: `Bearer ${token}` },
          });
          const imageUrl = URL.createObjectURL(response.data);
          setOriginalImagePreview(imageUrl);
          setFile(null); 
        } catch (error) {
          console.error("Error fetching image for prediction:", error);
          setMessage("Failed to load the selected image for prediction.");
        }
      };
      fetchImage();
    }
  }, [imageFilename]);

  // Handle file upload and get task_id
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file && !imageFilename) {
      setMessage("Please select a file to upload or use the provided image.");
      return;
    }
    setIsProcessing(true);
    try {
      const token = localStorage.getItem("token");
      // Check if the image already exists on the server
      const checkResponse = await api.get<{ exists: boolean }>(`/api/check_image_exists?img_name=${imageFilename || file?.name}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (checkResponse.data.exists) {

        const rePredictResponse = await api.get<{ task_id: string }>(
          `/api/re_predict/${realRadius}&${imageFilename || file?.name}&${unit}&${conf}&${iou}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setTaskId(rePredictResponse.data.task_id);
        setMessage("Trying to re-predict...");
      } else {
        const formData = new FormData();
        if (file) {
          formData.append("file", file);
        } else if (imageFilename) {
          formData.append("imageFilename", imageFilename);
        }
        const uploadResponse = await api.post<{ task_id: string }>(
          `/api/upload_predict/${realRadius}&${unit}&${conf}&${iou}`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setTaskId(uploadResponse.data.task_id);
        setMessage("File uploaded successfully. Task is processing...");
      }
    } catch (error) {
      console.error(error);
      setMessage("Failed to process the image.");
      setIsProcessing(false); // Reset processing state on error
    }
  };

  // Clear error message and results when a file is selected
  useEffect(() => {
    if (file) {
      setMessage("");
      setOverlaidImage(null);
      setCdfChart(null);
      setIsCalibrated(null);
      setTaskStatus(null);
      setTaskId(null);
    }
  }, [file]);

  // Poll task status and fetch prediction if successful
  useEffect(() => {
    if (taskId) {
      const interval = setInterval(async () => {
        try {
          const token = localStorage.getItem("token");
          const statusResponse = await api.get<{ status: string }>(`/api/task_status/${taskId}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          setTaskStatus(statusResponse.data.status);
          if (statusResponse.data.status === "SUCCESS") {
            clearInterval(interval);
            // Fetch the zip file from get_prediction
            const zipResponse = await api.get(`/api/fetch_prediction/${taskId}`, {
              headers: { Authorization: `Bearer ${token}` },
              responseType: "blob",
            });
            const zip = await JSZip.loadAsync(zipResponse.data);
            // Extract images as blob URLs
            const overlaidImageBlob = await zip.file("overlaid_image.png")?.async("blob");
            const cdfChartBlob = await zip.file("cdf_chart.png")?.async("blob");
            const isCalibratedJson = await zip.file("is_calibrated.json")?.async("string");
            setOverlaidImage(overlaidImageBlob ? URL.createObjectURL(overlaidImageBlob) : null);
            setCdfChart(cdfChartBlob ? URL.createObjectURL(cdfChartBlob) : null);
            if (isCalibratedJson) {
              const parsed = JSON.parse(isCalibratedJson);
              setIsCalibrated(parsed.is_calibrated);
            } else {
              setIsCalibrated(null);
            }
            setMessage("Prediction completed successfully.");
            setIsProcessing(false); // Reset processing state on success
          }
        } catch (error) {
          console.error(error);
          setMessage("Failed to fetch task status.");
          clearInterval(interval);
          setIsProcessing(false); // Reset processing state on error
        }
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [taskId]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-900">
      <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Predict</h2>
      <PredictSetter
        file={file}
        setFile={setFile}
        realRadius={realRadius}
        setRealRadius={setRealRadius}
        unit={unit}
        setUnit={setUnit}
        conf={conf}
        setConf={setConf}
        iou={iou}
        setIou={setIou}
        isProcessing={isProcessing}
        handleUpload={handleUpload}
        taskStatus={taskStatus}
        setOriginalImagePreview={setOriginalImagePreview}
      />
      {message && <p className="mt-4 text-red-500 dark:text-red-400">{message}</p>}
      <PredictImageDisplayer
        originalImagePreview={originalImagePreview}
        overlaidImage={overlaidImage}
        cdfChart={cdfChart}
        isCalibrated={isCalibrated}
      />
    </div>
  );
}

export default Predict;