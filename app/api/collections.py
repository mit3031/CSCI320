from flask import Blueprint, request, jsonify, abort
from dao import collection_dao as dao

collections_bp = Blueprint("collections", __name__)

#check headers later
#Needs edit for total duration in minuites

@collections_bp.post("/")
def create():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    creator = data.get("creator_username", "").strip()
    if not name or not creator:
        return {"error": "name and creator_username required"}, 400
    return jsonify(dao.create_collection(name, creator)), 201

@collections_bp.get("/user/<username>")
def view_collection_by_user(username):
    return jsonify(dao.view_collections(username)), 200

@collections_bp.delete("/<int:cid>")
def delete(cid):
    ok = dao.delete_collection(cid)
    if not ok: abort(404)
    return "", 204

