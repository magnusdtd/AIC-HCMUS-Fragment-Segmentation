import { useEffect, useState } from 'react';
import api from '../services/api';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';

interface Image {
  filename: string;
  size: number;
  upload_time: string;
  url?: string; 
}

function UserImages() {
  const [images, setImages] = useState<Image[]>([]); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await api.get('/api/display_images', {
          headers: { Authorization: `Bearer ${token}` },
        });

        const imagesData = response.data.images;

        // Fetch each image's data from the server
        const imagesWithUrls = await Promise.all(
          imagesData.map(async (image: Image) => {
            try {
              const imageResponse = await api.get(`/api/fetch_image/${image.filename}`, {
                responseType: 'blob', // Fetch as binary data
              });
              const imageUrl = URL.createObjectURL(imageResponse.data); 
              return { ...image, url: imageUrl };
            } catch (err) {
              console.error('Error fetching image blob:', err); 
              return { ...image, url: '' }; 
            }
          })
        );

        setImages(imagesWithUrls);
      } catch (err) {
        console.error('Error fetching images:', err);
        setError('Failed to load images.');
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, []);

  if (loading) {
    return (
      <div className='flex items-center justify-center h-screen bg-white dark:bg-gray-900'>
        <h1 className='text-2xl font-sans text-gray-900 dark:text-white'>Loading...</h1>
      </div>
    );
  }
  if (error) {
    return (
      <div className='flex items-center justify-center h-screen bg-white dark:bg-gray-900'>
        <h1 className='text-xl text-red-700 dark:text-red-400'>{error}</h1>
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className='flex items-center text-2xl font-sans justify-center h-screen bg-white dark:bg-gray-900'>
        <h1 className='text-xl text-red-700 dark:text-red-400'>No images found. Start uploading your images!</h1>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-900">
      <h2 className="text-2xl font-bold mt-4 mb-4 text-gray-900 dark:text-white">Your Images</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {images.map((image, index) => (
          <Card key={index} sx={{ maxWidth: 512 }} >
            <CardContent className='flex flex-col items-center'>
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
        ))}
      </div>
    </div>
  );
}

export default UserImages;