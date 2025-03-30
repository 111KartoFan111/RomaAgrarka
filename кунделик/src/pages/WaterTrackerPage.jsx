import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/WaterTrackerPage.css';
import { getAuthHeader } from '../api/auth';

const API_URL = 'http://127.0.0.1:5000/api';

function WaterTrackerPage() {
  const [waterIntake, setWaterIntake] = useState(0);
  const [dailyGoal, setDailyGoal] = useState(2000);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch water intake data
  const fetchWaterData = async () => {
    try {
      setLoading(true);
      const headers = getAuthHeader();
      const response = await axios.get(`${API_URL}/water`, headers);
      setWaterIntake(response.data.total_intake);
      setDailyGoal(response.data.daily_goal);
      setHistory(response.data.history.map(entry => ({
        date: new Date(entry.date).toLocaleString(),
        amount: entry.amount
      })));
      setError(null); // Clear any previous errors
    } catch (error) {
      console.error('Failed to fetch water data:', error);
      setError('Деректерді жүктеу мүмкін болмады');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWaterData();
  }, []);

  const addWater = async (amount) => {
    try {
      // Ensure amount is a number
      const numAmount = Number(amount);
      if (isNaN(numAmount)) {
        throw new Error('Invalid amount');
      }
      
      const headers = getAuthHeader();
      const response = await axios.post(
        `${API_URL}/water/add`,
        { amount: numAmount },
        headers
      );
      
      // Update the water intake value from the response
      setWaterIntake(response.data.total_intake);
      
      // Refresh the data to update the history
      fetchWaterData();
      setError(null); // Clear any previous errors
    } catch (error) {
      console.error('Failed to add water:', error);
      setError('Су қосу мүмкін болмады');
    }
  };

  const resetDaily = async () => {
    try {
      const headers = getAuthHeader();
      await axios.post(`${API_URL}/water/reset`, {}, headers);
      setWaterIntake(0);
      fetchWaterData(); // Refresh data after reset
      setError(null); // Clear any previous errors
    } catch (error) {
      console.error('Failed to reset water data:', error);
      setError('Деректерді қалпына келтіру мүмкін болмады');
    }
  };

  const getProgressPercentage = () => {
    return Math.min((waterIntake / dailyGoal) * 100, 100);
  };

  if (loading) {
    return <div className="loading">Жүктелуде...</div>;
  }

  return (
    <div className="water-tracker">
      <h1>Су ішу трекері</h1>
      
      {error && <div className="error-message">{error}</div>}
      
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
  );
}

export default WaterTrackerPage;