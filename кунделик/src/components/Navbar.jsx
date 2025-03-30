import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import '../styles/Navbar.css';
import { logout } from '../api/auth';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const location = useLocation();
  const navigate = useNavigate();

  // Проверяем авторизацию при загрузке и изменении маршрута
  useEffect(() => {
    checkAuth();
    setIsMenuOpen(false);
  }, [location]);

  const checkAuth = () => {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (token && user) {
      setIsLoggedIn(true);
      setUsername(user.username || '');
    } else {
      setIsLoggedIn(false);
      setUsername('');
    }
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
    setUsername('');
    navigate('/login');
  };

  // Проверяем, находимся ли на странице входа или регистрации
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          DenSaulyq Tracker
        </Link>
        
        {!isAuthPage && (
          <>
            <div className="menu-icon" onClick={toggleMenu}>
              <i className={isMenuOpen ? 'fas fa-times' : 'fas fa-bars'} />
            </div>
            
            <ul className={`nav-menu ${isMenuOpen ? 'active' : ''}`}>
              <li className="nav-item">
                <Link to="/" className="nav-link" onClick={toggleMenu}>
                  Негізгі бет
                </Link>
              </li>
              
              {isLoggedIn ? (
                <>
                  <li className="nav-item">
                    <Link to="/water" className="nav-link" onClick={toggleMenu}>
                      Су ішу
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link to="/sleep" className="nav-link" onClick={toggleMenu}>
                      Ұйқы
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link to="/nutrition" className="nav-link" onClick={toggleMenu}>
                      Тамақтану
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link to="/progress" className="nav-link" onClick={toggleMenu}>
                      Прогресс
                    </Link>
                  </li>
                  <li className="nav-item user-menu">
                    <span className="nav-link username">
                      {username}
                    </span>
                    <div className="user-dropdown">
                      <button className="logout-btn" onClick={handleLogout}>
                        Шығу
                      </button>
                    </div>
                  </li>
                </>
              ) : (
                <>
                  <li className="nav-item">
                    <Link to="/login" className="nav-link" onClick={toggleMenu}>
                      Кіру
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link to="/register" className="nav-link" onClick={toggleMenu}>
                      Тіркелу
                    </Link>
                  </li>
                </>
              )}
            </ul>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;