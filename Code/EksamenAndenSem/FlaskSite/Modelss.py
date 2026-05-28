from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

class Winner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(30), nullable=False)
    prize = db.Column(db.String(30), nullable=False)



