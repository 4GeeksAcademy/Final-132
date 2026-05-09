"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
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
    
    username_empty = len(username.strip()) < 5
    email_empty = len(email.strip()) < 5
    password_empty = len(password.strip()) < 5
    if username_empty or email_empty or password_empty:
        return jsonify({"msg": "Username, email and password must be at least five characters"}), 400

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

    db.session.add(user)
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

    username_empty = len(username.strip()) < 5
    password_empty = len(web_password.strip()) < 5
    if username_empty or password_empty:
        return jsonify({"msg": "Username, email and password must be at least five characters"}), 400

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


# # 4 Listar Juegos(/games)
# # Devuelve todos los juegos de la base de datos.
# # No requiere autenticación — cualquiera puede ver los juegos.


# @api.route('/games', methods=['GET'])
# def handle_games():
#     query = select(Game)
#     games = db.session.execute(query).scalars().all()

#     # Convertimos cada objeto Game a JSON usando su método serialize()
#     return jsonify([game.serialize() for game in games]), 200

# # 5 Detalles de juegos(/games/<id>)
# # Devuelve un solo juego por su ID.


# @api.route('/game/<int:game_id>', methods=['GET'])
# def handle_game(game_id):
#     # db.session.get() busca por primary key
#     game = db.session.get(Game, game_id)

#     if game is None:
#         return jsonify({"msg": "Game not found"}), 404

#     return jsonify(game.serialize()), 200

# # 6 Agregar Juegos a Lista (Post / user/ games)
# # El usuario logueado agrega un juego a su lista personal.


# @api.route('/user/game', methods=['POST'])
# @jwt_required()
# def handle_add_user_game():
#     user_id = get_jwt_identity()
#     body = request.get_json()

#     if body is None or "game_id" not in body:
#         return jsonify({"msg": "Game_id is requiered"})

#     game_id = body.get("game_id")
#     status = body.get("status", "want_to_play")
#     rating = body.get("rating", 0)
#     review = body.get("review", "")
# # Verificar que el juego existe
#     game = db.session.get(Game, game_id)
#     if game is None:
#         return jsonify({"msg": "Game no found"}), 404
# # Verificamos que no lo tenga ya en su lista
#     existing = db.session.execute(
#         select(UserGameList).where(UserGameList.user_id == user_id,
#                                    UserGameList.game_id == game_id)
#     ).scalar_one_or_none()
#     if existing:
#         return jsonify({"msg": "GAme already in your list"}), 400
#     entry = UserGameList(
#         user_id=user_id, game_id=game_id,
#         status=status, rating=rating, review=review
#     )
#     db.session.add(entry)
#     db.session.commit()

#     return jsonify({"msg": "Game added to your list", "entry": entry.serialize()}), 201
