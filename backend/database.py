import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self, db_name="petshop.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Создает новое соединение с базой данных."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Создает таблицы, если они отсутствуют."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT UNIQUE,
            password TEXT,
            address TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            selected_pet_id INTEGER,
            FOREIGN KEY (selected_pet_id) REFERENCES pets(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            breed TEXT,
            age INTEGER,
            gender TEXT CHECK (gender IN ('male', 'female')),
            medical_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
        ''')

        conn.commit()
        conn.close()

    def register_user(self, name, email, password, phone=None, address=None, role='user'):
        """Регистрирует нового пользователя."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return None, "User with this email already exists"

        cursor.execute('''
        INSERT INTO users (name, email, password, phone, address, role)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, password, phone, address, role))

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id, "User registered successfully"

    def authenticate_user(self, email, password):
        """Аутентифицирует пользователя."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, name, email, password, phone, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        print(f"User found: {user is not None}")
        if user:
            password_valid = check_password_hash(user["password"], password)
            print(f"Password valid: {password_valid}")
            if password_valid:
                return dict(user)
        return None

    def get_user(self, user_id):
        """Возвращает пользователя по ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, name, phone, email, address, role, created_at FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        return dict(user) if user else None

    def update_user(self, user_id, name=None, phone=None, email=None, address=None, password=None):
        """Обновляет информацию о пользователе."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Сначала получаем текущие данные пользователя
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        current_user = cursor.fetchone()

        if not current_user:
            conn.close()
            return False

        # Подготавливаем данные для обновления
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if phone is not None:
            update_data['phone'] = phone
        if email is not None:
            update_data['email'] = email
        if address is not None:
            update_data['address'] = address
        if password is not None:
            update_data['password'] = generate_password_hash(password)

        # Если нет данных для обновления, просто возвращаем True
        if not update_data:
            conn.close()
            return True

        # Формируем SQL-запрос для обновления
        query_parts = []
        query_values = []
        for key, value in update_data.items():
            query_parts.append(f"{key} = ?")
            query_values.append(value)
        
        query_values.append(user_id)  # Добавляем user_id в список значений
        
        query = f"UPDATE users SET {', '.join(query_parts)} WHERE id = ?"
        
        cursor.execute(query, query_values)
        conn.commit()
        conn.close()
        return True

    def delete_user(self, user_id):
        """Удаляет пользователя и его питомцев."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Удаляем всех питомцев пользователя
        cursor.execute('DELETE FROM pets WHERE owner_id = ?', (user_id,))
        
        # Удаляем самого пользователя
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))

        conn.commit()
        conn.close()
        return True

    def add_pet(self, owner_id, name, species, breed=None, age=None, gender=None, medical_history=None):
        """Добавляет питомца в базу данных."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO pets (owner_id, name, species, breed, age, gender, medical_history)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (owner_id, name, species, breed, age, gender, medical_history))

        conn.commit()
        pet_id = cursor.lastrowid
        conn.close()
        return pet_id

    def get_pet(self, pet_id):
        """Возвращает данные питомца по ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM pets WHERE id = ?', (pet_id,))
        pet = cursor.fetchone()
        conn.close()

        return dict(pet) if pet else None

    def get_pets_by_owner(self, user_id):
        """Возвращает список питомцев по ID владельца."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM pets WHERE owner_id = ?', (user_id,))
        pets = cursor.fetchall()
        conn.close()

        return [dict(pet) for pet in pets]

    def get_pets(self):
        """Возвращает всех питомцев."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM pets')
        pets = cursor.fetchall()
        conn.close()

        return [dict(pet) for pet in pets]

    def update_pet(self, pet_id, name=None, species=None, breed=None, age=None, gender=None, medical_history=None):
        """Обновляет информацию о питомце."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Сначала получаем текущие данные питомца
        cursor.execute('SELECT * FROM pets WHERE id = ?', (pet_id,))
        current_pet = cursor.fetchone()

        if not current_pet:
            conn.close()
            return False

        # Подготавливаем данные для обновления
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if species is not None:
            update_data['species'] = species
        if breed is not None:
            update_data['breed'] = breed
        if age is not None:
            update_data['age'] = age
        if gender is not None:
            update_data['gender'] = gender
        if medical_history is not None:
            update_data['medical_history'] = medical_history

        # Если нет данных для обновления, просто возвращаем True
        if not update_data:
            conn.close()
            return True

        # Формируем SQL-запрос для обновления
        query_parts = []
        query_values = []
        for key, value in update_data.items():
            query_parts.append(f"{key} = ?")
            query_values.append(value)

        query_values.append(pet_id)  # Добавляем pet_id в список значений

        query = f"UPDATE pets SET {', '.join(query_parts)} WHERE id = ?"

        cursor.execute(query, query_values)
        conn.commit()
        conn.close()
        return True

    def delete_pet(self, pet_id):
        """Удаляет питомца по ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM pets WHERE id = ?', (pet_id,))

        conn.commit()
        conn.close()
        return True
    
    def update_selected_pet(self, user_id, pet_id):
        """Updates the user's currently selected pet."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # First verify the pet belongs to this user
        cursor.execute('SELECT id FROM pets WHERE id = ? AND owner_id = ?', (pet_id, user_id))
        pet = cursor.fetchone()
        
        if not pet:
            conn.close()
            return False
            
        cursor.execute('UPDATE users SET selected_pet_id = ? WHERE id = ?', (pet_id, user_id))
        conn.commit()
        conn.close()
        return True
        
    def get_user_with_selected_pet(self, user_id):
        """Returns user data along with their selected pet information."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.name, u.phone, u.email, u.address, u.role, u.created_at, u.selected_pet_id,
                p.id as pet_id, p.name as pet_name, p.species, p.breed, p.age, p.gender
            FROM users u
            LEFT JOIN pets p ON u.selected_pet_id = p.id
            WHERE u.id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
            
        user_data = dict(result)
        
        # If there's a selected pet, create a nested structure
        if user_data.get('pet_id'):
            user_data['selected_pet'] = {
                'id': user_data.pop('pet_id'),
                'name': user_data.pop('pet_name'),
                'species': user_data.pop('species'),
                'breed': user_data.pop('breed'),
                'age': user_data.pop('age'),
                'gender': user_data.pop('gender')
            }
        else:
            # Clean up null pet fields
            for field in ['pet_id', 'pet_name', 'species', 'breed', 'age', 'gender']:
                if field in user_data:
                    user_data.pop(field, None)
            user_data['selected_pet'] = None
            
        return user_data