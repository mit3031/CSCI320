from flask import Blueprint, request, jsonify, abort
from dao import collection_dao as dao

collections_bp = Blueprint("collections", __name__)

#Needs edit for total duration in minuites
@collections_bp.post("/")
def create():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    creator = data.get("creator_username", "").strip()
    if not name or not creator:
        return {"error": "name and creator_username required"}, 400
    return jsonify(dao.create_collection(name, creator)), 201

