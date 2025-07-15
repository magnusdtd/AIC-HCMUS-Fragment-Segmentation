import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Tooltip from '@mui/material/Tooltip';
import { useDropzone } from "react-dropzone";

interface PredictSetterProps {
  file: File | null;
  setFile: (file: File | null) => void;
  realRadius: string;
  setRealRadius: (val: string) => void;
  unit: string;
  setUnit: (val: string) => void;
  conf: number;
  setConf: (val: number) => void;
  iou: number;
  setIou: (val: number) => void;
  isProcessing: boolean;
  handleUpload: (e: React.FormEvent) => void;
  taskStatus: string | null;
  setOriginalImagePreview: (val: string | null) => void;
}

const PredictSetter: React.FC<PredictSetterProps> = ({
  file,
  setFile,
  realRadius,
  setRealRadius,
  unit,
  setUnit,
  conf,
  setConf,
  iou,
  setIou,
  isProcessing,
  handleUpload,
  taskStatus,
  setOriginalImagePreview
}) => {
  // Handle drag and drop
  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    if (!isProcessing && acceptedFiles && acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setOriginalImagePreview(URL.createObjectURL(acceptedFiles[0]));
    }
  }, [isProcessing, setFile, setOriginalImagePreview]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: { 'image/*': [] },
    disabled: isProcessing,
  });

  const handleRealRadiusChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRealRadius(e.target.value);
  };

  const handleUnitChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setUnit(e.target.value);
  };

  const handleConfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConf(parseFloat(e.target.value));
  };

  const handleIouChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIou(parseFloat(e.target.value));
  };

  return (
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
      {/* Real Radius Input */}
      <div className="mb-4">
        <label htmlFor="realRadiusInput" className="block text-gray-700 dark:text-gray-200 mb-2">
          Real Radius:
        </label>
        <input
          id="realRadiusInput"
          type="text"
          value={realRadius}
          onChange={handleRealRadiusChange}
          className="w-full px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          placeholder="Enter real radius"
        />
      </div>
      {/* Unit Selection */}
      <div className="mb-4">
        <label htmlFor="unit" className="block text-gray-700 dark:text-gray-200 mb-2">
          Unit:
        </label>
        <select
          id="unit"
          value={unit}
          onChange={handleUnitChange}
          className="w-full px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-600 dark:text-white"
        >
          <option value="m">m</option>
          <option value="dm">dm</option>
          <option value="cm">cm</option>
          <option value="mm">mm</option>
        </select>
      </div>
      {/* Confidence Slider */}
      <div className="mb-4">
        <label htmlFor="confSlider" className="block text-gray-700 dark:text-gray-200 mb-2">
          Confidence (Conf): {conf}
        </label>
        <input
          id="confSlider"
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={conf}
          onChange={handleConfChange}
          className="w-full"
        />
      </div>
      {/* IoU Slider */}
      <div className="mb-4">
        <label htmlFor="iouSlider" className="block text-gray-700 dark:text-gray-200 mb-2">
          Intersection over Union (IoU): {iou}
        </label>
        <input
          id="iouSlider"
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={iou}
          onChange={handleIouChange}
          className="w-full"
        />
      </div>
      <div className="flex justify-center items-center gap-4">
        <Tooltip title="Click to run the model and get predictions for your image!" arrow placement="left">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700"
            disabled={isProcessing}
          >
            Predict
          </button>
        </Tooltip>
        {taskStatus && taskStatus !== "SUCCESS" && (
          <div className="flex items-center">
            <CircularProgress size={28} />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-200">{taskStatus}</span>
          </div>
        )}
      </div>
    </form>
  );
};

export default PredictSetter; 