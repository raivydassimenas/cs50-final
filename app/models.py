from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    predictions = db.relationship("Prediction", backref="user", lazy=True)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(20), nullable=False)
    score1 = db.Column(db.Integer, nullable=False)
    team2 = db.Column(db.String(20), nullable=False)
    score2 = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    predictions = db.relationship("Prediction", backref="game", lazy=True)


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score1 = db.Column(db.Integer, nullable=False)
    score2 = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
