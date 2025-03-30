import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../styles/SleepTrackerPage.css'
import { getAuthHeader } from '../api/auth'

const API_URL = 'http://127.0.0.1:5000/api'

function SleepTrackerPage() {
  const [sleepStart, setSleepStart] = useState(null)
  const [sleepHistory, setSleepHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSleepData()
  }, [])

  const fetchSleepData = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/sleep`, getAuthHeader())
      
      // Set sleep history from API
      setSleepHistory(response.data.history || [])
      
      // Check if there's an active sleep session
      if (response.data.current_sleep) {
        setSleepStart(new Date(response.data.current_sleep))
      }
    } catch (error) {
      console.error('Failed to fetch sleep data:', error)
      setError('Деректерді жүктеу мүмкін болмады')
    } finally {
      setLoading(false)
    }
  }

  const startSleep = async () => {
    try {
      const response = await axios.post(`${API_URL}/sleep/start`, {}, getAuthHeader())
      setSleepStart(new Date(response.data.start_time))
    } catch (error) {
      console.error('Failed to start sleep tracking:', error)
      setError('Ұйқыны бастау мүмкін болмады')
    }
  }

  const endSleep = async () => {
    if (sleepStart) {
      try {
        const response = await axios.post(`${API_URL}/sleep/end`, {}, getAuthHeader())
        
        // Refresh sleep data to get updated history
        fetchSleepData()
        
        // Clear current sleep session
        setSleepStart(null)
      } catch (error) {
        console.error('Failed to end sleep tracking:', error)
        setError('Ұйқыны аяқтау мүмкін болмады')
      }
    }
  }

  const resetSleep = async () => {
    try {
      await axios.post(`${API_URL}/sleep/reset`, {}, getAuthHeader())
      setSleepHistory([])
      setSleepStart(null)
    } catch (error) {
      console.error('Failed to reset sleep data:', error)
      setError('Деректерді қалпына келтіру мүмкін болмады')
    }
  }

  if (loading) {
    return <div className="loading">Жүктелуде...</div>
  }

  return (
    <div className="sleep-tracker">
      <h1>Ұйқы трекері</h1>

      {error && <div className="error-message">{error}</div>}

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