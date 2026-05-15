from flask import jsonify, request
from api.models import db, Game, UserGameList, UserGLG
from api.routes import api
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select

# GET /favorites
@api.route('/favorite/change', methods=['PUT'])
@jwt_required()
def change_favorite():

    current_user_id = get_jwt_identity()

    body= request.get_json()
    game_id= body.get("game_id")
    if not game_id: 
        return jsonify({"msg": "game_id is a required field", "success": False}), 400
    
    game= db.session.get(Game, game_id)
    if not game:
        return jsonify({"msg": "game not found"}), 404
    
    user_game_list = db.session.execute(select(UserGameList).where(
        UserGameList.user_id == current_user_id
    )).scalar_one_or_none()

    if not user_game_list:
        return jsonify({"msg": "User game list not found", "success": False}), 404

    user_glg = db.session.execute(select(UserGLG).where(
        UserGLG.ugl_id == user_game_list.id,
        UserGLG.game_id == game_id
    )).scalar_one_or_none()

    if not user_glg:
        return jsonify({"msg": "Game is not in user list", "success": False}), 404
    
    user_glg.is_favorite = not user_glg.is_favorite
    db.session.commit()

    return jsonify({
        "msg": "Favorite updated", "success": True, "is_favorite": user_glg.is_favorite
    }), 200


    #buscar UserGameList que tenga el id del usuario
    #una vez encontrado, crear una variable usergl_id, la cual va aguardar el id del UserGameList encontrado
    #busco UserGLG que su usergl_id sea el mismo que el de la variable creada anteriormente Y que su game_id sea el mismo que el de la variable game_id
    #una vez encontrado UserGLG, le cambio la propiedad is_favorite a lo opuesto de lo que era antes !
    #guardar los cambios y return jsonify
