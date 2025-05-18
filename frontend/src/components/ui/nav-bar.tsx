import { Link } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { useRef, useState, useEffect } from 'react';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import Switch from '@mui/material/Switch';
import { styled } from '@mui/material/styles';

// MaterialUISwitch styled component
const MaterialUISwitch = styled(Switch)(({ theme }) => ({
  width: 62,
  height: 34,
  padding: 7,
  '& .MuiSwitch-switchBase': {
    margin: 1,
    padding: 0,
    transform: 'translateX(6px)',
    '&.Mui-checked': {
      color: '#fff',
      transform: 'translateX(22px)',
      '& .MuiSwitch-thumb:before': {
        backgroundImage: `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 20 20"><path fill="${encodeURIComponent(
          '#fff',
        )}" d="M4.2 2.5l-.7 1.8-1.8.7 1.8.7.7 1.8.6-1.8L6.7 5l-1.9-.7-.6-1.8zm15 8.3a6.7 6.7 0 11-6.6-6.6 5.8 5.8 0 006.6 6.6z"/></svg>')`,
      },
      '& + .MuiSwitch-track': {
        opacity: 1,
        backgroundColor: '#aab4be',
        ...(theme.palette.mode === 'dark' && {
          backgroundColor: '#8796A5',
        }),
      },
    },
  },
  '& .MuiSwitch-thumb': {
    backgroundColor: '#001e3c',
    width: 32,
    height: 32,
    '&::before': {
      content: "''",
      position: 'absolute',
      width: '100%',
      height: '100%',
      left: 0,
      top: 0,
      backgroundRepeat: 'no-repeat',
      backgroundPosition: 'center',
      backgroundImage: `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 20 20"><path fill="${encodeURIComponent(
        '#fff',
      )}" d="M9.305 1.667V3.75h1.389V1.667h-1.39zm-4.707 1.95l-.982.982L5.09 6.072l.982-.982-1.473-1.473zm10.802 0L13.927 5.09l.982.982 1.473-1.473-.982-.982zM10 5.139a4.872 4.872 0 00-4.862 4.86A4.872 4.872 0 0010 14.862 4.872 4.872 0 0014.86 10 4.872 4.872 0 0010 5.139zm0 1.389A3.462 3.462 0 0113.471 10a3.462 3.462 0 01-3.473 3.472A3.462 3.462 0 016.527 10 3.462 3.462 0 0110 6.528zM1.665 9.305v1.39h2.083v-1.39H1.666zm14.583 0v1.39h2.084v-1.39h-2.084zM5.09 13.928L3.616 15.4l.982.982 1.473-1.473-.982-.982zm9.82 0l-.982.982 1.473 1.473.982-.982-1.473-1.473zM9.305 16.25v2.083h1.389V16.25h-1.39z"/></svg>')`,
    },
    ...(theme.palette.mode === 'dark' && {
      backgroundColor: '#003892',
    }),
  },
  '& .MuiSwitch-track': {
    opacity: 1,
    backgroundColor: '#aab4be',
    borderRadius: 20 / 2,
    ...(theme.palette.mode === 'dark' && {
      backgroundColor: '#8796A5',
    }),
  },
}));

export default function NavBar() {
  const { user, logout } = useUser();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') === 'dark' ||
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
    return false;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

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
    <nav className="bg-gradient-to-r from-blue-500 to-purple-500 dark:bg-blue-800 p-4">
      <div className="container mx-auto flex justify-between items-center relative">
        {/* Left: Logo */}
        <div className="flex items-center space-x-4">
          <Link to="/">
          <img src="ai-made-by-rock-fragment.svg" alt="HCMUS AI Challenge" className="h-8" />
          </Link>
            <a
            href="https://magnusdtd.github.io/AIC-HCMUS-Fragment-Segmentation/"
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
          {/* Theme Switcher */}
          <div className="flex items-center">
            <MaterialUISwitch
              checked={darkMode}
              onChange={() => setDarkMode((prev) => !prev)}
            />
          </div>
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