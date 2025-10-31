from flask import Blueprint, redirect, render_template, request, jsonify, abort, url_for
from flask_login import login_required, current_user
from .dao import collection_dao as dao

bp = Blueprint("collections", __name__, url_prefix="/collections")

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
    tracks = dao.get_collection_tracks(current_user.id, cid)
    return render_template("collections/view.html", cid=cid, tracks=tracks)

@bp.route("/add-albums/<int:cid>", methods=["GET", "POST"])
@login_required
def add_albums_view(cid: int):
    if request.method == "POST":
        query = request.form['album'].strip()

        albums = dao.get_albums(query)
        return render_template('collections/modify.html', albums=albums, cid=cid)

    return render_template('collections/modify.html')

@bp.route("add-albums/<int:cid>/<int:aid>", methods=["POST"])
@login_required
def add_albums(cid: int, aid: int):
    dao.add_album_to_collection(cid, aid)

    return redirect(url_for('.view_collection', cid=cid))

@bp.route("/remove/<int:cid>/<int:song_id>", methods=["POST"])
@login_required
def delete_track_from_collection(cid: int, song_id):
    dao.remove_song_from_collection(cid, song_id)

    return redirect(url_for(".view_collection", cid=cid))

@bp.route("/add-to-collections/<int:song_id>", methods=["GET", "POST"])
@login_required
def add_track_view(song_id):
    collections = dao.view_collections(current_user.id)

    return render_template("search/add_to_collection.html", collections=collections, song_id=song_id)

@bp.route("/add/<int:cid>/<int:song_id>", methods=["POST"])
@login_required
def add_track_to_collection(cid: int, song_id: int):
    dao.add_song_to_collection(cid, song_id)
    return redirect(url_for("search.search_songs"))

@bp.route("/remove/album/<int:cid>/", methods=["POST"])
@login_required
def delete_album_from_collection(cid: int):
    album_name = request.form['delete-album-col'].strip()
    dao.remove_album_from_collection(cid, album_name)

    return redirect(url_for(".view_collection", cid=cid))

@bp.get("/user/<username>")
@login_required
def view_collection_by_user(username):
    return jsonify(dao.view_collections(username)), 200

@bp.route("/rename/<int:cid>", methods=["POST"])
@login_required
def rename_collection(cid):
    new_name = request.form['collection-rename'].strip()
    dao.rename_collection(cid, new_name)

    return redirect(url_for(".view_collection", cid=cid))

@bp.route("/delete/<int:cid>", methods=["POST"])
@login_required
def delete_collection(cid):
    dao.delete_collection(cid)

    return redirect(url_for(".collections_home"))

