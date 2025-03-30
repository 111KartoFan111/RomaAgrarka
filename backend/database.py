from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    # Relationships
    water_intake = db.relationship('WaterIntake', backref='user', uselist=False, cascade='all, delete-orphan')
    sleep_record = db.relationship('SleepRecord', backref='user', uselist=False, cascade='all, delete-orphan')
    nutrition_record = db.relationship('NutritionRecord', backref='user', uselist=False, cascade='all, delete-orphan')
    progress_record = db.relationship('ProgressRecord', backref='user', uselist=False, cascade='all, delete-orphan')

class WaterIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    daily_goal = db.Column(db.Integer, default=2000)  # in ml
    total_intake = db.Column(db.Integer, default=0)  # in ml
    last_reset_date = db.Column(db.DateTime, default=datetime.datetime.now)

    # Relationships
    entries = db.relationship('WaterIntakeEntry', backref='water_intake', cascade='all, delete-orphan')

class WaterIntakeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    water_intake_id = db.Column(db.Integer, db.ForeignKey('water_intake.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # in ml
    date = db.Column(db.DateTime, default=datetime.datetime.now)

class SleepRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_sleep_start = db.Column(db.DateTime, nullable=True)

    # Relationships
    entries = db.relationship('SleepEntry', backref='sleep_record', cascade='all, delete-orphan')

class SleepEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sleep_record_id = db.Column(db.Integer, db.ForeignKey('sleep_record.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

class NutritionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    daily_goal = db.Column(db.Integer, default=2000)  # in calories

    # Relationships
    meals = db.relationship('Meal', backref='nutrition_record', cascade='all, delete-orphan')

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nutrition_record_id = db.Column(db.Integer, db.ForeignKey('nutrition_record.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime, nullable=True)

class ProgressRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_weight = db.Column(db.Float, default=0)  # in kg
    goal_weight = db.Column(db.Float, default=0)  # in kg
    height = db.Column(db.Float, default=0)  # in cm
    weight = db.Column(db.Float, default=0)  # in kg (for BMI calculation)

    # Relationships
    entries = db.relationship('ProgressEntry', backref='progress_record', cascade='all, delete-orphan')

class ProgressEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    progress_record_id = db.Column(db.Integer, db.ForeignKey('progress_record.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    current_weight = db.Column(db.Float, nullable=False)  # in kg
    goal_weight = db.Column(db.Float, nullable=False)  # in kg