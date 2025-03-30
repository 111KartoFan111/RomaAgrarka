import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import WaterTrackerPage from './pages/WaterTrackerPage'
import SleepTrackerPage from './pages/SleepTrackerPage.jsx'
import NutritionPage from './pages/NutritionPage'
import ProgressPage from './pages/ProgressPage'
import './App.css'

function App() {
  return (
    <div className="app">
      <Navbar />
      
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/water" element={<WaterTrackerPage />} />
          <Route path="/sleep" element={<SleepTrackerPage />} />
          <Route path="/nutrition" element={<NutritionPage />} />
          <Route path="/progress" element={<ProgressPage />} />
        </Routes>
      </main>

      <Footer />
    </div>
  )
}

export default App