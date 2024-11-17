import { isExpired } from 'react-jwt';


export const isTokenValid = () => {
  const token = localStorage.getItem('token');
  return token && !isExpired(token); // Returns true if valid, false otherwise
};