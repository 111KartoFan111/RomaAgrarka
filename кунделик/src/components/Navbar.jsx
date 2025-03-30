import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/Navbar.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation(); // Отслеживаем текущий путь

  // Сбрасываем состояние меню при смене страницы
  useEffect(() => {
    setIsMenuOpen(false);
  }, [location]);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
        DenSaulyq Tracker
        </Link>
        <div className="menu-icon" onClick={toggleMenu}>
          <i className={isMenuOpen ? 'fas fa-times' : 'fas fa-bars'} />
        </div>
        <ul className={`nav-menu ${isMenuOpen ? 'active' : ''}`}>
          <li className="nav-item">
            <Link to="/" className="nav-link" onClick={toggleMenu}>
              Негізгі бет
            </Link>
          </li>
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
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;