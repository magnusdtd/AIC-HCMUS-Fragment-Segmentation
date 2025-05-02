import React, { useState } from "react";
import api from "../services/api";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function Predict() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string>("");
  const [overlaidImage, setOverlaidImage] = useState<string | null>(null);
  const [originalImagePreview, setOriginalImagePreview] = useState<string | null>(null);
  const [volumeData, setVolumeData] = useState<number[]>([]);
  const [isCalibrated, setIsCalibrated] = useState<boolean | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setOriginalImagePreview(URL.createObjectURL(selectedFile)); // Generate a preview URL for the original image
    }
  };

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
      const response = await api.post<{
        message: string;
        overlaid_image: string;
        volumes: number[];
        is_calibrated: boolean;
      }>("/api/upload_predict", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });

      setMessage(response.data.message);
      setOverlaidImage(response.data.overlaid_image);
      setVolumeData(response.data.volumes); 
      setIsCalibrated(response.data.is_calibrated);
    } catch (error) {
      console.error(error);
      setMessage("Failed to upload the file.");
    }
  };

  // Generate CDF data
  const generateCDF = (data: number[]) => {
    const sortedData = [...data].sort((a, b) => a - b);
    const cdf = sortedData.map((value, index) => ({
      x: value,
      y: (index + 1) / sortedData.length,
    }));
    return cdf;
  };

  const cdfData = generateCDF(volumeData);

  const chartData = {
    labels: cdfData.map((point) => point.x.toFixed(2)), // X-axis values
    datasets: [
      {
        label: "Volume",
        data: cdfData.map((point) => point.y), // Y-axis values
        borderColor: "rgba(75, 192, 192, 1)",
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Cumulative Distribution Function (CDF)",
      },
    },
  };

  return (
    <div>
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
      {volumeData.length > 0 && (
      <div className="mt-8">
        <h3 className="text-xl font-bold">Volume Data CDF</h3>
        <div style={{ maxWidth: "800px", margin: "0 auto" }}>
        <Line data={chartData} options={chartOptions} />
        </div>
      </div>
      )}

      {/* Display whether the image is calibrated or not */}
      {isCalibrated !== null && (
      <p className="mt-4">
        Model Calibration:{" "}
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