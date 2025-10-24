from flask import Blueprint, request, render_template
from .db import get_db
import psycopg

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # connect to the db somehow and create new (unique user)
        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                #curs.execute(
                #    "INSERT INTO your_user_table (username, password) VALUES (%s, %s)",
                #    (username, password) # Pass as a tuple!
                #)
                pass

            # db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            print(f"Error during operation: {e}")

        return username
    
    return render_template("auth/register.html")