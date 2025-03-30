import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/ProgressPage.css';
import { getAuthHeader } from '../api/auth';

const API_URL = 'http://127.0.0.1:5000/api';

function ProgressPage() {
  const [weight, setWeight] = useState({
    current: 0,
    goal: 0,
    history: []
  });

  const [measurements, setMeasurements] = useState({
    height: 0,
    weight: 0
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProgressData();
  }, []);

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/progress`, getAuthHeader());
      
      setWeight({
        current: response.data.current_weight,
        goal: response.data.goal_weight,
        history: response.data.history.map(entry => ({
          date: new Date(entry.date).toLocaleDateString('kk-KZ'),
          currentWeight: entry.current_weight,
          goalWeight: entry.goal_weight
        }))
      });
      
      setMeasurements({
        height: response.data.height,
        weight: response.data.weight
      });
    } catch (error) {
      console.error('Failed to fetch progress data:', error);
      setError('Деректерді жүктеу мүмкін болмады');
    } finally {
      setLoading(false);
    }
  };

  const updateProgress = async (type, field, value) => {
    if (type === 'weight') {
      setWeight(prev => ({ ...prev, [field]: value }));
    } else if (type === 'measurements') {
      setMeasurements(prev => ({ ...prev, [field]: value }));
    }
  };

  const addWeightEntry = async () => {
    if (weight.current > 0 && weight.goal > 0) {
      try {
        await axios.post(
          `${API_URL}/progress/update`, 
          {
            current_weight: weight.current,
            goal_weight: weight.goal,
            add_entry: true
          },
          getAuthHeader()
        );
        
        // Refresh data to get the updated history
        fetchProgressData();
      } catch (error) {
        console.error('Failed to add weight entry:', error);
        setError('Салмақ жазбасын қосу мүмкін болмады');
      }
    }
  };

  const saveMeasurements = async () => {
    try {
      await axios.post(
        `${API_URL}/progress/update`,
        {
          height: measurements.height,
          weight: measurements.weight
        },
        getAuthHeader()
      );
    } catch (error) {
      console.error('Failed to save measurements:', error);
      setError('Өлшемдерді сақтау мүмкін болмады');
    }
  };

  const resetProgress = async () => {
    try {
      await axios.post(`${API_URL}/progress/reset`, {}, getAuthHeader());
      setWeight({ current: 0, goal: 0, history: [] });
      setMeasurements({ height: 0, weight: 0 });
    } catch (error) {
      console.error('Failed to reset progress data:', error);
      setError('Деректерді қалпына келтіру мүмкін болмады');
    }
  };

  const calculateBMI = () => {
    if (measurements.height > 0 && measurements.weight > 0) {
      const heightInMeters = measurements.height / 100;
      return (measurements.weight / (heightInMeters * heightInMeters)).toFixed(1);
    }
    return "Бой мен салмақ енгізіңіз";
  };

  if (loading) {
    return <div className="loading">Жүктелуде...</div>;
  }

  return (
    <div className="progress-page">
      <h1 style={{ color: 'white' }}>Денсаулық Прогресі</h1>

      {error && <div className="error-message">{error}</div>}

      <div className="weight-tracker">
        <h2>Салмақ</h2>
        
        <div className="weight-inputs">
          <div className="input-group">
            <label>Ағымдағы салмақ (кг)</label>
            <input 
              type="number" 
              value={weight.current}
              onChange={(e) => updateProgress('weight', 'current', Number(e.target.value))}
              onBlur={() => saveMeasurements()}
            />
          </div>

          <div className="input-group">
            <label>Мақсат салмақ (кг)</label>
            <input 
              type="number" 
              value={weight.goal}
              onChange={(e) => updateProgress('weight', 'goal', Number(e.target.value))}
              onBlur={() => saveMeasurements()}
            />
          </div>

          <button onClick={addWeightEntry}>Жазу</button>
        </div>

        <div className="weight-history">
          <h3>Салмақ тарихы</h3>
          {weight.history.length === 0 ? (
            <p>Əлі ешқандай жазба жоқ</p>
          ) : (
            <ul>
              {weight.history.map((entry, index) => (
                <li key={index}>
                  {entry.date}: Ағымдағы салмақ - {entry.currentWeight} кг, Мақсат салмақ - {entry.goalWeight} кг
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="body-measurements">
        <h2>Дене өлшемдері</h2>

        <div className="measurement-inputs">
          <div className="input-group">
            <label htmlFor="height">Бой (см)</label>
            <input 
              id="height"
              type="number" 
              value={measurements.height}
              onChange={(e) => updateProgress('measurements', 'height', Number(e.target.value))}
              onBlur={() => saveMeasurements()}
            />
          </div>

          <div className="input-group">
            <label htmlFor="bmi-weight">Салмақ (кг)</label>
            <input 
              id="bmi-weight"
              type="number" 
              value={measurements.weight}
              onChange={(e) => updateProgress('measurements', 'weight', Number(e.target.value))}
              onBlur={() => saveMeasurements()}
            />
          </div>
        </div>

        <div className="health-metrics">
          <p>Дене Салмақ Индексі (BMI): {calculateBMI()}</p>
        </div>
      </div>

      <div className="progress-actions">
        <button 
          className="reset-button" 
          onClick={resetProgress}
        >
          Барлық деректерді тазалау
        </button>
      </div>
    </div>
  );
}

export default ProgressPage;