from flask import Blueprint, redirect, render_template, request, jsonify, abort, url_for
from flask_login import login_required, current_user
from .dao import collection_dao as dao

bp = Blueprint("collections", __name__, url_prefix="/collections")

#check headers later
#Needs edit for total duration in minuites

@bp.route("/", methods=["GET"])
@login_required
def collections_home():
    collections = dao.view_collections(current_user.id)
    infos = [dao.get_collection_info(playlist['collection_id']) for playlist in collections]
    print(infos)

    for i in range(len(collections)):
        collections[i]['info'] = list(infos[i])
        if collections[i]['info'][1] == None:
            collections[i]['info'][1] = 0 

    print(collections)
    return render_template("collections/collections.html", collections=collections)

@bp.route("/create", methods=["POST"])
@login_required
def create_collection():
    name = request.form['name'].strip()
    dao.create_collection(name, current_user.id)

    return redirect(url_for(".collections_home"))

@bp.route("/<int:cid>", methods=["GET", "POST"])
@login_required
def view_collection(cid):
    tracks = dao.get_collection_tracks(cid)
    return render_template("collections/view.html", tracks=tracks)

@bp.get("/user/<username>")
@login_required
def view_collection_by_user(username):
    return jsonify(dao.view_collections(username)), 200

@bp.route("/rename/<int:cid>", methods=["POST"])
@login_required
def rename_collection(cid):
    new_name = (request.get_json(force=True) or {}).get("name", "").strip()
    if not new_name: return {"error": "name required"}, 400
    updated = dao.rename_collection(cid, new_name)
    if not updated: abort(404)
    return jsonify(updated)

@bp.route("/delete/<int:cid>", methods=["POST"])
@login_required
def delete_collection(cid):
    ok = dao.delete_collection(cid)
    return redirect(url_for(".collections_home"))

