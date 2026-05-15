from flask import request, jsonify
from api.models import db, User, Ban, AddGame, Game
from api.routes import api
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select
from datetime import datetime

def admin_required():

    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)
    return current_user and current_user.is_admin

@api.route("/admin/addgames", methods=["GET"])
@jwt_required() 
def get_pending_addgames():

    if not admin_required():
        return jsonify({"msg": "Admin access required", "success": False}), 403
    
    submissions = db.session.execute(select(AddGame).where(
        AddGame.status == "pending")).scalars().all()

    return jsonify({"success": True, "submissions": [
        submission.serialize() for submission in submissions
    ]}), 200

@api.route("admins/addgames/<int:addgame_id>", methods=['PUT'])
@jwt_required()
def update_addgame_status(addgame_id):

    if not admin_required():
        return jsonify({"msg": "Admin access required", "success": False}), 403
    
    add_game = db.session.get(AddGame, addgame_id)

    if not add_game:
        return jsonify({"msg": "Submission not found", "success": False}), 404
    
    body = request.get_json()

    if not body or "status" not in body:
        return jsonify({"msg": "Status is required", "success": False}), 400
    
    if body["status"] not in ["approved", "rejected"]:
        return jsonify({"msg": "Invalid status", "success": False}), 400
    
    if add_game.status != "pending":
        return jsonify({"msg": "Submission already processed", "success": False}), 400
    
    add_game = body["status"]

    #Have to create a code for working only if aproved to add the game successfuly