from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, WaterIntake, WaterIntakeEntry, SleepRecord, SleepEntry, NutritionRecord, Meal, ProgressRecord, ProgressEntry
import datetime
import os

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:5173'])  # Укажите домен фронтенда

# Конфигурация
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-very-secret-jwt-key')  # Обязательно измените в продакшене
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=7)

# Инициализация расширений
jwt = JWTManager(app)
db.init_app(app)

# Создание таблиц базы данных
with app.app_context():
    db.create_all()

# Вспомогательная функция для инициализации записей пользователя
def initialize_user_records(user_id):
    water_intake = WaterIntake(user_id=user_id, daily_goal=2000)
    sleep_record = SleepRecord(user_id=user_id)
    nutrition_record = NutritionRecord(user_id=user_id, daily_goal=2000)
    progress_record = ProgressRecord(user_id=user_id)

    db.session.add_all([water_intake, sleep_record, nutrition_record, progress_record])
    db.session.flush()  # Assign IDs to the records

    meals = [
        Meal(name='Таңғы ас', calories=0, nutrition_record_id=nutrition_record.id),
        Meal(name='Түскі ас', calories=0, nutrition_record_id=nutrition_record.id),
        Meal(name='Кешкі ас', calories=0, nutrition_record_id=nutrition_record.id)
    ]

    db.session.add_all(meals)
    db.session.commit()

# Аутентификация
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 409

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already taken'}), 409

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password'])
    )

    db.session.add(new_user)
    db.session.commit()

    initialize_user_records(new_user.id)  # Убеждаемся, что функция вызывается

    access_token = create_access_token(identity=str(new_user.id))
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': {'id': new_user.id, 'username': new_user.username, 'email': new_user.email}
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Преобразуем user.id в строку
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logout successful'}), 200  # JWT не требует серверного логаута, это делается на клиенте

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    }), 200

# Water Tracker
@app.route('/api/water', methods=['GET'])
@jwt_required()
def get_water_intake():
    user_id = get_jwt_identity()
    water_intake = WaterIntake.query.filter_by(user_id=user_id).first()

    if not water_intake:
        return jsonify({'message': 'Water intake record not found'}), 404

    entries = [{'id': e.id, 'amount': e.amount, 'date': e.date.isoformat()} for e in water_intake.entries]
    return jsonify({
        'total_intake': water_intake.total_intake,
        'daily_goal': water_intake.daily_goal,
        'history': entries
    }), 200

@app.route('/api/water/add', methods=['POST'])
@jwt_required()
def add_water():
    user_id = get_jwt_identity()
    water_intake = WaterIntake.query.filter_by(user_id=user_id).first()

    if not water_intake:
        # Создаем запись, если она отсутствует
        water_intake = WaterIntake(user_id=user_id, daily_goal=2000)
        db.session.add(water_intake)
        db.session.commit()

    data = request.get_json()
    amount = data.get('amount', 0)
    new_entry = WaterIntakeEntry(water_intake_id=water_intake.id, amount=amount)
    water_intake.total_intake += amount

    db.session.add(new_entry)
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

    WaterIntakeEntry.query.filter_by(water_intake_id=water_intake.id).delete()
    water_intake.total_intake = 0
    water_intake.last_reset_date = datetime.datetime.now()

    db.session.commit()
    return jsonify({'message': 'Water intake reset successfully'}), 200

# Sleep Tracker
@app.route('/api/sleep', methods=['GET'])
@jwt_required()
def get_sleep_records():
    user_id = get_jwt_identity()
    sleep_record = SleepRecord.query.filter_by(user_id=user_id).first()

    if not sleep_record:
        return jsonify({'message': 'Sleep record not found'}), 404

    history = [
        {
            'id': e.id,
            'start': e.start_time.isoformat(),
            'end': e.end_time.isoformat(),
            'duration': str(e.end_time - e.start_time)
        } for e in sleep_record.entries
    ]

    current_sleep = sleep_record.current_sleep_start.isoformat() if sleep_record.current_sleep_start else None
    return jsonify({'current_sleep': current_sleep, 'history': history}), 200

@app.route('/api/sleep/start', methods=['POST'])
@jwt_required()
def start_sleep():
    user_id = get_jwt_identity()
    sleep_record = SleepRecord.query.filter_by(user_id=user_id).first()

    if not sleep_record:
        # Создаем запись, если она отсутствует
        sleep_record = SleepRecord(user_id=user_id)
        db.session.add(sleep_record)
        db.session.commit()

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
    new_entry = SleepEntry(
        sleep_record_id=sleep_record.id,
        start_time=sleep_record.current_sleep_start,
        end_time=end_time
    )
    sleep_record.current_sleep_start = None

    db.session.add(new_entry)
    db.session.commit()

    return jsonify({
        'message': 'Sleep tracking ended',
        'duration': str(end_time - new_entry.start_time)
    }), 200

@app.route('/api/sleep/reset', methods=['POST'])
@jwt_required()
def reset_sleep():
    user_id = get_jwt_identity()
    sleep_record = SleepRecord.query.filter_by(user_id=user_id).first()

    if not sleep_record:
        return jsonify({'message': 'Sleep record not found'}), 404

    SleepEntry.query.filter_by(sleep_record_id=sleep_record.id).delete()
    sleep_record.current_sleep_start = None

    db.session.commit()
    return jsonify({'message': 'Sleep history cleared successfully'}), 200

# Nutrition Tracker
@app.route('/api/nutrition', methods=['GET'])
@jwt_required()
def get_nutrition():
    user_id = get_jwt_identity()
    nutrition_record = NutritionRecord.query.filter_by(user_id=user_id).first()

    if not nutrition_record:
        return jsonify({'message': 'Nutrition record not found'}), 404

    meals = [
        {'id': m.id, 'name': m.name, 'calories': m.calories, 'time': m.time.isoformat() if m.time else None}
        for m in nutrition_record.meals
    ]
    return jsonify({'daily_goal': nutrition_record.daily_goal, 'meals': meals}), 200

@app.route('/api/nutrition/update', methods=['POST'])
@jwt_required()
def update_meal():
    user_id = int(get_jwt_identity())  # Convert string to integer
    data = request.get_json()
    meal = Meal.query.get(data['meal_id'])

    if not meal or meal.nutrition_record.user_id != user_id:
        nutrition_record = NutritionRecord.query.filter_by(user_id=user_id).first()
        if not nutrition_record:
            nutrition_record = NutritionRecord(user_id=user_id, daily_goal=2000)
            db.session.add(nutrition_record)
            db.session.commit()
        if not nutrition_record.meals:
            meals = [
                Meal(name='Таңғы ас', calories=0, nutrition_record_id=nutrition_record.id),
                Meal(name='Түскі ас', calories=0, nutrition_record_id=nutrition_record.id),
                Meal(name='Кешкі ас', calories=0, nutrition_record_id=nutrition_record.id)
            ]
            db.session.add_all(meals)
            db.session.commit()
            created_meals = [
                {'id': m.id, 'name': m.name, 'calories': m.calories, 'time': m.time.isoformat() if m.time else None}
                for m in meals
            ]
            return jsonify({
                'message': 'Meals created for existing nutrition record. Use a valid meal_id from the list.',
                'meals': created_meals
            }), 201
        return jsonify({'message': 'Meal not found'}), 404
    if 'calories' in data:
        meal.calories = data['calories']
    if 'time' in data and data['time']:
        meal.time = datetime.datetime.fromisoformat(data['time'])

    db.session.commit()
    return jsonify({
        'message': 'Meal updated successfully',
        'meal': {'id': meal.id, 'name': meal.name, 'calories': meal.calories, 'time': meal.time.isoformat() if meal.time else None}
    }), 200

@app.route('/api/nutrition/reset', methods=['POST'])
@jwt_required()
def reset_nutrition():
    user_id = get_jwt_identity()
    nutrition_record = NutritionRecord.query.filter_by(user_id=user_id).first()

    if not nutrition_record:
        return jsonify({'message': 'Nutrition record not found'}), 404

    for meal in nutrition_record.meals:
        meal.calories = 0
        meal.time = None

    db.session.commit()
    return jsonify({'message': 'Nutrition data reset successfully'}), 200

# Progress Tracker
@app.route('/api/progress', methods=['GET'])
@jwt_required()
def get_progress():
    user_id = get_jwt_identity()
    progress_record = ProgressRecord.query.filter_by(user_id=user_id).first()

    if not progress_record:
        return jsonify({'message': 'Progress record not found'}), 404

    history = [
        {'id': e.id, 'date': e.date.isoformat(), 'current_weight': e.current_weight, 'goal_weight': e.goal_weight}
        for e in progress_record.entries
    ]
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

    if 'current_weight' in data:
        progress_record.current_weight = data['current_weight']
    if 'goal_weight' in data:
        progress_record.goal_weight = data['goal_weight']
    if 'height' in data:
        progress_record.height = data['height']
    if 'weight' in data:
        progress_record.weight = data['weight']

    if progress_record.current_weight > 0 and progress_record.goal_weight > 0 and data.get('add_entry', False):
        new_entry = ProgressEntry(
            progress_record_id=progress_record.id,
            current_weight=progress_record.current_weight,
            goal_weight=progress_record.goal_weight
        )
        db.session.add(new_entry)

    db.session.commit()
    return jsonify({'message': 'Progress updated successfully'}), 200

@app.route('/api/progress/reset', methods=['POST'])
@jwt_required()
def reset_progress():
    user_id = get_jwt_identity()
    progress_record = ProgressRecord.query.filter_by(user_id=user_id).first()

    if not progress_record:
        return jsonify({'message': 'Progress record not found'}), 404

    ProgressEntry.query.filter_by(progress_record_id=progress_record.id).delete()
    progress_record.current_weight = 0
    progress_record.goal_weight = 0
    progress_record.height = 0
    progress_record.weight = 0

    db.session.commit()
    return jsonify({'message': 'Progress data cleared successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)