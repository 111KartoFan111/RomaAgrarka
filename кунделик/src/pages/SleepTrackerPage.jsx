import React, { useState, useEffect } from 'react'
import '../styles/SleepTrackerPage.css'

function SleepTrackerPage() {
  const [sleepStart, setSleepStart] = useState(null)
  const [sleepEnd, setSleepEnd] = useState(null)
  const [sleepHistory, setSleepHistory] = useState([])

  useEffect(() => {
    const savedHistory = JSON.parse(localStorage.getItem('sleepHistory')) || []
    setSleepHistory(savedHistory)
  }, [])

  useEffect(() => {
    localStorage.setItem('sleepHistory', JSON.stringify(sleepHistory))
  }, [sleepHistory])

  const startSleep = () => {
    setSleepStart(new Date())
  }

  const endSleep = () => {
    if (sleepStart) {
      const end = new Date()
      const duration = calculateSleepDuration(sleepStart, end)
      
      const newEntry = {
        start: sleepStart,
        end: end,
        duration: duration
      }

      setSleepHistory([...sleepHistory, newEntry])
      setSleepStart(null)
      setSleepEnd(end)
    }
  }

  const calculateSleepDuration = (start, end) => {
    const diff = end - start;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    return `${hours} сағ ${minutes} мин ${seconds} сек`;
  };
  

  const resetSleep = () => {
    setSleepHistory([])
  }

  return (
    <div className="sleep-tracker">
      <h1>Ұйқы трекері</h1>

      <div className="sleep-controls">
        {!sleepStart ? (
          <button 
            className="start-sleep-btn" 
            onClick={startSleep}
          >
            Ұйқыны бастау
          </button>
        ) : (
          <button 
            className="end-sleep-btn" 
            onClick={endSleep}
          >
            Ұйқыны аяқтау
          </button>
        )}
      </div>

      {sleepStart && (
        <div className="current-sleep">
          <p>Ұйқы басталды: {sleepStart.toLocaleTimeString()}</p>
        </div>
      )}

      <div className="sleep-history">
        <h3>Ұйқы тарихы</h3>
        {sleepHistory.length === 0 ? (
          <p>Əлі ешқандай жазба жоқ</p>
        ) : (
          <ul>
            {sleepHistory.map((entry, index) => (
              <li key={index}>
                {new Date(entry.start).toLocaleDateString()} - 
                Ұйқы уақыты: {entry.duration}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="sleep-actions">
        <button 
          className="reset-button" 
          onClick={resetSleep}
        >
          Тарихты тазалау
        </button>
      </div>
    </div>
  )
}

export default SleepTrackerPage