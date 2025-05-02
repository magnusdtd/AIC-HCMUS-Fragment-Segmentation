import { useState } from 'react';
import Predict from './Predict';
import UserImages from './UserImages';
import { useUser } from './../context/UserContext';

function Main () {
  const [activeFeature, setActiveFeature] = useState('Predict');
  const { logout } = useUser();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <div className="w-1/4 bg-gray-800 text-white p-4">
        <h2 className="text-2xl font-bold mb-6">App Features</h2>
        <ul>
          <li
            className={`cursor-pointer p-2 rounded ${activeFeature === 'Predict' ? 'bg-gray-600' : ''}`}
            onClick={() => setActiveFeature('Predict')}
          >
            Predict
          </li>
          <li
            className={`cursor-pointer p-2 rounded ${activeFeature === 'UserImages' ? 'bg-gray-600' : ''}`}
            onClick={() => setActiveFeature('UserImages')}
          >
            Your Images
          </li>
        </ul>
        <button
          onClick={handleLogout}
          className="mt-6 px-4 py-2 bg-red-500 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      {/* Main Content */}
      <div className="w-3/4 p-6">
        {activeFeature === 'Predict' && <Predict />}
        {activeFeature === 'UserImages' && <UserImages />}
      </div>
    </div>
  );
}

export default Main;