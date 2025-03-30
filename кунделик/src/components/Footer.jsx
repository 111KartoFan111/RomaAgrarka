import React, { useState } from 'react';
import '../styles/Footer.css';

function Footer() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <footer className="footer">
        <div className="footer-container">
          <p className="footer-text">&copy; 2025 Денсаулық Күнделігі. Барлық құқықтар қорғалған.</p>
          <div className="footer-links">
  <span className="footer-link" onClick={() => setIsModalOpen(true)}>
    Байланыс
  </span>
</div>

        </div>
      </footer>

      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Бізбен байланысу</h2>
            <p>Email: romaxxss@gmail.com</p>
            <p>Телефон: +7 (777) 206-72-05</p>
            <button className="close-button" onClick={() => setIsModalOpen(false)}>Жабу</button>
          </div>
        </div>
      )}
    </>
  );
}

export default Footer;
