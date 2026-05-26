"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Profile, UserGameList, imgurl
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from extensions import bcrypt
from sqlalchemy import select


api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)

from api.api_routes.admins import *
from api.api_routes.comments import *
from api.api_routes.favorites import *
from api.api_routes.games import *
from api.api_routes.users import *




@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

# 1. RUTA DE REGISTRO (Signup)
# el usuario crea su cuenta por primera vez


@api.route('/signup', methods=['POST'])
def handle_signup():
    body = request.get_json()

# Verificamos que nos hayan enviado los datos
    if body is None:
        return jsonify({"msg": "No data was sent in the request body"}), 400
    if "username" not in body or "password" not in body or "email" not in body:
        return jsonify({"msg": "You must provide email, username and password"}), 400

    username = body.get("username")
    email = body.get("email")
    password = body.get("password")

    # Validar vacío + mínimo de caracteres
    for field_name, field_val in [("Username", username), ("Email", email), ("Password", password)]:
        if not field_val.strip():
            return jsonify({"msg": f"{field_name} cannot be empty"}), 400
        if len(field_val.strip()) < 5:
            return jsonify({"msg": f"{field_name} must be at least 5 characters"}), 400

    # Revisamos si el usuario ya existe en la base de datos
    email_exists = db.session.execute(select(User).where(
        User.email == email)).scalar_one_or_none()
    user_exists = db.session.execute(select(User).where(
        User.username == username)).scalar_one_or_none()
    if user_exists or email_exists:
        return jsonify({"msg": "The username or email already exists"}), 400

    # Hasheamos la contraseña para que sea segura
    password_hash= bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(username=username, email=email, password_hash=password_hash)
    #Cuano se crea el  usuario, se debe de crear profile y user game list aun que esten vacios
    db.session.add(user)
    db.session.flush()  # ← necesario para obtener user.id antes del commit

    #crear profile vacio al crear user
    profile= Profile(
        user_id=user.id,
        description="No description",
        avatar_url=imgurl
    )

    #crear gamelist vacia al crear user
    game_list = UserGameList(user_id=user.id)
    db.session.add(profile)
    db.session.add(game_list)
    db.session.commit()
    return jsonify({"msg": "Successfully created user",
                    "user": user.serialize()}), 201

# Login

@api.route('/login', methods=['POST'])
def handle_login():
    body = request.get_json()

    if body is None or "username" not in body or "password" not in body:
        return jsonify({"msg": "Access data is missing, username and password are required fields"}), 400

    username = body.get("username")
    web_password = body.get("password")

    # Validar vacío + mínimo de caracteres
    for field_name, field_val in [("Username", username), ("Password", web_password)]:
        if not field_val.strip():
            return jsonify({"msg": f"{field_name} cannot be empty"}), 400
        if len(field_val.strip()) < 5:
            return jsonify({"msg": f"{field_name} must be at least 5 characters"}), 400

    # Filtrar usuario por nombre
    query = select(User).where(User.username == username)
    user = db.session.execute(query).scalar_one_or_none()

    if user is None:
        return jsonify({"msg": "User not found"}), 401

    # Comparacion de la clave que llega con el HASH guardado
    is_valid = bcrypt.check_password_hash(user.password_hash, web_password)

    if not is_valid:
        return jsonify({"msg": "password not valid"}), 401

    # Creamos la pulsera (Token) usando el ID del usuario
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"msg": "Successful login", "token": access_token, "user_id": user.id}), 200

# 3. Private: validar acceso
@api.route('/private', methods=['GET'])
@jwt_required()
def handle_private():
    #extraemos el ID del dueño del token
    current_user_id = get_jwt_identity()

    #Obtener por ID
    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({"msg": "User not found","success":False}), 404
    return jsonify({"msg":"User authenticated successfully", "success":True, "user_id":user.id}), 200

