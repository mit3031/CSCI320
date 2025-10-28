import psycopg
import bcrypt
import datetime
import time

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from .models import User
from .db import get_db

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

bp = Blueprint("auth", __name__, url_prefix="/auth")

"""
This is a routing function for registering new users into the system. It takes in the fields for a user and inserts it into the database
using an SQL statement
"""
@bp.route("/register", methods=["GET", "POST"])
def register():
    print("Entered register route")
    if request.method == "POST":
        start = time.time()
        print("Starting register")
        print("Request method:", request.method)
        print("Form data:", request.form)
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        email = request.form['email'].strip()
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        curr_time = datetime.datetime.now() #changed it into a singular time

        #If statements follow the constraints for data
        if not username.isalnum() or len(username) > 20:
            flash("Invalid username. Must be alphanumeric and ≤ 20 characters.")
            return render_template("auth/register.html")

        if "\\" in password or len(password) > 20:
            flash("Invalid password. Must be ≤ 20 characters and no backslashes.")
            return render_template("auth/register.html")

        if "@" not in email or len(email) > 100:
            flash("Invalid email format. Must contain '@' and ≤ 100 characters.")
            return render_template("auth/register.html")

        if len(first_name) > 20 or len(last_name) > 20:
            flash("First and last names must each be ≤ 20 characters.")
            return render_template("auth/register.html")

        # expand the size of the password in the database. hashed passwords > 20 chars
        # secure_pw = hash_password(password)

        # connect to the db somehow and create new (unique user)
        db_conn = get_db()
        try:
            print("DB connection established:", db_conn)
            print("After DB connect:", time.time() - start)
            with db_conn.cursor() as curs:

                # Checks if username has already been taken within the database
                curs.execute('SELECT username FROM "user" WHERE username = %s', (username,))
                if curs.fetchone():
                    return "Username already exists. Please choose another one.", 400

                secure_pw = hash_password(password) #hashing the password
                print("After hashing:", time.time() - start)

                curs.execute( #inserts the values inputed into the field into the user table
                    '''
                    INSERT INTO "user" (username, password, email, first_name, last_name, last_login, date_created)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''',
                    (username, secure_pw, email, first_name, last_name, None, curr_time) #None represents the last_login since this is registration
                )
                print("After insert:", time.time() - start)
            # figure out login & sessions

            db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500

        flash("Registration successful! You can now log in.")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")

"""
This is a routing function for logging into the system. It takes in two fields, username and password, then checks the databasee if those exists.
If it does it updates last_login column and creates a session for the user. Redirects them to homepage
"""
@bp.route("/login", methods=["GET", "POST"])
def login():
    print("Entered login route")
    if request.method == "POST":
        print("Request method: POST")
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        print(f"Form data received: Username: {username}, Password length: {len(password)}")

        # Domain constraint checks again
        if not username.isalnum() or len(username) > 20:
            print("invalid username")
            flash("Invalid username. Must be alphanumeric and ≤ 20 characters.")
            return render_template("auth/login.html")

        if "\\" in password or len(password) > 20:
            print("invalid password")
            flash("Invalid password. Must be ≤ 20 characters and no backslashes.")
            return render_template("auth/login.html")

        db_conn = get_db()
        print("Database connection retrieved successfully")
        try:
            print("Attempting query for user")
            with db_conn.cursor() as curs: #getting and checking if username is in the user table database
                curs.execute(
                    'SELECT username, password FROM "user" WHERE username = %s',
                    (username,)
                )
                user_data = curs.fetchone()
                print(f"DB result: {user_data}") # Shows if the user exists or not

                if not user_data:
                    flash("Incorrect Username or Password")
                    return render_template("auth/login.html")

                db_username, db_password_hash = user_data

                # Verify  password
                if not verify_password(password, db_password_hash):
                    flash("Incorrect Username or Password")
                    return render_template("auth/login.html")

                # Update last_login 
                curr_time = datetime.datetime.now()
                curs.execute(
                    'UPDATE "user" SET last_login = %s WHERE username = %s',
                    (curr_time, username)
                )
                db_conn.commit()
                print("Creating user session") # Prints after a succeful login

                # Log user in  (This is where the session is created)
                user = User(username=db_username)
                login_user(user)

                print(f"User {db_username} successfully logged in.") # We did it
                flash("Login successful!")
                return username # this is a place holder for our theoretical homepage (shoudl redirect you to the homepage once it's made)

        except psycopg.Error as e:
            db_conn.rollback()
            print(f"Error during login: {e}")
            flash("An internal error occurred.")
            return render_template("auth/login.html")

    return render_template("auth/login.html")

"""
This is a routing function for logging out, and when called it will end the user session and redirect them back to the 
login page of the website.
"""
@bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.")
    return redirect(url_for("auth.login"))