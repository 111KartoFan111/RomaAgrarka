import React from 'react'
import { Link } from 'react-router-dom'
import '../styles/HomePage.css'

function HomePage() {
  return (
    <div className="home-page">
<div className="hero-section">
    <h1>DenSaulyq Tracker</h1>
    <p className='p5'>БЕЛСЕНДІ ДЕНСАУЛЫҚ БАҚЫЛАУ ЖАҢЕ ЖАҚСАРТУ</p>
    <a href="/progress" className="cta-button">Денсаулықты бақылауды бастаңыз</a>
</div>

      <div className="features">
        <div className="feature-grid">
          <div className="feature">
            <h3>Су ішу</h3>
            <p className='p2'>Күнделікті сумен қамтамасыз ету және мөлшерін бақылау</p>
            <Link to="/water" className="feature-link">Толығырақ</Link>
          </div>

          <div className="feature">
            <h3>Ұйқы</h3>
            <p className='p2'>Ұйқы режимін және сапасын қадағалау</p>
            <Link to="/sleep" className="feature-link">Толығырақ</Link>
          </div>

          <div className="feature">
            <h3>Тамақтану</h3>
            <p className='p2'>Дұрыс тамақтану жоспарын жасау</p>
            <Link to="/nutrition" className="feature-link">Толығырақ</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage