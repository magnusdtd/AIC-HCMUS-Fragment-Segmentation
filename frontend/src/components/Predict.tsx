import React, { useState, useEffect } from "react";
import api from "../services/api";
import CircularProgress from "@mui/material/CircularProgress";

function Predict() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string>("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<string | null>(null);
  const [overlaidImage, setOverlaidImage] = useState<string | null>(null);
  const [originalImagePreview, setOriginalImagePreview] = useState<string | null>(null);
  const [cdfChart, setCdfChart] = useState<string | null>(null);
  const [isCalibrated, setIsCalibrated] = useState<boolean | null>(null);

  // Handle file selection and preview generation
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setOriginalImagePreview(URL.createObjectURL(selectedFile));
    }
  };

  // Handle file upload and get task_id
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("token");
      const response = await api.post<{ task_id: string }>("/api/upload_predict", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });

      setTaskId(response.data.task_id);
      setMessage("File uploaded successfully. Task is processing...");
    } catch (error) {
      console.error(error);
      setMessage("Failed to upload the file.");
    }
  };

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
          }
        } catch (error) {
          console.error(error);
          setMessage("Failed to fetch task status.");
          clearInterval(interval);
        }
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [taskId]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Predict</h2>
      <form onSubmit={handleUpload}>
        <label
          htmlFor="fileInput"
          className="px-4 py-2 bg-amber-300 text-black rounded cursor-pointer hover:bg-amber-400"
        >
          Choose File
        </label>
        <input
          id="fileInput"
          type="file"
          onChange={handleFileChange}
          className="hidden"
        />
        <button
          type="submit"
          className="ml-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Upload
        </button>
      </form>
      {message && <p className="mt-4 text-red-500">{message}</p>}

      {/* Show progress bar while task is processing */}
      {taskStatus && taskStatus !== "SUCCESS" && (
        <div className="mt-4">
          <CircularProgress />
          <p className="mt-2">Task Status: {taskStatus}</p>
        </div>
      )}

      {/* Display original and overlaid images side by side */}
      {(originalImagePreview || overlaidImage) && (
        <div className="mt-4 flex gap-4">
          {originalImagePreview && (
            <div>
              <h3 className="text-xl font-bold">Original Image</h3>
              <img
                src={originalImagePreview}
                alt="Original"
                className="border p-2"
              />
            </div>
          )}
          {overlaidImage && (
            <div>
              <h3 className="text-xl font-bold">Overlaid Prediction</h3>
              <img
                src={`data:image/png;base64,${overlaidImage}`}
                alt="Overlaid Prediction"
                className="border p-2"
              />
            </div>
          )}
        </div>
      )}

      {/* Display CDF chart */}
      {cdfChart && (
        <div className="mt-8">
          <h3 className="text-xl font-bold">Volume Data CDF</h3>
          <img
            src={`data:image/png;base64,${cdfChart}`}
            alt="CDF Chart"
            className="border p-2"
          />
        </div>
      )}

      {/* Display whether the image is calibrated or not */}
      {isCalibrated !== null && (
        <p className="mt-4">
          Model Calibration: {" "}
          <span className={isCalibrated ? "text-green-500" : "text-red-500"}>
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