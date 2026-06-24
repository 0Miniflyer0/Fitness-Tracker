from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    workouts = db.relationship('Workout', backref='user', lazy=True)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # example "Leg Day" lol
    date = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercises = db.relationship('Exercise', backref='workout', lazy=True)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exercise_type = db.Column(db.String(20), nullable=False, default='strength')
    # Fields for strength exercises
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    # Fields for cardio exercises
    duration = db.Column(db.Float, nullable=True)   # minutes
    distance = db.Column(db.Float, nullable=True)   # miles
    calories = db.Column(db.Float, nullable=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)