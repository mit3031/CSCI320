import os
import psycopg
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
from flask import Flask
from .models import User
from flask_login import LoginManager

login_manager = LoginManager() #this had to be placed up here cause it needs to be defined 

@login_manager.user_loader #Some function thats needed to run login
def load_user(username):
    return User(username)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey123")

    load_dotenv()
    app.config.from_mapping(
        RIT_USERNAME=os.getenv("RIT_USERNAME"),
        RIT_PASSWORD=os.getenv("RIT_PASSWORD"),
        DB_NAME=os.getenv("DB_NAME"),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def hi():
        return "hi"
    
    from . import db
    from . import auth
    from . import song_search

    try:
        db.init_db(app)
    except RuntimeError as e:
        print(f"DB init failed: {e}")

    login_manager.init_app(app)
    print("Login manager initialized")

    app.register_blueprint(auth.bp)
    app.register_blueprint(song_search.bp)

    app.add_url_rule("/", endpoint="index")

    return app