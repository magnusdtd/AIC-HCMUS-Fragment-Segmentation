import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import api from "../services/api";
import { useUser } from "../context/UserContext";

function Login() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useUser();

  // Handle Google OAuth redirect
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tokenParam = params.get("token");
    if (tokenParam) {
      // No JSON.parse here, tokenParam is the JWT string
      const access_token = tokenParam;
      localStorage.setItem("token", access_token);
      api.get('/api/auth/current-user', {
        headers: { Authorization: `Bearer ${access_token}` },
      })
        .then((userResponse) => {
          login(userResponse.data);
          navigate("/predict");
        })
        .catch(() => {
          setMessage("Google login failed");
          localStorage.removeItem("token");
        });
    }
  }, [location.search, login, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await api.post<{ access_token: string }>("/api/auth/login", { username, password });
      const { access_token } = response.data;
      localStorage.setItem("token", access_token);

      const userResponse = await api.get('/api/auth/current-user', {
        headers: { Authorization: `Bearer ${access_token}` },
      });
      login(userResponse.data); 

      navigate("/predict");
    } catch (error: any) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="w-full max-w-md p-8 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-white">Login</h2>
        <form className="mt-6" onSubmit={handleLogin}>
          <div className="mb-4">
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-200">
              Username
            </label>
            <input
              type="text"
              id="username"
              className="w-full px-4 py-2 mt-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-200">
              Password
            </label>
            <input
              type="password"
              id="password"
              className="w-full px-4 py-2 mt-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />
          </div>
          <button
            type="submit"
            className="w-full px-4 py-2 text-white bg-blue-500 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-blue-600 dark:hover:bg-blue-700"
          >
            Login
          </button>
        </form>
        <div className="mt-4 flex flex-col items-center">
          <span className="text-gray-500 dark:text-gray-300 mb-2">or</span>
          <button
            type="button"
            className="w-full px-4 py-2 text-white bg-red-500 rounded-lg hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 flex items-center justify-center dark:bg-red-600 dark:hover:bg-red-700"
            onClick={() => {
              window.location.href = '/api/auth/google-login';
            }}
          >
            <svg className="w-5 h-5 mr-2" viewBox="0 0 48 48">
              <g>
                <path fill="#4285F4" d="M24 9.5c3.54 0 6.7 1.22 9.19 3.23l6.85-6.85C36.45 2.36 30.68 0 24 0 14.82 0 6.73 5.8 2.69 14.09l7.99 6.2C12.36 13.13 17.74 9.5 24 9.5z"/>
                <path fill="#34A853" d="M46.1 24.55c0-1.64-.15-3.22-.42-4.74H24v9.01h12.42c-.54 2.9-2.18 5.36-4.65 7.01l7.19 5.59C43.98 37.13 46.1 31.3 46.1 24.55z"/>
                <path fill="#FBBC05" d="M10.68 28.29c-1.13-3.36-1.13-6.97 0-10.33l-7.99-6.2C.86 16.09 0 19.94 0 24c0 4.06.86 7.91 2.69 12.24l7.99-6.2z"/>
                <path fill="#EA4335" d="M24 48c6.48 0 11.93-2.14 15.9-5.82l-7.19-5.59c-2.01 1.35-4.59 2.16-8.71 2.16-6.26 0-11.64-3.63-13.32-8.79l-7.99 6.2C6.73 42.2 14.82 48 24 48z"/>
                <path fill="none" d="M0 0h48v48H0z"/>
              </g>
            </svg>
            Login with Google
          </button>
        </div>
        {message && (
          <p className="mt-4 text-center text-sm text-red-600 font-medium dark:text-red-400">
            {message}
          </p>
        )}
      </div>
    </div>
  );
}

export default Login;