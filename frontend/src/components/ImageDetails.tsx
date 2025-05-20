import React, { useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

interface Task {
  task_id: string;
  created_at: string;
}

interface ImageDetailsProps {
  image: {
    filename: string;
    size: number;
    upload_time: string;
    url?: string;
  };
  tasks: Task[];
  onBack: () => void;
}

const ImageDetails: React.FC<ImageDetailsProps> = ({ image, tasks, onBack }) => {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [predictionDetails, setPredictionDetails] = useState<{ overlaidImage: string; cdfChart: string } | null>(null);
  const navigate = useNavigate(); 

  const handleDownload = async (taskId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get(`api/download_results/${taskId}`, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${token}` }
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `results_${taskId}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading results:', error);
    }
  };

  const handleViewPrediction = async (taskId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get(`api/get_prediction/${taskId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!response.data.result) {
        console.error("Result attribute is missing in the API response");
        return;
      }
      const { overlaid_image, cdf_chart } = response.data.result;
      setPredictionDetails({ overlaidImage: overlaid_image, cdfChart: cdf_chart });
      setSelectedTask(tasks.find((task) => task.task_id === taskId) || null);
    } catch (error) {
      console.error('Error fetching prediction details:', error);
    }
  };

  const handleSwitchToPredict = () => {
    navigate(`/predict?image=${image.filename}`);
  };

  return (
    <div
      className="flex flex-col md:flex-row items-start justify-center min-h-screen bg-white dark:bg-gray-900"
    >
      {/* Combined Section for Small Devices */}
      <div className="flex flex-col items-center w-full md:w-1/2 p-4">
        <h2 className="text-2xl font-bold mt-4 mb-4 text-gray-900 dark:text-white">Image Details</h2>
        {image.url ? (
          <img
            src={image.url}
            alt={image.filename}
            className="w-full h-auto"
            style={{ objectFit: 'contain', maxWidth: '512px' }}
          />
        ) : (
          <div className="text-red-500 dark:text-red-400">Failed to load image</div>
        )}
        <p className="mt-2 text-sm text-gray-900 dark:text-white">{image.filename}</p>
        <p className="text-xs text-gray-700 dark:text-white">Size: {image.size} bytes</p>
        <p className="text-xs text-gray-700 dark:text-white">Uploaded: {new Date(image.upload_time).toLocaleString()}</p>

        <div className="w-full mt-4">
          <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-1 text-center">Predictions</h3>
          {tasks.length > 0 ? (
            <table className="min-w-full text-xs text-left text-gray-700 dark:text-white border border-gray-200 dark:border-gray-700">
              <thead>
                <tr>
                  <th className="px-2 py-1 border-b border-gray-200 dark:border-white">Task ID</th>
                  <th className="px-2 py-1 border-b border-gray-200 dark:border-white">Created At</th>
                  <th className="px-2 py-1 border-b border-gray-200 dark:border-white">Actions</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.task_id}>
                    <td className="px-2 py-1 border-b border-gray-200 dark:border-white">{task.task_id}</td>
                    <td className="px-2 py-1 border-b border-gray-200 dark:border-white">{new Date(task.created_at).toLocaleString()}</td>
                    <td className="px-2 py-1 border-b border-gray-200 dark:border-white">
                      <button
                        onClick={() => handleViewPrediction(task.task_id)}
                        className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 mr-2"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDownload(task.task_id)}
                        className="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 dark:bg-green-600 dark:hover:bg-green-700"
                      >
                        Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-xs text-gray-700 dark:text-black">No tasks found for this image.</p>
          )}
        </div>

        {selectedTask && predictionDetails && (
          <div className="mt-4 w-full">
            <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-1 text-center">Prediction Details</h3>
            <p className="text-xs text-center text-gray-700 dark:text-white">Task ID: {selectedTask.task_id}</p>
            <p className="text-xs text-center text-gray-700 dark:text-white">Created At: {new Date(selectedTask.created_at).toLocaleString()}</p>
            <div className="flex flex-col items-center mt-5">
              <img
                src={`data:image/png;base64,${predictionDetails.overlaidImage}`}
                alt="Overlaid Prediction"
                className="w-full h-auto mb-5"
                style={{ objectFit: 'contain', maxWidth: '512px' }}
              />
              <img
                src={`data:image/png;base64,${predictionDetails.cdfChart}`}
                alt="CDF Chart"
                className="w-full h-auto mb-5"
                style={{ objectFit: 'contain', maxWidth: '1024px' }}
              />
            </div>
          </div>
        )}

        <div className="flex gap-4 mt-4">
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-700"
          >
            Back
          </button>
          <button
            onClick={handleSwitchToPredict}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700"
          >
            Predict with this Image
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageDetails;
