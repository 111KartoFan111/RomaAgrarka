from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from database import db, User, WaterIntake, WaterIntakeEntry, SleepRecord, NutritionRecord, Meal, ProgressRecord, SleepEntry, WaterIntakeEntry, ProgressEntry
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_app.db'  # Use SQLite for simplicity (change to PostgreSQL in production)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', '4a6f6b1e5b2a8e3d4c6f6a1b8e9d3c2f7e6d5a4c3b2a1d0e5f4c3b2a1d0e9f8')  # Change in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

# Initialize extensions
jwt = JWTManager(app)
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 409
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already taken'}), 409
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password'])
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Initialize default records for the user
    initialize_user_records(new_user.id)
    
    # Create access token
    access_token = create_access_token(identity=new_user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200

# Helper function to initialize user records
def initialize_user_records(user_id):
    # Create water intake record
    water_intake = WaterIntake(user_id=user_id, daily_goal=2000)
    db.session.add(water_intake)
    
    # Create sleep record
    sleep_record = SleepRecord(user_id=user_id)
    db.session.add(sleep_record)
    
    # Create nutrition record with default meals
    nutrition_record = NutritionRecord(user_id=user_id, daily_goal=2000)
    db.session.add(nutrition_record)
    
    # Add default meals
    meals = [
        Meal(name='Таңғы ас', calories=0, nutrition_record_id=nutrition_record.id),
        Meal(name='Түскі ас', calories=0, nutrition_record_id=nutrition_record.id),
        Meal(name='Кешкі ас', calories=0, nutrition_record_id=nutrition_record.id)
    ]
    db.session.add_all(meals)
    
    # Create progress record
    progress_record = ProgressRecord(user_id=user_id)
    db.session.add(progress_record)
    
    db.session.commit()

# Water Tracker routes
@app.route('/api/water', methods=['GET'])
@jwt_required()
def get_water_intake():
    user_id = get_jwt_identity()
    water_intake = WaterIntake.query.filter_by(user_id=user_id).first()
    
    if not water_intake:
        return jsonify({'message': 'Water intake record not found'}), 404
    
    entries = [
        {
            'id': entry.id,
            'amount': entry.amount,
            'date': entry.date.isoformat()
        } for entry in water_intake.entries
    ]
    
    return jsonify({
        'total_intake': water_intake.total_intake,
        'daily_goal': water_intake.daily_goal,
        'history': entries
    }), 200

@app.route('/api/water/add', methods=['POST'])
@jwt_required()
def add_water():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    water_intake = WaterIntake.query.filter_by(user_id=user_id).first()
    
    if not water_intake:
        return jsonify({'message': 'Water intake record not found'}), 404
    
    amount = data.get('amount', 0)
    
    # Add new entry
    new_entry = WaterIntakeEntry(
        water_intake_id=water_intake.id,
        amount=amount
    )
    db.session.add(new_entry)
    
    # Update total
    water_intake.total_intake += amount
    
    db.session.commit()
    
    return jsonify({
        'message': 'Water intake added successfully',
        'total_intake': water_intake.total_intake
    }), 201

@app.route('/api/water/reset', methods=['POST'])
@jwt_required()
def reset_water():
    user_id = get_jwt_identity()
    water_intake = WaterIntake.query.filter_by(user_id=user_id).first()
    
    if not water_intake:
        return jsonify({'message': 'Water intake record not found'}), 404
    
    # Clear entries or archive them as needed
    WaterIntakeEntry.query.filter_by(water_intake_id=water_intake.id).delete()
    
    # Reset total
    water_intake.total_intake = 0
    water_intake.last_reset_date = datetime.datetime.now()
    
    db.session.commit()
    
    return jsonify({'message': 'Water intake reset successfully'}), 200

# Sleep Tracker routes
@app.route('/api/sleep', methods=['GET'])
@jwt_required()
def get_sleep_records():
    user_id = get_jwt_identity()
    sleep_record = SleepRecord.query.filter_by(user_id=user_id).first()
    
    if not sleep_record:
        return jsonify({'message': 'Sleep record not found'}), 404
    
    history = []
    for entry in sleep_record.entries:
        duration_seconds = (entry.end_time - entry.start_time).total_seconds()
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        history.append({
            'id': entry.id,
            'start': entry.start_time.isoformat(),
            'end': entry.end_time.isoformat(),
            'duration': f"{hours} сағ {minutes} мин {seconds} сек"
        })
    
    current_sleep = None
    if sleep_record.current_sleep_start:
        current_sleep = sleep_record.current_sleep_start.isoformat()
    
    return jsonify({
        'current_sleep': current_sleep,
        'history': history
    }), 200

@app.route('/api/sleep/start', methods=['POST'])
@jwt_required()
def start_sleep():
    user_id = get_jwt_identity()
    sleep_record = SleepRecord.query.filter_by(user_id=user_id).first()
    
    if not sleep_record:
        return jsonify({'message': 'Sleep record not found'}), 404
    
    # Start sleep tracking
    sleep_record.current_sleep_start = datetime.datetime.now()
    db.session.commit()
    
    return jsonify({
        'message': 'Sleep tracking started',
        'start_time': sleep_record.current_sleep_start.isoformat()
    }), 200

@app.route('/api/sleep/end', methods=['POST'])
@jwt_required()
def end_sleep():
    user_id = get_jwt_identity()
    sleep_record = SleepRecord.query.filter_by(user_id=user_id).first()
    
    if not sleep_record or not sleep_record.current_sleep_start:
        return jsonify({'message': 'No active sleep tracking found'}), 404
    
    end_time = datetime.datetime.now()
    
    # Create new sleep entry
    new_entry = SleepEntry(
        sleep_record_id=sleep_record.id,
        start_time=sleep_record.current_sleep_start,
        end_time=end_time
    )
    db.session.add(new_entry)
    
    # Reset current sleep tracking
    sleep_record.current_sleep_start = None
    
    db.session.commit()
    
    # Calculate duration
    duration_seconds = (end_time - new_entry.start_time).total_seconds()
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)
    
    return jsonify({
        'message': 'Sleep tracking ended',
        'duration': f"{hours} сағ {minutes} мин {seconds} сек"
    }), 200

@app.route('/api/sleep/reset', methods=['POST'])
@jwt_required()
def reset_sleep():
    user_id = get_jwt_identity()
    sleep_record = SleepRecord.query.filter_by(user_id=user_id).first()
    
    if not sleep_record:
        return jsonify({'message': 'Sleep record not found'}), 404
    
    # Clear entries
    SleepEntry.query.filter_by(sleep_record_id=sleep_record.id).delete()
    
    # Reset current sleep tracking
    sleep_record.current_sleep_start = None
    
    db.session.commit()
    
    return jsonify({'message': 'Sleep history cleared successfully'}), 200

# Nutrition Tracker routes
@app.route('/api/nutrition', methods=['GET'])
@jwt_required()
def get_nutrition():
    user_id = get_jwt_identity()
    nutrition_record = NutritionRecord.query.filter_by(user_id=user_id).first()
    
    if not nutrition_record:
        return jsonify({'message': 'Nutrition record not found'}), 404
    
    meals = []
    for meal in nutrition_record.meals:
        meals.append({
            'id': meal.id,
            'name': meal.name,
            'calories': meal.calories,
            'time': meal.time.isoformat() if meal.time else None
        })
    
    return jsonify({
        'daily_goal': nutrition_record.daily_goal,
        'meals': meals
    }), 200

@app.route('/api/nutrition/update', methods=['POST'])
@jwt_required()
def update_meal():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    meal_id = data.get('meal_id')
    meal = Meal.query.get(meal_id)
    
    if not meal or meal.nutrition_record.user_id != user_id:
        return jsonify({'message': 'Meal not found'}), 404
    
    # Update meal
    if 'calories' in data:
        meal.calories = data['calories']
    
    if 'time' in data and data['time']:
        meal.time = datetime.datetime.fromisoformat(data['time'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Meal updated successfully',
        'meal': {
            'id': meal.id,
            'name': meal.name,
            'calories': meal.calories,
            'time': meal.time.isoformat() if meal.time else None
        }
    }), 200

@app.route('/api/nutrition/reset', methods=['POST'])
@jwt_required()
def reset_nutrition():
    user_id = get_jwt_identity()
    nutrition_record = NutritionRecord.query.filter_by(user_id=user_id).first()
    
    if not nutrition_record:
        return jsonify({'message': 'Nutrition record not found'}), 404
    
    # Reset meals
    for meal in nutrition_record.meals:
        meal.calories = 0
        meal.time = None
    
    db.session.commit()
    
    return jsonify({'message': 'Nutrition data reset successfully'}), 200

# Progress Tracker routes
@app.route('/api/progress', methods=['GET'])
@jwt_required()
def get_progress():
    user_id = get_jwt_identity()
    progress_record = ProgressRecord.query.filter_by(user_id=user_id).first()
    
    if not progress_record:
        return jsonify({'message': 'Progress record not found'}), 404
    
    history = []
    for entry in progress_record.entries:
        history.append({
            'id': entry.id,
            'date': entry.date.isoformat(),
            'current_weight': entry.current_weight,
            'goal_weight': entry.goal_weight
        })
    
    return jsonify({
        'current_weight': progress_record.current_weight,
        'goal_weight': progress_record.goal_weight,
        'height': progress_record.height,
        'weight': progress_record.weight,
        'history': history
    }), 200

@app.route('/api/progress/update', methods=['POST'])
@jwt_required()
def update_progress():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    progress_record = ProgressRecord.query.filter_by(user_id=user_id).first()
    
    if not progress_record:
        return jsonify({'message': 'Progress record not found'}), 404
    
    # Update progress record
    if 'current_weight' in data:
        progress_record.current_weight = data['current_weight']
    
    if 'goal_weight' in data:
        progress_record.goal_weight = data['goal_weight']
    
    if 'height' in data:
        progress_record.height = data['height']
    
    if 'weight' in data:
        progress_record.weight = data['weight']
    
    # Add entry to history if both current and goal weights are set
    if progress_record.current_weight > 0 and progress_record.goal_weight > 0 and data.get('add_entry', False):
        new_entry = ProgressEntry(
            progress_record_id=progress_record.id,
            current_weight=progress_record.current_weight,
            goal_weight=progress_record.goal_weight
        )
        db.session.add(new_entry)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Progress updated successfully'
    }), 200

@app.route('/api/progress/reset', methods=['POST'])
@jwt_required()
def reset_progress():
    user_id = get_jwt_identity()
    progress_record = ProgressRecord.query.filter_by(user_id=user_id).first()

    if not progress_record:
        return jsonify({'message': 'Progress record not found'}), 404

    # Clear entries
    ProgressEntry.query.filter_by(progress_record_id=progress_record.id).delete()

    # Reset values
    progress_record.current_weight = 0
    progress_record.goal_weight = 0
    progress_record.height = 0
    progress_record.weight = 0

    db.session.commit()

    return jsonify({'message': 'Progress data cleared successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)