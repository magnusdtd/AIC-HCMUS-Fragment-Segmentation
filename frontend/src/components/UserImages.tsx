import { useEffect, useState } from 'react';
import api from '../services/api';
import ImageCard from './ImageCard';
import ImageDetails from './ImageDetails';

interface Image {
  filename: string;
  size: number;
  upload_time: string;
  url?: string; 
}

interface Task {
  task_id: string;
  created_at: string;
}

function UserImages() {
  const [images, setImages] = useState<Image[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tasks, setTasks] = useState<Record<string, Task[]>>({});
  const [selectedImage, setSelectedImage] = useState<Image | null>(null);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await api.get('/api/display_images', {
          headers: { Authorization: `Bearer ${token}` },
        });

        const imagesData = response.data.images;

        const imagesWithUrls = await Promise.all(
          imagesData.map(async (image: Image) => {
            try {
              const imageResponse = await api.get(`/api/fetch_image/${image.filename}`, {
                responseType: 'blob',
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

        const tasksData: Record<string, Task[]> = {};
        for (const image of imagesData) {
          try {
            const tasksResponse = await api.get(`/api/get_user_tasks?img_id=${image.id}`, {
              headers: { Authorization: `Bearer ${token}` },
            });
            tasksData[image.filename] = tasksResponse.data.tasks;
          } catch (err) {
            console.error(`Error fetching tasks for image ${image.filename}:`, err);
            tasksData[image.filename] = [];
          }
        }
        setTasks(tasksData);
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

  if (selectedImage) {
    return (
      <ImageDetails
        image={selectedImage}
        tasks={tasks[selectedImage.filename] || []}
        onBack={() => setSelectedImage(null)}
      />
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
          <ImageCard
            key={index}
            image={image}
            onClick={() => setSelectedImage(image)}
          />
        ))}
      </div>
    </div>
  );
}

export default UserImages;