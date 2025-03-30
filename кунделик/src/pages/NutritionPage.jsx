import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../styles/NutritionPage.css'
import { getAuthHeader } from '../api/auth'

const API_URL = 'http://127.0.0.1:5000/api'

function NutritionPage() {
  const [meals, setMeals] = useState([])
  const [totalCalories, setTotalCalories] = useState(0)
  const [dailyGoal, setDailyGoal] = useState(2000)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchNutritionData()
  }, [])

  // Calculate total calories whenever meals update
  useEffect(() => {
    const total = meals.reduce((sum, meal) => sum + meal.calories, 0)
    setTotalCalories(total)
  }, [meals])

  const fetchNutritionData = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/nutrition`, getAuthHeader())
      setMeals(response.data.meals)
      setDailyGoal(response.data.daily_goal)
    } catch (error) {
      console.error('Failed to fetch nutrition data:', error)
      setError('Деректерді жүктеу мүмкін болмады')
    } finally {
      setLoading(false)
    }
  }

  const updateMeal = async (id, field, value) => {
    const updatedMeals = meals.map(meal => 
      meal.id === id ? { ...meal, [field]: value } : meal
    )
    setMeals(updatedMeals)
    
    try {
      // If updating time, we need to format it for the API
      let time = null
      if (field === 'time' && value) {
        // Create a date object with today's date and the time value
        const today = new Date()
        const [hours, minutes] = value.split(':')
        today.setHours(hours)
        today.setMinutes(minutes)
        time = today.toISOString()
      }
      
      await axios.post(
        `${API_URL}/nutrition/update`, 
        { 
          meal_id: id, 
          [field]: field === 'time' ? time : value 
        }, 
        getAuthHeader()
      )
    } catch (error) {
      console.error('Failed to update meal:', error)
      setError('Тамақты жаңарту мүмкін болмады')
      // Revert to original data if API call fails
      fetchNutritionData()
    }
  }

  const resetNutrition = async () => {
    try {
      await axios.post(`${API_URL}/nutrition/reset`, {}, getAuthHeader())
      // Reset UI state
      const resetMeals = meals.map(meal => ({ ...meal, calories: 0, time: '' }))
      setMeals(resetMeals)
    } catch (error) {
      console.error('Failed to reset nutrition data:', error)
      setError('Деректерді қалпына келтіру мүмкін болмады')
    }
  }

  const getCalorieProgressPercentage = () => {
    return Math.min((totalCalories / dailyGoal) * 100, 100)
  }

  if (loading) {
    return <div className="loading">Жүктелуде...</div>
  }

  return (
    <div className="nutrition-page">
      <h1>Тамақтану Күнделігі</h1>

      {error && <div className="error-message">{error}</div>}

      <div className="calorie-goal">
        <h2>Күндізгі калория мақсаты: {dailyGoal} калория</h2>
        <div className="progress-bar">
          <div 
            className="progress" 
            style={{width: `${getCalorieProgressPercentage()}%`}}
          ></div>
        </div>
        <p>{totalCalories} / {dailyGoal} калория</p>
      </div>

      <div className="meal-tracker">
        {meals.map(meal => (
          <div key={meal.id} className="meal-entry">
            <h3>{meal.name}</h3>
            <div className="meal-inputs">
              <input 
                type="number" 
                placeholder="Калория" 
                value={meal.calories}
                onChange={(e) => updateMeal(meal.id, 'calories', Number(e.target.value))}
              />
              <input 
                type="time" 
                value={meal.time ? new Date(meal.time).toTimeString().slice(0, 5) : ''}
                onChange={(e) => updateMeal(meal.id, 'time', e.target.value)}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="nutrition-actions">
        <button 
          className="reset-button" 
          onClick={resetNutrition}
        >
          Күнделікті нөлдеу
        </button>
      </div>
    </div>
  )
}

export default NutritionPage