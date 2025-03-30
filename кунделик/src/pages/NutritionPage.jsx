import React, { useState, useEffect } from 'react'
import '../styles/NutritionPage.css'

function NutritionPage() {
  const [meals, setMeals] = useState([
    { id: 1, name: 'Таңғы ас', calories: 0, time: '' },
    { id: 2, name: 'Түскі ас', calories: 0, time: '' },
    { id: 3, name: 'Кешкі ас', calories: 0, time: '' }
  ])

  const [totalCalories, setTotalCalories] = useState(0)
  const [dailyGoal, setDailyGoal] = useState(2000)

  useEffect(() => {
    const savedMeals = JSON.parse(localStorage.getItem('nutritionMeals'))
    const savedGoal = localStorage.getItem('dailyCalorieGoal')

    if (savedMeals) setMeals(savedMeals)
    if (savedGoal) setDailyGoal(Number(savedGoal))
  }, [])

  useEffect(() => {
    localStorage.setItem('nutritionMeals', JSON.stringify(meals))
    localStorage.setItem('dailyCalorieGoal', dailyGoal)

    const total = meals.reduce((sum, meal) => sum + meal.calories, 0)
    setTotalCalories(total)
  }, [meals, dailyGoal])

  const updateMeal = (id, field, value) => {
    const updatedMeals = meals.map(meal => 
      meal.id === id ? { ...meal, [field]: value } : meal
    )
    setMeals(updatedMeals)
  }

  const resetNutrition = () => {
    const resetMeals = meals.map(meal => ({ ...meal, calories: 0, time: '' }))
    setMeals(resetMeals)
  }

  const getCalorieProgressPercentage = () => {
    return Math.min((totalCalories / dailyGoal) * 100, 100)
  }

  return (
    <div className="nutrition-page">
      <h1>Тамақтану Күнделігі</h1>

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
                value={meal.time}
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