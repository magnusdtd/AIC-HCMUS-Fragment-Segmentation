import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, useLocation } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Main from './components/Main';
import './App.css';
import { useUser } from './context/UserContext';
import { jwtDecode } from 'jwt-decode';
import api from './services/api';
import { AuroraBackground } from './components/ui/aurora-background';
import { motion } from 'motion/react';
import { TextGenerateEffect } from './components/ui/text-generate-effect';
import NavBar from './components/ui/nav-bar';
import TechStackBar from './components/ui/tech-stack-bar';

type DecodedToken = {
  exp?: number; 
};

const techSkills = [
  { name: 'Vite', logo: 'Vite.svg' },
  { name: 'React', logo: 'React.png' },
  { name: 'TypeScript', logo: 'TypeScript.svg' },
  { name: 'TailwindCSS', logo: 'TailwindCSS.svg' },
  { name: 'FastAPI', logo: 'FastAPI.svg' },
  { name: 'Celery', logo: 'Celery.png' },
  { name: 'PostgreSQL', logo: 'Postgresql.svg' },
  { name: 'MinIO', logo: 'MinIO.png' },
  { name: 'Redis', logo: 'Redis.svg' },
  { name: 'Prometheus', logo: 'Prometheus.png' },
  { name: 'Grafana', logo: 'Grafana.png' },
  { name: 'Nginx', logo: 'Nginx.svg' },
  { name: 'Kubernetes', logo: 'Kubernetes.svg' },
  { name: 'GCP', logo: 'GCP.svg' },
  { name: 'GitHubActions', logo: 'GitHubActions.svg' },
  { name: 'Duckdns', logo: 'duckdns.png' }
];

const isTokenExpired = (token: string): boolean => {
  try {
    const decodedToken = jwtDecode<DecodedToken>(token);
    const currentTime = Date.now() / 1000;
    return decodedToken.exp ? decodedToken.exp < currentTime : true;
  } catch (error) {
    console.error('Failed to decode token: ', error);
    return true;
  }
};

const TechStackBarWrapper = () => {
  const location = useLocation();
  return location.pathname === '/' ? <TechStackBar skills={techSkills} /> : null;
};

export default function App() {
  const { user, login, logout } = useUser();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCurrentUser = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        if (isTokenExpired(token)) {
          logout();
        } else {
          try {
            const response = await api.get('/api/auth/current-user', {
              headers: { Authorization: `Bearer ${token}` },
            });
            if (response.data.message === 'Token is valid') {
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
    return (
      <div className='flex items-center justify-center h-screen'>
        <h1 className='text-2xl font-sans'>Loading...</h1>
      </div>
    );
  }

  return (
    <Router>
      <NavBar />
      <Routes>
        <Route
          path='/'
          element={
            <AuroraBackground>
              <motion.div
                initial={{ opacity: 0.0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{
                  delay: 0.3,
                  duration: 0.8,
                  ease: 'easeInOut',
                }}
                className='relative flex flex-col gap-4 items-center justify-center px-4'
              >
                <TextGenerateEffect 
                  words={'GDGoC HCMUS AI Challenge'} 
                  className='text-[120px] font-bold' 
                />
                <TextGenerateEffect 
                  words={'Rock Fragment Segmentation App'} 
                  className='text-[60px] font-sans' 
                />
              </motion.div>
            </AuroraBackground>
          }
        />
        <Route path='/login' element={<Login />} />
        <Route path='/register' element={<Register />} />
        <Route
          path='/main/*'
          element={
            user ? (
              <Main />
            ) : (
              <Navigate to='/' />
            )
          }
        />
      </Routes>
      <TechStackBarWrapper />
    </Router>
  );
}
