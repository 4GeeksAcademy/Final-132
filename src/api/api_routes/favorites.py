from api.routes import api
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Favorite, Game
from sqlalchemy import select


# ═══════════════════════════════════════════
# CRUD favorite
# ═══════════════════════════════════════════

#Read all favorites (del usuario logueado)
@api.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    favorites = db.session.execute(
        select(Favorite).where(Favorite.user_id == user_id)
    ).scalars().all()
    return jsonify([fav.serialize() for fav in favorites]), 200


#Read one favorite
@api.route('/favorites/<int:fav_id>', methods=['GET'])
@jwt_required()
def get_favorite(fav_id):
    user_id = get_jwt_identity()
    fav = db.session.execute(
        select(Favorite).where(Favorite.id == fav_id, Favorite.user_id == user_id)
    ).scalar_one_or_none()
    if not fav:
        return jsonify({"msg": "Favorite not found"}), 404
    return jsonify(fav.serialize()), 200


#Create a favorite (agregar juego a favoritos)
@api.route('/favorites', methods=['POST'])
@jwt_required()
def add_favorite():
    user_id = get_jwt_identity()
    body = request.get_json()

    if not body or "game_id" not in body:
        return jsonify({"msg": "game_id is required"}), 400

    game = db.session.get(Game, body["game_id"])
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    existing = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.game_id == body["game_id"]
        )
    ).scalar_one_or_none()
    if existing:
        return jsonify({"msg": "Game already in favorites"}), 400

    fav = Favorite(user_id=user_id, game_id=body["game_id"])
    db.session.add(fav)
    db.session.commit()

    return jsonify({"msg": "Favorite added", "favorite": fav.serialize()}), 201


#Delete a favorite
@api.route('/favorites/<int:fav_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite(fav_id):
    user_id = get_jwt_identity()
    fav = db.session.execute(
        select(Favorite).where(Favorite.id == fav_id, Favorite.user_id == user_id)
    ).scalar_one_or_none()

    if not fav:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"msg": "Favorite removed"}), 200
