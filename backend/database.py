from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class WaterIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_intake = db.Column(db.Integer, default=0)
    daily_goal = db.Column(db.Integer, default=2000)
    last_reset_date = db.Column(db.DateTime)
    entries = db.relationship('WaterIntakeEntry', backref='water_intake', lazy=True)

class WaterIntakeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    water_intake_id = db.Column(db.Integer, db.ForeignKey('water_intake.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

class SleepRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_sleep_start = db.Column(db.DateTime)
    entries = db.relationship('SleepEntry', backref='sleep_record', lazy=True)

class SleepEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sleep_record_id = db.Column(db.Integer, db.ForeignKey('sleep_record.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

class NutritionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    daily_goal = db.Column(db.Integer, default=2000)
    meals = db.relationship('Meal', backref='nutrition_record', lazy=True)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nutrition_record_id = db.Column(db.Integer, db.ForeignKey('nutrition_record.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime)

class ProgressRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_weight = db.Column(db.Float, default=0)
    goal_weight = db.Column(db.Float, default=0)
    height = db.Column(db.Float, default=0)
    weight = db.Column(db.Float, default=0)
    entries = db.relationship('ProgressEntry', backref='progress_record', lazy=True)

class ProgressEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    progress_record_id = db.Column(db.Integer, db.ForeignKey('progress_record.id'), nullable=False)
    current_weight = db.Column(db.Float, nullable=False)
    goal_weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())