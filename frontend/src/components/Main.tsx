import Predict from './Predict';
import UserImages from './UserImages';
import { Routes, Route, useLocation } from 'react-router-dom';
import { useUser } from '../context/UserContext';

function Main() {
  const { user } = useUser();
  const location = useLocation();

  return (
    <div className="w-full p-6">
      <Routes>
        <Route path="predict" element={<Predict />} />
        <Route path="user-images" element={<UserImages />} />
      </Routes>
      {location.pathname !== '/main/predict' && location.pathname !== '/main/user-images' && (
        <div className="flex items-center justify-center h-screen">
          <h1 className="text-3xl font-bold">Welcome, {user?.username}!</h1>
        </div>
      )}
    </div>
  );
}

export default Main;


