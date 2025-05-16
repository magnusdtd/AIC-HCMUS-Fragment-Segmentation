import { Link } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { useRef, useState, useEffect } from 'react';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

export default function NavBar() {
  const { user, logout } = useUser();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuOpen]);

  return (
    <nav className="bg-gray-800 p-4">
      <div className="container mx-auto flex justify-between items-center relative">
        {/* Left: Logo */}
        <div className="flex items-center space-x-4">
          <Link to="/">
          <img src="ai-made-by-rock-fragment.svg" alt="HCMUS AI Challenge" className="h-8" />
          </Link>
            <a
            href="https://github.com/magnusdtd/AIC-HCMUS-Fragment-Segmentation"
            className="text-gray-300 hover:text-white"
            target="_blank"
            rel="noopener noreferrer"
            >
            Docs
            </a>
            <a
            href="https://github.com/magnusdtd/AIC-HCMUS-Fragment-Segmentation"
            className="text-gray-300 hover:text-white"
            target="_blank"
            rel="noopener noreferrer"
            >
            Githubs
            </a>
        </div>


        {/* Center: Navigation Links - absolutely centered */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex space-x-4 items-center">
          {user && (
            <>
              <Link to="/predict" className="text-gray-300 hover:text-white">Predict</Link>
              <Link to="/images" className="text-gray-300 hover:text-white">Images</Link>
            </>
          )}
        </div>

        {/* Right: User Info or Auth Links */}
        <div className="flex space-x-4 items-center">
          {user ? (
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setMenuOpen((open) => !open)}
                className="px-3 py-1 bg-gray-700 text-gray-200 rounded hover:bg-gray-600 focus:outline-none flex items-center gap-2"
                aria-label="Account menu"
              >
                <AccountCircleIcon />
                <span className="hidden sm:inline">{user.username}</span>
                <span className="ml-1">&#x25BC;</span>
              </button>
              {menuOpen && (
                <div className="absolute right-0 mt-2 w-40 bg-white rounded shadow-lg z-50 border border-gray-200">
                  <div className="px-4 py-2 text-gray-800 border-b border-gray-100">{user.username}</div>
                  <button
                    onClick={logout}
                    className="w-full text-left px-4 py-2 text-red-500 hover:bg-gray-100 hover:text-red-700"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
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