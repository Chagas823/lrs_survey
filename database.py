from flask import Flask
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/lrs'  # ou outro banco de dados
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    return app

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/lrs'  # Ou outro banco de dados
    SQLALCHEMY_TRACK_MODIFICATIONS = False