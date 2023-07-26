import configparser
import os

from flask import Flask
from flask_login import LoginManager
from flask_minify import Minify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "secret key"

DB_FLAG = 0

if DB_FLAG == 0:
    # Use SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"
elif DB_FLAG == 1:
    # Use MySQL
    config = configparser.ConfigParser()
    config.read("config.ini")
    uri = "mysql://{}:{}@{}:{}/{}"
    uri = uri.format(*config["mysql"].values())
    app.config["SQLALCHEMY_DATABASE_URI"] = uri

Minify(app=app, html=True, js=True)
db = SQLAlchemy(app)
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"

from msgs import routes
from msgs import models

with app.app_context():
    db.create_all()
