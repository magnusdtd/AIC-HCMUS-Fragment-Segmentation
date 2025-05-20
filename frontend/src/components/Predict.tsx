import React, { useState, useEffect } from "react";
import api from "../services/api";
import CircularProgress from "@mui/material/CircularProgress";
import { useDropzone } from "react-dropzone";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Tooltip from '@mui/material/Tooltip';
import { useSearchParams } from "react-router-dom";

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

  // Handle drag and drop
  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    if (!isProcessing && acceptedFiles && acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setOriginalImagePreview(URL.createObjectURL(acceptedFiles[0]));
    }
  }, [isProcessing]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: { 'image/*': [] },
    disabled: isProcessing, // Disable drag & drop when processing
  });

  // Handle file upload and get task_id
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file && !imageFilename) {
      setMessage("Please select a file to upload or use the provided image.");
      return;
    }

    setIsProcessing(true); // Set processing state to true

    try {
      const token = localStorage.getItem("token");

      // Check if the image already exists on the server
      const checkResponse = await api.get<{ exists: boolean }>(`/api/check_image_exists?img_name=${imageFilename || file?.name}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (checkResponse.data.exists) {
        // If the image exists, use the re-predict API
        const rePredictResponse = await api.get<{ task_id: string }>(`/api/re_predict?img_name=${imageFilename || file?.name}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setTaskId(rePredictResponse.data.task_id);
        setMessage("Trying to re-predict...");
      } else {
        // If the image does not exist, upload it
        const formData = new FormData();
        if (file) {
          formData.append("file", file);
        } else if (imageFilename) {
          formData.append("imageFilename", imageFilename);
        }

        const uploadResponse = await api.post<{ task_id: string }>("/api/upload_predict", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${token}`,
          },
        });

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

            const resultResponse = await api.get<{
              status: string;
              result: {
                overlaid_image: string;
                cdf_chart: string;
                is_calibrated: boolean;
              };
            }>(`/api/fetch_prediction/${taskId}`, {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            });
            setOverlaidImage(resultResponse.data.result.overlaid_image);
            setCdfChart(resultResponse.data.result.cdf_chart);
            setIsCalibrated(resultResponse.data.result.is_calibrated);
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
      <form onSubmit={handleUpload}>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded p-6 mb-4 w-80 flex flex-col items-center justify-center cursor-pointer transition-colors duration-200 ${isDragActive ? 'border-blue-500 bg-blue-50 dark:bg-blue-800' : 'border-gray-300 bg-white dark:border-gray-600 dark:bg-gray-800'}`}
        >
          <input {...getInputProps()} disabled={isProcessing} />
          {isDragActive ? (
            <p className="text-blue-500 dark:text-blue-300">Drop the file here ...</p>
          ) : file ? (
            <p className="text-green-600 dark:text-green-400">Selected: {file.name}</p>
          ) : (
            <p className="text-gray-700 dark:text-gray-200">Drag & drop an image here, or click to select a file</p>
          )}
        </div>
        <div className="flex justify-center items-center gap-4">
          <Tooltip title="Click to run the model and get predictions for your image!" arrow placement="left">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700"
              disabled={isProcessing} // Disable button when processing
            >
              Predict
            </button>
          </Tooltip>
          {/* Show progress bar next to Predict button while task is processing */}
          {taskStatus && taskStatus !== "SUCCESS" && (
            <div className="flex items-center">
              <CircularProgress size={28} />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-200">{taskStatus}</span>
            </div>
          )}
        </div>
      </form>
      {message && <p className="mt-4 text-red-500 dark:text-red-400">{message}</p>}

      {/* Display original and overlaid images side by side */}
      {(originalImagePreview || overlaidImage) && (
        <div className="mt-4 flex flex-col md:flex-row gap-4">
          {originalImagePreview && (
            <Card sx={{ maxWidth: 512 }}>
              <CardContent>
                <h3 className="text-xl font-bold text-center text-gray-900 dark:text-black">Your Image</h3>
                <img
                  src={originalImagePreview}
                  alt="Original"
                  style={{ width: '100%', objectFit: 'contain' }}
                />
              </CardContent>
            </Card>
          )}
          {overlaidImage && (
            <Card sx={{ maxWidth: 512 }}>
              <CardContent>
                <h3 className="text-xl font-bold text-center text-gray-900 dark:text-black">Overlaid Prediction</h3>
                <img
                  src={`data:image/png;base64,${overlaidImage}`}
                  alt="Overlaid Prediction"
                  style={{ width: '100%', objectFit: 'contain' }}
                />
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Display CDF chart */}
      {cdfChart && (
        <div className="mt-8">
          <h3 className="text-xl font-bold text-center text-gray-900 dark:text-white">Diameter CDF</h3>
          <img
            src={`data:image/png;base64,${cdfChart}`}
            alt="CDF Chart"
            className="border p-2 dark:border-gray-600"
          />
        </div>
      )}

      {/* Display whether the image is calibrated or not */}
      {isCalibrated !== null && (
        <p className="mt-4 text-gray-900 dark:text-white">
          Model Calibration: {" "}
          <span className={isCalibrated ? "text-green-500 dark:text-green-400" : "text-red-500 dark:text-red-400"}>
            {isCalibrated
              ? "This image contains a calibrated object."
              : "There is no calibrated object in this image."}
          </span>
        </p>
      )}
    </div>
  );
}

export default Predict;