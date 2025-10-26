import psycopg
import bcrypt
import datetime

from flask import Blueprint, request, render_template
from flask_login import login_user
from .db import get_db

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form['email']
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        curr_date = datetime.date.today().strftime("%Y-%m-%d")
        curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # expand the size of the password in the database. hashed passwords > 20 chars
        # secure_pw = hash_password(password)

        # connect to the db somehow and create new (unique user)
        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                curs.execute(
                    'INSERT INTO "user" (username, password, email, first_name, last_name, last_login, date_created) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (username, password, email, first_name, last_name, curr_date, curr_time)
                )

            # figure out login & sessions

            db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            print(f"Error during operation: {e}")

        return username
    
    return render_template("auth/register.html")