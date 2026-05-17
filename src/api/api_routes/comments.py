from flask import request, jsonify
from api.models import db, Game, Comment, User
from api.routes import api
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select


# GET /games/<id>/comments — Listar comentarios de un juego
@api.route('/games/<int:game_id>/comments', methods=['GET'])
def get_game_comments(game_id):
    game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"msg": "Game not found"}), 404
    comments = db.session.execute(
        select(Comment).where(Comment.game_id == game_id).order_by(Comment.created_at.desc())
    ).scalars().all()
    return jsonify([c.serialize() for c in comments]), 200


# POST /games/<id>/comments — Crear comentario en un juego
@api.route('/games/<int:game_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(game_id):
    current_user_id = get_jwt_identity()

    game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    body = request.get_json()
    if not body or not body.get("content", "").strip():
        return jsonify({"msg": "Content is required"}), 400

    comment = Comment(
        user_id=current_user_id,
        game_id=game_id,
        content=body["content"].strip()
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.serialize()), 201


# DELETE /comments/<id> — Eliminar comentario (solo el autor o admin)
@api.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return jsonify({"msg": "Comment not found"}), 404

    user = db.session.get(User, current_user_id)
    if comment.user_id != current_user_id and (not user or not user.is_admin):
        return jsonify({"msg": "Not authorized"}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"msg": "Comment deleted"}), 200
