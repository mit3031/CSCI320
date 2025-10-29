import psycopg
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .db import get_db

bp = Blueprint("profile", __name__, url_prefix="/profile")

"""
Displays the current users profile infomation
Renders the html page for profile viewing
"""
@bp.route("/", methods=["GET"])
@login_required
def view_profile():
    db = get_db()
    with db.cursor() as curs:
        # Get user info
        curs.execute(
            'SELECT username, email, first_name, last_name, date_created, last_login '
            'FROM "user" WHERE username = %s',
            (current_user.username,)
        )
        user = curs.fetchone()

        # Get users they follow
        curs.execute(
            '''
            SELECT u.username, u.first_name, u.last_name
            FROM "followuser" f
            JOIN "user" u ON f.followed_username = u.username
            WHERE f.follow_username = %s
            ORDER BY u.username ASC
            ''',
            (current_user.username,)
        )
        following = curs.fetchall()

    return render_template("profile/view.html", user=user, following=following)


"""
Searches for a user via email in the database
Directs you to the search.html page (this is where you will be able to follow other users)
"""
@bp.route("/search", methods=["GET", "POST"])
@login_required
def search_user():
    result = None
    if request.method == "POST":
        email = request.form["email"].strip().lower()

        db = get_db()
        with db.cursor() as curs:
            curs.execute(
                'SELECT username, first_name, last_name, email '
                'FROM "user" WHERE email = %s AND username != %s',
                (email, current_user.username)
            )
            result = curs.fetchone()

        if not result:
            flash("No user found with that email")
        else:
            flash("User found below:")

    return render_template("profile/search.html", result=result)


"""
Follows a user
Adds username to the followuser table [follower_username, followed_username]
@Param: Username of the user to be followed
"""
@bp.route("/follow/<username>", methods=["POST"])
@login_required
def follow_user(username):
    db = get_db()
    with db.cursor() as curs:
        try:
            # Prevent duplicates from entering table
            curs.execute(
                'SELECT * FROM "followuser" WHERE follow_username = %s AND followed_username = %s',
                (current_user.username, username)
            )
            if curs.fetchone():
                flash("You already follow this user")
                return redirect(url_for("profile.view_profile"))

            curs.execute(
                'INSERT INTO "followuser" (follow_username, followed_username) VALUES (%s, %s)',
                (current_user.username, username)
            )
            db.commit()
            flash(f"You are now following {username}.")
        except psycopg.Error as e:
            db.rollback()
            flash(f"Error following user: {e}")

    return redirect(url_for("profile.view_profile"))


"""
Unfollow a user
Deletes username from the followuser table
"""
@bp.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow_user(username):
    db = get_db()
    with db.cursor() as curs:
        try:
            curs.execute(
                'DELETE FROM "followuser" WHERE follow_username = %s AND followed_username = %s',
                (current_user.username, username)
            )
            db.commit()
            flash(f"You unfollowed {username}.")
        except psycopg.Error as e:
            db.rollback()
            flash(f"Error unfollowing user: {e}")

    return redirect(url_for("profile.view_profile"))