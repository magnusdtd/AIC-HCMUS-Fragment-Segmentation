import { Link } from 'react-router-dom';
import { useUser } from '../../context/UserContext';

export default function NavBar() {
  const { user, logout } = useUser();

  return (
    <nav className="bg-gray-800 p-4">
      <div className="container mx-auto flex justify-between items-center">
        {/* Left: Logo */}
        <Link to="/" className="flex items-center space-x-2">
          <img src="ai-made-by-rock-fragment.svg" alt="HCMUS AI Challenge" className="h-8" />
          <h1 className="text-gray-300 hover:text-white font-sans">RFSA</h1>
        </Link>

        {/* Center: Navigation Links */}
        <div className="flex space-x-4 items-center">
          {user && (
            <>
              <Link to="/main/predict" className="text-gray-300 hover:text-white">Predict</Link>
              <Link to="/main/user-images" className="text-gray-300 hover:text-white">Your Images</Link>
            </>
          )}
        </div>

        {/* Right: User Info or Auth Links */}
        <div className="flex space-x-4 items-center">
          {user ? (
            <>
              <span className="text-gray-300">{user.username}</span>
              <button
                onClick={logout}
                className="text-red-500 hover:text-red-700"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-300 hover:text-white">Login</Link>
              <Link to="/register" className="text-gray-300 hover:text-white">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}