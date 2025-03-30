from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from database import Database
from flask import session

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["*"], allow_headers=["Content-Type", "Authorization"])
app.config['SECRET_KEY'] = '4a6f6b1e5b2a8e3d4c6f6a1b8e9d3c2f7e6d5a4c3b2a1d0e5f4c3b2a1d0e9f8'

# Настройки безопасности сессии
app.config.update(
    SESSION_COOKIE_SECURE=False,  # True в продакшене
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized", "authenticated": False}), 401

db = Database()

class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = str(id)
        self.email = email
        self.name = name  # Добавляем имя

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, email, name FROM users WHERE id = ?', (user_id,))
    user = cur.fetchone()
    conn.close()
    return User(id=user['id'], email=user['email'], name=user['name']) if user else None

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = sqlite3.connect('petshop.db')
        g.db_conn.row_factory = sqlite3.Row
    return g.db_conn

@app.teardown_appcontext
def close_db_connection(exception):
    db_conn = g.pop('db_conn', None)
    if db_conn:
        db_conn.close()

# Регистрация
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Расширенная валидация
    if not data:
        return jsonify({"error": "Деректер жіберілмеді"}), 400
    
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"{field.capitalize()} міндетті өріс"}), 400
    
    # Валидация email
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({"error": "Дұрыс емес email форматы"}), 400
    
    # Валидация пароля
    if len(data['password']) < 6:
        return jsonify({"error": "Парольдің ұзындығы кемінде 6 таңба болуы керек"}), 400

    try:
        hashed_password = generate_password_hash(data['password'])
        user_id, message = db.register_user(
            name=data['name'],
            email=data['email'],
            password=hashed_password,
            phone=data.get('phone'),
            address=data.get('address')
        )

        if user_id:
            user = User(user_id, data['email'], data['name'])
            login_user(user, remember=True)
            return jsonify({
                "message": "Тіркелу сәтті өтті",
                "user_id": user_id
            }), 201
        
        return jsonify({"error": message}), 400

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({"error": "Тіркелу кезінде қате пайда болды"}), 500
# Вход
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email и пароль обязательны"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    # Извлекаем id, email и name из базы данных
    cur.execute('SELECT id, email, name, password FROM users WHERE email = ?', (data['email'],))
    user = cur.fetchone()
    
    if user and check_password_hash(user['password'], data['password']):
        # Передаем id, email и name в конструктор User
        login_user(User(user['id'], user['email'], user['name']), remember=True)
        conn.close()  # Закрываем соединение после использования
        return jsonify({"message": "Вход успешен"}), 200
    conn.close()  # Закрываем соединение в случае ошибки
    return jsonify({"error": "Неверный email или пароль"}), 401

# Выход
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    logout_user()  # Разлогинивает пользователя в Flask-Login
    return jsonify({"message": "Выход успешен"}), 200

# Получение текущего пользователя
@app.route('/api/current-user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }), 200  # Заменил 212 на 200, так как 212 не является стандартным кодом

# Новый endpoint для выбора питомца
@app.route('/api/select-pet', methods=['POST'])
@login_required
def select_pet():
    data = request.json
    if not data or 'pet_id' not in data:
        return jsonify({"error": "Pet ID is required"}), 400
    pet_id = data.get('pet_id')
    success = db.update_selected_pet(current_user.id, pet_id)
    
    if success:
        return jsonify({"message": "Selected pet updated successfully"}), 200
    return jsonify({"error": "Pet not found or doesn't belong to user"}), 404

# Проверка авторизации
@app.route('/api/check-auth', methods=['GET'])
@login_required  # Требуется авторизация
def check_auth():
    return jsonify({"authenticated": True}), 200

# Получение конкретного пользователя
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.get_user(user_id)
    return jsonify(user) if user else jsonify({"error": "User not found"}), 404


@app.route('/api/my-profile', methods=['GET'])
@login_required
def get_my_profile():
    user = db.get_user(current_user.id)
    return jsonify(user)


# Обновление информации пользователя
@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if current_user.id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    success = db.update_user(user_id, **data)
    return jsonify({"message": "User updated successfully"}) if success else jsonify({"error": "User not found"}), 404

# Удаление пользователя
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    success = db.delete_user(user_id)
    return jsonify({"message": "User deleted successfully"}) if success else jsonify({"error": "User not found"}), 404

# Endpoint для получения всех питомцев
@app.route('/api/pets', methods=['GET'])
def get_pets():
    pets = db.get_pets()
    return jsonify(pets)

# Endpoint для получения питомцев конкретного владельца
@app.route('/api/users/<int:user_id>/pets', methods=['GET'])
@login_required
def get_pets_by_owner(user_id):

    if str(current_user.id) != str(user_id):  # Приведение типов
        return jsonify({"error": "Unauthorized"}), 403

    pets = db.get_pets_by_owner(user_id)
    return jsonify(pets)

# Endpoint для получения конкретного питомца
@app.route('/api/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = db.get_pet(pet_id)
    if pet:
        return jsonify(pet)
    return jsonify({"error": "Pet not found"}), 404

# Endpoint для создания нового питомца
@app.route('/api/pets', methods=['POST'])
@login_required
def create_pet():
    data = request.json
    if not data or 'name' not in data or 'species' not in data:
        return jsonify({"error": "Name and species are required"}), 400

    # Устанавливаем owner_id из текущего пользователя
    data['owner_id'] = current_user.id

    pet_id = db.add_pet(
        owner_id=data.get('owner_id'),
        name=data.get('name'),
        species=data.get('species'),
        breed=data.get('breed'),
        age=data.get('age'),
        gender=data.get('gender'),
        medical_history=data.get('medical_history')
    )

    return jsonify({"id": pet_id, "message": "Pet created successfully"}), 201

# Endpoint для обновления питомца
@app.route('/api/pets/<int:pet_id>', methods=['PUT'])
@login_required
def update_pet(pet_id):
    # Проверяем, что питомец принадлежит текущему пользователю
    pet = db.get_pet(pet_id)
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    if pet['owner_id'] != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    success = db.update_pet(
        pet_id=pet_id,
        name=data.get('name'),
        species=data.get('species'),
        breed=data.get('breed'),
        age=data.get('age'),
        gender=data.get('gender'),
        medical_history=data.get('medical_history')
    )

    if success:
        return jsonify({"message": "Pet updated successfully"})
    return jsonify({"error": "Pet not found"}), 404

# Endpoint для удаления питомца
@app.route('/api/pets/<int:pet_id>', methods=['DELETE'])
@login_required
def delete_pet(pet_id):

    pet = db.get_pet(pet_id)
    if not pet:
        return jsonify({"error": "Pet not found"}), 404

    if int(pet['owner_id']) != int(current_user.id):
        return jsonify({"error": "Unauthorized"}), 403

    success = db.delete_pet(pet_id)
    if success:
        return jsonify({"message": "Pet deleted successfully"})
    return jsonify({"error": "Pet not found"}), 404

if __name__ == '__main__':
    app.run(host='localhost', port=5000)