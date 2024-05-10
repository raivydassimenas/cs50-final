import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from app import config

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, config.SQLALCHEMY_DATABASE_URI)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = config.SECRET_KEY
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from app.models import User, Game, Prediction, Access

login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    db.create_all()
    db.session.commit()

from app import views, models

migrate = Migrate(app, db)

