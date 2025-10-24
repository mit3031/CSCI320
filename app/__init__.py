import os
import psycopg
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    load_dotenv()
    app.config.from_mapping(
        RIT_USERNAME=os.getenv("RIT_USERNAME"),
        RIT_PASSWORD=os.getenv("RIT_PASSWORD"),
        DB_NAME=os.getenv("DB_NAME"),
        SECRET_KEY=os.getenv("SECRET_KEY", "a_default_secret_key_for_dev")
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

    app.register_blueprint(auth.bp)

    app.add_url_rule("/", endpoint="index")

    return app