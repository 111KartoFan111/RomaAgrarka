import React, { useState, useEffect } from 'react';
import '../styles/ProgressPage.css';

function ProgressPage() {
  const [weight, setWeight] = useState({
    current: 0,
    goal: 0,
    history: []
  });

  const [measurements, setMeasurements] = useState({
    height: 0,
    weight: 0  // Добавляем вес отдельно для BMI
  });

  useEffect(() => {
    const savedWeight = JSON.parse(localStorage.getItem('weightProgress'));
    const savedMeasurements = JSON.parse(localStorage.getItem('bodyMeasurements'));
    
    if (savedWeight) setWeight(savedWeight);
    if (savedMeasurements) setMeasurements(savedMeasurements);
  }, []);

  useEffect(() => {
    localStorage.setItem('weightProgress', JSON.stringify(weight));
    localStorage.setItem('bodyMeasurements', JSON.stringify(measurements));
  }, [weight, measurements]);

  const addWeightEntry = () => {
    if (weight.current > 0 && weight.goal > 0) {
      const newEntry = {
        date: new Date().toLocaleDateString('kk-KZ'),
        currentWeight: weight.current,
        goalWeight: weight.goal
      };
      setWeight(prev => ({ ...prev, history: [...prev.history, newEntry] }));
    }
  };

  const resetProgress = () => {
    setWeight({ current: 0, goal: 0, history: [] });
    setMeasurements({ height: 0, waist: 0, hip: 0, chest: 0 });
    localStorage.removeItem('weightProgress');
    localStorage.removeItem('bodyMeasurements');
  };

  const calculateBMI = () => {
    if (measurements.height > 0 && measurements.weight > 0) {
      const heightInMeters = measurements.height / 100;
      return (measurements.weight / (heightInMeters * heightInMeters)).toFixed(1);
    }
    return "Бой мен салмақ енгізіңіз";
  };
  
  

  return (
    <div className="progress-page">
      <h1 style={{ color: 'white' }}>Денсаулық Прогресі</h1>

      <div className="weight-tracker">
        <h2>Салмақ</h2>
        
        <div className="weight-inputs">
          <div className="input-group">
            <label>Ағымдағы салмақ (кг)</label>
            <input 
              type="number" 
              value={weight.current}
              onChange={(e) => setWeight(prev => ({ ...prev, current: Number(e.target.value) }))}
            />
          </div>

          <div className="input-group">
            <label>Мақсат салмақ (кг)</label>
            <input 
              type="number" 
              value={weight.goal}
              onChange={(e) => setWeight(prev => ({ ...prev, goal: Number(e.target.value) }))}
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
        onChange={(e) => setMeasurements(prev => ({ ...prev, height: Number(e.target.value) }))}
      />
    </div>

    <div className="input-group">
      <label htmlFor="bmi-weight">Салмақ (кг)</label>
      <input 
        id="bmi-weight"
        type="number" 
        value={measurements.weight}
        onChange={(e) => setMeasurements(prev => ({ ...prev, weight: Number(e.target.value) }))}
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