from flask import jsonify, request
from api.models import db, Game, User, UserGameList, UserGLG
from api.routes import api
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select


# PUT /favorite/change — Toggle favorito (auto-agrega a la lista si no está)
@api.route('/favorite/change', methods=['PUT'])
@jwt_required()
def change_favorite():

    current_user_id = get_jwt_identity()

    body = request.get_json()
    game_id = body.get("game_id") if body else None
    if not game_id:
        return jsonify({"msg": "game_id is a required field", "success": False}), 400

    game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"msg": "game not found"}), 404

    # Obtener o crear UserGameList
    user_game_list = db.session.execute(select(UserGameList).where(
        UserGameList.user_id == current_user_id
    )).scalar_one_or_none()

    if not user_game_list:
        user_game_list = UserGameList(user_id=current_user_id)
        db.session.add(user_game_list)
        db.session.flush()

    # Buscar si el juego ya está en UserGLG
    user_glg = db.session.execute(select(UserGLG).where(
        UserGLG.ugl_id == user_game_list.id,
        UserGLG.game_id == game_id
    )).scalar_one_or_none()

    if not user_glg:
        # Auto-agregar a la lista con status "want_to_play"
        user_glg = UserGLG(
            game_id=game_id,
            ugl_id=user_game_list.id,
            status="want_to_play",
            is_favorite=True
        )
        db.session.add(user_glg)
        db.session.commit()
        return jsonify({
            "msg": "Game added to list and favorited",
            "success": True,
            "is_favorite": True
        }), 200

    # Ya está en la lista → toggle favorite
    user_glg.is_favorite = not user_glg.is_favorite
    db.session.commit()

    return jsonify({
        "msg": "Favorite updated",
        "success": True,
        "is_favorite": user_glg.is_favorite
    }), 200


# GET /favorite/status/<game_id> — Saber si el usuario tiene el juego en favoritos
@api.route('/favorite/status/<int:game_id>', methods=['GET'])
@jwt_required()
def get_favorite_status(game_id):
    current_user_id = get_jwt_identity()

    user_game_list = db.session.execute(select(UserGameList).where(
        UserGameList.user_id == current_user_id
    )).scalar_one_or_none()

    if not user_game_list:
        return jsonify({"is_favorite": False}), 200

    user_glg = db.session.execute(select(UserGLG).where(
        UserGLG.ugl_id == user_game_list.id,
        UserGLG.game_id == game_id
    )).scalar_one_or_none()

    return jsonify({"is_favorite": user_glg.is_favorite if user_glg else False}), 200
