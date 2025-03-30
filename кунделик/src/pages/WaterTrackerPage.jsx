import React, { useState, useEffect } from 'react'
import '../styles/WaterTrackerPage.css'

function WaterTrackerPage() {
  const [waterIntake, setWaterIntake] = useState(0)
  const [dailyGoal, setDailyGoal] = useState(2000) // 2 литра по умолчанию
  const [history, setHistory] = useState([])

  // Сохранение данных в localStorage
  useEffect(() => {
    const savedWaterIntake = localStorage.getItem('waterIntake')
    const savedHistory = JSON.parse(localStorage.getItem('waterHistory')) || []
    
    if (savedWaterIntake) {
      setWaterIntake(Number(savedWaterIntake))
    }
    
    setHistory(savedHistory)
  }, [])

  // Обновление localStorage при изменении данных
  useEffect(() => {
    localStorage.setItem('waterIntake', waterIntake)
    localStorage.setItem('waterHistory', JSON.stringify(history))
  }, [waterIntake, history])

  const addWater = (amount) => {
    const newTotal = waterIntake + amount
    setWaterIntake(newTotal)
    
    const newEntry = {
      date: new Date().toLocaleString(),
      amount: amount
    }
    setHistory([...history, newEntry])
  }

  const resetDaily = () => {
    setWaterIntake(0)
    setHistory([])
  }

  const getProgressPercentage = () => {
    return Math.min((waterIntake / dailyGoal) * 100, 100)
  }

  return (
    <div className="water-tracker">
      <h1>Су ішу трекері</h1>
      
      <div className="water-goal">
        <h2>Күндізгі мақсат: {dailyGoal} мл</h2>
        <div className="progress-bar">
          <div 
            className="progress" 
            style={{width: `${getProgressPercentage()}%`}}
          ></div>
        </div>
        <p>{waterIntake} / {dailyGoal} мл</p>
      </div>

      <div className="water-buttons">
        <button onClick={() => addWater(250)}>+ 250 мл</button>
        <button onClick={() => addWater(500)}>+ 500 мл</button>
        <button onClick={() => addWater(1000)}>+ 1000 мл</button>
      </div>

      <div className="water-history">
        <h2>Су ішу тарихы</h2>
        {history.length === 0 ? (
          <p>Əлі ешқандай жазба жоқ</p>
        ) : (
          <ul>
            {history.map((entry, index) => (
              <li key={index}>
                {entry.date}: {entry.amount} мл
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="water-actions">
        <button 
          className="reset-button" 
          onClick={resetDaily}
        >
          Күнделікті нөлдеу
        </button>
      </div>
    </div>
  )
}

export default WaterTrackerPage