from api.routes import api
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Comment, Game
from sqlalchemy import select


# ═══════════════════════════════════════════
# CRUD(create,read one,read all,update,delete) commets
# ═══════════════════════════════════════════

#Read all comments (de un juego específico)
@api.route('/games/<int:game_id>/comments', methods=['GET'])
def get_game_comments(game_id):
    game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    comments = db.session.execute(
        select(Comment)
        .where(Comment.game_id == game_id)
        .order_by(Comment.created_at.desc())
    ).scalars().all()

    return jsonify([c.serialize() for c in comments]), 200


#Read one comment
@api.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return jsonify({"msg": "Comment not found"}), 404
    return jsonify(comment.serialize()), 200


#Create a comment
@api.route('/comments', methods=['POST'])
@jwt_required()
def create_comment():
    user_id = get_jwt_identity()
    body = request.get_json()

    if not body or "game_id" not in body or "content" not in body:
        return jsonify({"msg": "game_id and content are required"}), 400

    game = db.session.get(Game, body["game_id"])
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    # Si tiene parent_id, verificar que el comentario padre exista
    parent_id = body.get("parent_id")
    if parent_id is not None:
        parent = db.session.get(Comment, parent_id)
        if not parent:
            return jsonify({"msg": "Parent comment not found"}), 404

    comment = Comment(
        user_id=user_id,
        game_id=body["game_id"],
        content=body["content"],
        parent_id=parent_id
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({"msg": "Comment created", "comment": comment.serialize()}), 201


#Update a comment (solo el autor puede editar)
@api.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    user_id = get_jwt_identity()
    comment = db.session.get(Comment, comment_id)

    if not comment:
        return jsonify({"msg": "Comment not found"}), 404

    if comment.user_id != int(user_id):
        return jsonify({"msg": "You can only edit your own comments"}), 403

    body = request.get_json()
    if not body or "content" not in body:
        return jsonify({"msg": "content is required"}), 400

    comment.content = body["content"]
    db.session.commit()

    return jsonify({"msg": "Comment updated", "comment": comment.serialize()}), 200


#Delete a comment (solo el autor puede borrar)
@api.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    user_id = get_jwt_identity()
    comment = db.session.get(Comment, comment_id)

    if not comment:
        return jsonify({"msg": "Comment not found"}), 404

    if comment.user_id != int(user_id):
        return jsonify({"msg": "You can only delete your own comments"}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"msg": "Comment deleted"}), 200
