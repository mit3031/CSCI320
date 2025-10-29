from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint("home", __name__, url_prefix="/")

"""
Simple home route that renders the home page html
"""
@bp.route("/home", methods=["GET"])
@login_required
def index():
    return render_template("home/home.html", username=current_user.id)