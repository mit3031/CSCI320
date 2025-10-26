import os
import psycopg
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
from flask import Flask
from flask_login import LoginManager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

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

    try:
        db.init_db(app)
    except RuntimeError as e:
        print(f"DB init failed: {e}")

    login_manager = LoginManager()
    login_manager.init_app(app)

    app.register_blueprint(auth.bp)

    app.add_url_rule("/", endpoint="index")

    return app