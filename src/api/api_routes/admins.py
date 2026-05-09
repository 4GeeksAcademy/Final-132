from api.routes import api
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, User, Ban, AddGame
from sqlalchemy import select
from datetime import datetime, timezone


# ─── Helper: verificar que el usuario sea admin ───
def _requiere_admin():
    """Retorna (user, None) si es admin, o (None, response) si no"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user or not user.is_admin:
        return None, (jsonify({"msg": "Admin access required"}), 403)
    return user, None


# ═══════════════════════════════════════════
# CRUD ban y addgame(aceptar o rechazar)
# ═══════════════════════════════════════════

#-----------------------------------------------------------------------

#BAN

#Read all bans
@api.route('/admin/bans', methods=['GET'])
@jwt_required()
def get_bans():
    admin, error = _requiere_admin()
    if error:
        return error

    bans = db.session.execute(select(Ban)).scalars().all()
    return jsonify([b.serialize() for b in bans]), 200


#Read one ban
@api.route('/admin/bans/<int:ban_id>', methods=['GET'])
@jwt_required()
def get_ban(ban_id):
    admin, error = _requiere_admin()
    if error:
        return error

    ban = db.session.get(Ban, ban_id)
    if not ban:
        return jsonify({"msg": "Ban not found"}), 404
    return jsonify(ban.serialize()), 200


#Create a ban (banear usuario)
@api.route('/admin/bans', methods=['POST'])
@jwt_required()
def create_ban():
    admin, error = _requiere_admin()
    if error:
        return error

    body = request.get_json()
    if not body or "user_id" not in body or "reason" not in body:
        return jsonify({"msg": "user_id and reason are required"}), 400

    if len(body["reason"].strip()) < 1:
        return jsonify({"msg": "Reason cannot be empty"}), 400

    user = db.session.get(User, body["user_id"])
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.is_admin:
        return jsonify({"msg": "Cannot ban another admin"}), 400

    ban = Ban(
        user_id=body["user_id"],
        admin_id=admin.id,
        reason=body["reason"],
        ends=datetime.fromisoformat(body["ends"]).replace(tzinfo=timezone.utc) if body.get("ends") else None
    )
    db.session.add(ban)
    db.session.commit()

    return jsonify({"msg": "Ban created", "ban": ban.serialize()}), 201


#Update a ban (modificar razón o duración)
@api.route('/admin/bans/<int:ban_id>', methods=['PUT'])
@jwt_required()
def update_ban(ban_id):
    admin, error = _requiere_admin()
    if error:
        return error

    ban = db.session.get(Ban, ban_id)
    if not ban:
        return jsonify({"msg": "Ban not found"}), 404

    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400

    if "reason" in body:
        if len(body["reason"].strip()) < 1:
            return jsonify({"msg": "Reason cannot be empty"}), 400
        ban.reason = body["reason"]

    if "ends" in body:
        ban.ends = datetime.fromisoformat(body["ends"]).replace(tzinfo=timezone.utc) if body["ends"] else None

    db.session.commit()
    return jsonify({"msg": "Ban updated", "ban": ban.serialize()}), 200


#Delete a ban (levantar un ban)
@api.route('/admin/bans/<int:ban_id>', methods=['DELETE'])
@jwt_required()
def delete_ban(ban_id):
    admin, error = _requiere_admin()
    if error:
        return error

    ban = db.session.get(Ban, ban_id)
    if not ban:
        return jsonify({"msg": "Ban not found"}), 404

    db.session.delete(ban)
    db.session.commit()

    return jsonify({"msg": "Ban removed"}), 200


#-----------------------------------------------------------------------

#ADDGAME (aprobar o rechazar solicitudes)

#Read all addgame requests (ver todas las solicitudes)
@api.route('/admin/addgames', methods=['GET'])
@jwt_required()
def get_admin_addgames():
    admin, error = _requiere_admin()
    if error:
        return error

    addgames = db.session.execute(select(AddGame)).scalars().all()
    return jsonify([a.serialize() for a in addgames]), 200


#Read one addgame request
@api.route('/admin/addgames/<int:addgame_id>', methods=['GET'])
@jwt_required()
def get_admin_addgame(addgame_id):
    admin, error = _requiere_admin()
    if error:
        return error

    addgame = db.session.get(AddGame, addgame_id)
    if not addgame:
        return jsonify({"msg": "AddGame request not found"}), 404
    return jsonify(addgame.serialize()), 200


#Update an addgame request (aprobar o rechazar)
@api.route('/admin/addgames/<int:addgame_id>', methods=['PUT'])
@jwt_required()
def update_admin_addgame(addgame_id):
    admin, error = _requiere_admin()
    if error:
        return error

    addgame = db.session.get(AddGame, addgame_id)
    if not addgame:
        return jsonify({"msg": "AddGame request not found"}), 404

    body = request.get_json()
    if not body or "status" not in body:
        return jsonify({"msg": "status is required"}), 400

    valid_statuses = ["approved", "rejected", "pending"]
    if body["status"] not in valid_statuses:
        return jsonify({"msg": f"Invalid status. Valid: {', '.join(valid_statuses)}"}), 400

    addgame.status = body["status"]
    db.session.commit()

    return jsonify({"msg": f"AddGame request {body['status']}", "addgame": addgame.serialize()}), 200


#Delete an addgame request
@api.route('/admin/addgames/<int:addgame_id>', methods=['DELETE'])
@jwt_required()
def delete_admin_addgame(addgame_id):
    admin, error = _requiere_admin()
    if error:
        return error

    addgame = db.session.get(AddGame, addgame_id)
    if not addgame:
        return jsonify({"msg": "AddGame request not found"}), 404

    db.session.delete(addgame)
    db.session.commit()

    return jsonify({"msg": "AddGame request deleted"}), 200
