import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const location = useLocation();

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = () => {
    // Simple check for token existence
    const token = localStorage.getItem('token');
    
    // Here you could add an API call to validate the token with your backend
    // For now, we're just checking if the token exists
    
    setIsAuthenticated(!!token);
    setIsLoading(false);
  };

  if (isLoading) {
    // You could add a loading spinner here
    return <div className="loading">Жүктелуде...</div>;
  }

  if (!isAuthenticated) {
    // Redirect to login page if not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;
