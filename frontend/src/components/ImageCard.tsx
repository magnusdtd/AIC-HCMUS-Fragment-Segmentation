import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';

interface ImageCardProps {
  image: {
    filename: string;
    size: number;
    upload_time: string;
    url?: string;
  };
  onClick: () => void;
}

const ImageCard: React.FC<ImageCardProps> = ({ image, onClick }) => {
  return (
    <Card sx={{ maxWidth: 512 }} onClick={onClick} className="cursor-pointer">
      <CardContent className="flex flex-col items-center">
        {image.url ? (
          <img
            src={image.url}
            alt={image.filename}
            className="w-full h-auto"
            style={{ objectFit: 'contain' }}
          />
        ) : (
          <div className="text-red-500 dark:text-red-400">Failed to load image</div>
        )}
        <p className="mt-2 text-sm text-gray-900 dark:text-black">{image.filename}</p>
        <p className="text-xs text-gray-700 dark:text-black">Size: {image.size} bytes</p>
        <p className="text-xs text-gray-700 dark:text-black">Uploaded: {new Date(image.upload_time).toLocaleString()}</p>
      </CardContent>
    </Card>
  );
};

export default ImageCard;
