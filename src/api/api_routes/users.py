from flask import request, jsonify
from api.models import db, User, Profile, UserSurvey, AddGame, imgurl
from api.routes import api
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select

#CRUD users y profile, user survey, addgame(crear)

# GET /users — Lista todos los usuarios (solo admin)
@api.route("/users", methods=['GET'])
@jwt_required()
def get_users () :
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if not current_user or not current_user.is_admin:
        return jsonify({"msg":"Admin access required"}), 401
    
    users = db.session.execute(select(User)).scalars().all()
    return jsonify({"users":[user.serialize() for user in users]}), 200

#GET me - Ver mi informacion
@api.route('/users/get_me', methods=['GET'])
@jwt_required()
def get_me():
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if not current_user:
        return jsonify({"msg":"User not found"}), 404
    
    return jsonify({"user":current_user.serialize()}), 200
    
# GET /users/<id> — Ver perfil de un usuario
@api.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user =db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    return jsonify({"user":user.serialize()}), 200

# PUT /users/<id> — Editar datos del usuario (solo puede el propio usuario)
@api.route('/users/<int:user_id>', methods=['PUT']) 
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    if int(current_user_id) != user_id:
        return jsonify({"msg": "You can only edit your own account"}), 403
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    body = request.get_json()
    if not body:
        return jsonify({"msg":" No data provided"}), 400  
    
    if "username" in body:
        if len(body["username"].strip()) < 5:
            return jsonify({"msg":"Username must be at least 5 characters"}), 400
        existing = db.session.execute(
            select(User).where(User.username == body["username"], User.id !=user_id)
        ).scalar_one_or_none()
        if existing:
            return jsonify({"msg":"Username already taken"}), 400
        user.username = body["username"]
    if "email" in body:
        existing = db.session.execute(
            select(User).where(User.email == body["email"], User.id != user_id)
        ).scalar_one_or_none()
        if existing:
            return jsonify({"msg":"Email already in use"}), 400
        user.email = body["email"]   

    db.session.commit()  
    return jsonify({"msg":"User updated", "user": user.serialize()}), 200

# DELETE /users/<id> — Eliminar cuenta (solo el propio usuario o admin)
@api.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user =db.session.get(User, current_user_id)

    if int(current_user_id) !=user_id and not current_user.is_admin:
        return jsonify({"msg":"Not authorized"}), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted"}), 200

# GET /users/<id>/profile — Ver perfil
@api.route('/users/<int:user_id>/profile', methods=['GET']) 
@jwt_required()
def get_profile(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    if not user.profile:
        return jsonify({"msg":"Profile not found"}), 404
    return jsonify({"user":user.serialize()}), 200

# POST /users/<id>/profile — Crear perfil
@api.route('/users/<int:user_id>/profile', methods=['POST'])
@jwt_required()
def create_profile(user_id):
    current_user_id = get_jwt_identity()
    if int(current_user_id) != user_id:
        return jsonify({"msg":"Not authorized"}), 403
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 400
    if user.profile:
        return jsonify({"msg":"Profile already exists"}), 400
    
    body = request.get_json() or {}

    profile = Profile(
        user_id = user_id,
        description = body.get("description", "No description"),
        redes=body.get("redes", None),
        avatar_url=body.get("avatar_url", imgurl)
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify({"msg":"Profile created", "profile": profile.serialize()}), 201

# PUT /users/<id>/profile — Editar perfil
@api.route('/users/<int:user_id>/profile', methods=['PUT'])
@jwt_required()
def update_profile(user_id):
    current_user_id = get_jwt_identity()
    if int(current_user_id) !=user_id:
        return jsonify({"msg": "Not authorized"}), 403
    
    user = db.session.get(User, user_id)
    if not user or not user.profile:
        return jsonify({"msg":"User or profile not found"}), 404
    
    body = request.get_json()
    if not body:
        return jsonify({"msg":"No data provided"}), 400
    
    if "description" in body:
        user.profile.description = body["description"]
    if "redes" in body:
        user.profile.redes = body["redes"]
    if "avatar_url" in body:
        user.profile.avatar_url = body["avatar_url"]

    db.session.commit()
    return jsonify({"msg":"Profile updated", "profile": user.profile.serialize()}), 200

# GET /users/<id>/survey — Ver encuesta del usuario
@api.route('/users/survey', methods=['GET'])
@jwt_required()
def get_survey():
    current_user_id = get_jwt_identity()

    surveys = db.session.execute(
        select(UserSurvey).where(UserSurvey.user_id == current_user_id)
    ).scalars().all()

    return jsonify([s.serialize() for s in surveys]), 200

# POST /users/survey — Crear encuesta
@api.route('/users/survey', methods=['POST'])
@jwt_required()
def create_survey():
    current_user_id = get_jwt_identity()

    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400

    required = ["genres", "platforms", "play_style"]
    missing = [f for f in required if f not in body]
    if missing:
        return jsonify({"msg": f"Missing fields: {', '.join(missing)}"}), 400

    survey = UserSurvey(
        user_id=current_user_id,
        genres=body["genres"],
        platforms=body["platforms"],
        play_style=body["play_style"],
        favorite_themes=body.get("favorite_themes", []),
    )
    db.session.add(survey)
    db.session.commit()
    return jsonify({"msg":"Survey created", "survey": survey.serialize()}), 201

# POST /addgame — Usuario propone añadir un juego (pendiente de aprobación admin)
@api.route('/addgame', methods=['POST'])
@jwt_required()
def create_add_game():
    current_user_id = get_jwt_identity()

    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400
    required = ["game_id", "body"]
    for field in required:
        if field not in body:
            return jsonify({"msg":"Missing field: {field}"}), 400
        
    add_game = AddGame(
        user_id = current_user_id,
        game_id = body["game_id"],
        creator=body.get("creator", False),
        update=body.get("update", False),
        body=body["body"],
        status="pending"
    ) 
    db.session.add(add_game)
    db.session.commit()
    return jsonify({"msg":"Game submission created", "add_game":add_game.serialize()}),201   
        