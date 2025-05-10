import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Main from './components/Main';
import './App.css';
import { useUser } from './context/UserContext';
import { jwtDecode } from 'jwt-decode';
import api from './services/api';
import { AuroraBackground } from './components/ui/aurora-background';
import { motion } from "motion/react";
import { TextGenerateEffect } from "./components/ui/text-generate-effect";

type DecodedToken = {
  exp?: number; 
};

export default function App() {
  const { user, login, logout } = useUser();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCurrentUser = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        const decodedToken: DecodedToken = jwtDecode(token);
        const currentTime = Date.now() / 1000; 
        if (decodedToken.exp && decodedToken.exp < currentTime) {
          console.log("Token expired");
          logout();
        } else {
          try {
            const response = await api.get('/api/auth/current-user', {
              headers: { Authorization: `Bearer ${token}` },
            });
            if (response.data.message === "Token is valid") {
              login(response.data.user);
            }
          } catch (error) {
            console.error('Failed to fetch current user: ', error);
            logout();
          }
        }
      }
      setLoading(false);
    };
    fetchCurrentUser();
  }, [login, logout]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <AuroraBackground>
              <motion.div
                initial={{ opacity: 0.0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{
                  delay: 0.3,
                  duration: 0.8,
                  ease: "easeInOut",
                }}
                className="relative flex flex-col gap-4 items-center justify-center px-4"
              >
                <TextGenerateEffect 
                  words={"HCMUS AI Challenge"} 
                  className="text-[120px] font-bold" 
                />
                <TextGenerateEffect 
                  words={"Fragment segmentation track"} 
                  className="text-[60px] font-sans" 
                />
                <div className="flex gap-4 justify-center">
                  <Link to="/login">
                    <button className="p-[3px] relative">
                      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg" />
                      <div className="px-8 py-2 bg-black rounded-[6px] relative group transition duration-200 text-white hover:bg-transparent">
                        Login
                      </div>
                    </button>
                  </Link>
                  <Link to="/register">
                    <button className="p-[3px] relative">
                      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg" />
                      <div className="px-8 py-2 bg-black rounded-[6px] relative group transition duration-200 text-white hover:bg-transparent">
                        Register
                      </div>
                    </button>
                  </Link>
                </div>
              </motion.div>
            </AuroraBackground>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/main"
          element={
            user ? (
              <Main/> 
            ) : (
              <Navigate to="/" />
            )
          }
        />
      </Routes>
    </Router>
  );
}
