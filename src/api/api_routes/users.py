from api.routes import api
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, User, Profile, UserSurvey, AddGame, Game
from sqlalchemy import select
from datetime import datetime, timezone


# ═══════════════════════════════════════════
# CRUD users y profile, user survey, addgame(crear)
# ═══════════════════════════════════════════

#-----------------------------------------------------------------------

#USERS

#Read all users
@api.route('/users', methods=['GET'])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return jsonify([u.serialize() for u in users]), 200


#Read one user
@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user.serialize()), 200


#-----------------------------------------------------------------------

#PROFILE

#Read my profile (del usuario logueado)
@api.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = db.session.get(Profile, user_id)

    # Si no existe perfil, lo crea automáticamente con valores por defecto
    if not profile:
        profile = Profile(id=user_id)
        db.session.add(profile)
        db.session.commit()

    return jsonify(profile.serialize()), 200


#Update my profile
@api.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    profile = db.session.get(Profile, user_id)

    if not profile:
        return jsonify({"msg": "Profile not found"}), 404

    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400

    if "description" in body:
        if len(body["description"].strip()) < 1:
            return jsonify({"msg": "Description cannot be empty"}), 400
        profile.description = body["description"]
    if "avatar_url" in body:
        if len(body["avatar_url"].strip()) < 1:
            return jsonify({"msg": "Avatar URL cannot be empty"}), 400
        profile.avatar_url = body["avatar_url"]
    if "redes" in body:
        if not isinstance(body["redes"], dict):
            return jsonify({"msg": "redes must be a JSON object"}), 400
        profile.redes = body["redes"]

    db.session.commit()
    return jsonify({"msg": "Profile updated", "profile": profile.serialize()}), 200


#-----------------------------------------------------------------------

#USER SURVEY

#Read all surveys (del usuario logueado)
@api.route('/user/surveys', methods=['GET'])
@jwt_required()
def get_user_surveys():
    user_id = get_jwt_identity()
    surveys = db.session.execute(
        select(UserSurvey).where(UserSurvey.user_id == user_id)
    ).scalars().all()
    return jsonify([s.serialize() for s in surveys]), 200


#Read one survey
@api.route('/user/surveys/<int:survey_id>', methods=['GET'])
@jwt_required()
def get_user_survey(survey_id):
    user_id = get_jwt_identity()
    survey = db.session.execute(
        select(UserSurvey).where(
            UserSurvey.id == survey_id,
            UserSurvey.user_id == user_id
        )
    ).scalar_one_or_none()
    if not survey:
        return jsonify({"msg": "Survey not found"}), 404
    return jsonify(survey.serialize()), 200


#Create a survey (completar encuesta sobre un juego)
@api.route('/user/surveys', methods=['POST'])
@jwt_required()
def create_survey():
    user_id = get_jwt_identity()
    body = request.get_json()

    required = ["game_id", "genres", "platforms", "play_style", "favorite_themes"]
    if not body or any(f not in body for f in required):
        return jsonify({"msg": f"Missing fields: {', '.join(required)}"}), 400

    # Validar que genres, platforms y favorite_themes sean listas
    for list_field in ["genres", "platforms", "favorite_themes"]:
        if not isinstance(body[list_field], list) or len(body[list_field]) == 0:
            return jsonify({"msg": f"{list_field} must be a non-empty list"}), 400

    # Validar play_style
    valid_styles = ["casual", "hardcore", "competitive"]
    if body["play_style"] not in valid_styles:
        return jsonify({"msg": f"play_style must be one of: {', '.join(valid_styles)}"}), 400

    game = db.session.get(Game, body["game_id"])
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    survey = UserSurvey(
        user_id=user_id,
        game_id=body["game_id"],
        genres=body["genres"],
        platforms=body["platforms"],
        play_style=body["play_style"],
        favorite_themes=body["favorite_themes"],
        completed_at=datetime.now(timezone.utc)
    )
    db.session.add(survey)
    db.session.commit()

    return jsonify({"msg": "Survey completed", "survey": survey.serialize()}), 201


#-----------------------------------------------------------------------

#ADDGAME (solicitar agregar un juego nuevo)

#Read all addgame requests (del usuario logueado)
@api.route('/user/addgames', methods=['GET'])
@jwt_required()
def get_user_addgames():
    user_id = get_jwt_identity()
    addgames = db.session.execute(
        select(AddGame).where(AddGame.user_id == user_id)
    ).scalars().all()
    return jsonify([a.serialize() for a in addgames]), 200


#Read one addgame request
@api.route('/user/addgames/<int:addgame_id>', methods=['GET'])
@jwt_required()
def get_user_addgame(addgame_id):
    user_id = get_jwt_identity()
    addgame = db.session.execute(
        select(AddGame).where(
            AddGame.id == addgame_id,
            AddGame.user_id == user_id
        )
    ).scalar_one_or_none()
    if not addgame:
        return jsonify({"msg": "AddGame request not found"}), 404
    return jsonify(addgame.serialize()), 200


#Create an addgame request (solicitar agregar un juego)
@api.route('/user/addgames', methods=['POST'])
@jwt_required()
def create_addgame():
    user_id = get_jwt_identity()
    body = request.get_json()

    if not body or "game_id" not in body or "body" not in body:
        return jsonify({"msg": "game_id and body are required"}), 400

    if not isinstance(body["body"], dict):
        return jsonify({"msg": "body field must be a JSON object"}), 400

    game = db.session.get(Game, body["game_id"])
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    addgame = AddGame(
        user_id=user_id,
        game_id=body["game_id"],
        creator=body.get("creator", False),
        update=body.get("update", False),
        body=body["body"]
    )
    db.session.add(addgame)
    db.session.commit()

    return jsonify({"msg": "AddGame request created", "addgame": addgame.serialize()}), 201
