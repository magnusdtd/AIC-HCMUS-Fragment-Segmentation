import React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";

interface PredictImageDisplayerProps {
  originalImagePreview: string | null;
  overlaidImage: string | null;
  cdfChart: string | null;
  isCalibrated: boolean | null;
}

const PredictImageDisplayer: React.FC<PredictImageDisplayerProps> = ({
  originalImagePreview,
  overlaidImage,
  cdfChart,
  isCalibrated,
}) => (
  <>
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
                src={overlaidImage}
                alt="Overlaid Prediction"
                style={{ width: '100%', objectFit: 'contain' }}
              />
            </CardContent>
          </Card>
        )}
      </div>
    )}
    {cdfChart && (
      <div className="mt-8">
        <h3 className="text-xl font-bold text-center text-gray-900 dark:text-white">Diameter CDF</h3>
        <img
          src={cdfChart}
          alt="CDF Chart"
          className="border p-2 dark:border-gray-600"
        />
      </div>
    )}
    {isCalibrated !== null && (
      <p className="mt-4 text-gray-900 dark:text-white">
        Calibration: {" "}
        <span className={isCalibrated ? "text-green-500 dark:text-green-400" : "text-red-500 dark:text-red-400"}>
          {isCalibrated
            ? "This image contains a calibrated object."
            : "There is no calibrated object in this image."}
        </span>
      </p>
    )}
  </>
);

export default PredictImageDisplayer; 