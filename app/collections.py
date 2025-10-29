from flask import Blueprint, redirect, render_template, request, jsonify, abort, url_for
from flask_login import login_required, current_user
from .dao import collection_dao as dao

bp = Blueprint("collections", __name__, url_prefix="/collections")

#check headers later
#Needs edit for total duration in minuites

@bp.route("/", methods=["GET", "POST"])
@login_required
def collections_home():
    collections = dao.view_collections(current_user.id)
    return render_template("collections/view.html", collections=collections)

@bp.route("/create", methods=["POST"])
@login_required
def create_collection():
    name = request.form['name'].strip()
    dao.create_collection(name, current_user.id)

    return redirect(url_for(".collections_home"))

@bp.get("/user/<username>")
@login_required
def view_collection_by_user(username):
    return jsonify(dao.view_collections(username)), 200

@bp.patch("/<int:cid>")
@login_required
def rename(cid):
    new_name = (request.get_json(force=True) or {}).get("name", "").strip()
    if not new_name: return {"error": "name required"}, 400
    updated = dao.rename_collection(cid, new_name)
    if not updated: abort(404)
    return jsonify(updated)

@bp.delete("/<int:cid>")
@login_required
def delete(cid):
    ok = dao.delete_collection(cid)
    if not ok: abort(404)
    return "", 204

