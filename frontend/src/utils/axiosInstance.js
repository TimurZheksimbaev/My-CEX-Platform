import axios from 'axios';
import { isTokenValid } from './checkToken';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/',
});

// Add Authorization header with JWT token
axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token && isTokenValid()) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

export default axiosInstance;
