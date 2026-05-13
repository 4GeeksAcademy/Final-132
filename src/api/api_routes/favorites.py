from flask import jsonify
from api.models import db, Favorite, Game
from api.routes import api
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select

# GET /favorites
@api.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():

    current_user_id = get_jwt_identity() #Mirar si hay que eliminar

    favorites = db.session.execute(
        select(Favorite).where(Favorite.user_id == current_user_id)
    ).scalars().all()

    return jsonify([f.serialize() for f in favorites]), 200

# POST /favorites/<game_id>
@api.route('/favorites/<int:game_id>', methods=['POST'])
@jwt_required()
def add_favorite(game_id):

    current_user_id = get_jwt_identity()

    game = db.session.get(Game, game_id)

    if not game:
        return jsonify({"msg": "Game not found"}), 404
    
    existing = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == current_user_id,
            Favorite.game_id == game_id
        )
    ).scalar_one_or_none()

    if existing:
        return jsonify({"msg": "Already in favorites"}), 400
    
    favorite = Favorite(
        user_id=current_user_id,
        game_id=game_id
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({
        "msg": "Favorite added",
        "favorite": favorite.serialize()
    }), 201

# DELETE /favorites/<game_id>
@api.route('favorites/<int:game_id>', methods=['DELETE'])
@jwt_required()
def remve_favorite(game_id):

    current_user_id = get_jwt_identity()

    favorite = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == current_user_id,
            Favorite.game_id == game_id
        )
    ).scalar_one_or_none()

    if not favorite:
        return jsonify({"msg": "Favorite not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite removed"}), 200