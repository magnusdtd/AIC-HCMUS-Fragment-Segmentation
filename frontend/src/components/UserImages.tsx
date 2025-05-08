import { useEffect, useState } from 'react';
import api from '../services/api';

// Define the type for an image object
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

  if (loading) return <div>Loading images...</div>;
  if (error) return <div>{error}</div>;

  if (images.length === 0) {
    return <div>No images found. Start uploading your images!</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Your Images</h2>
      <div className="grid grid-cols-3 gap-4">
        {images.map((image, index) => (
          <div key={index} className="border p-2">
            {image.url ? (
              <img
                src={image.url}
                alt={image.filename}
                className="w-full h-auto"
              />
            ) : (
              <div className="text-red-500">Failed to load image</div>
            )}
            <p className="mt-2 text-sm">{image.filename}</p>
            <p className="text-xs">Size: {image.size} bytes</p>
            <p className="text-xs">Uploaded: {new Date(image.upload_time).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default UserImages;