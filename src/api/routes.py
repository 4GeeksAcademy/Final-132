"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Game
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app import bcrypt
from sqlalchemy import select




api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


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
        return jsonify({"msg": "No enviaste datos en el cuerpo"}), 400
    if "username" not in body or "password" not in body or "email" not in body:
        return jsonify({"msg": "Debes enviar email, username y password"}), 400
    
    username = body.get("username")
    password =body.get("password")
    email = body.get("email")

    # Revisamos si el usuario ya existe en la base de datos
    email_exists= db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    user_exists = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user_exists or email_exists:
        return jsonify({"msg": "The username or email already exists"}), 400
    
    #Hasheamos la contraseña para que sea segura
    password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(username = username,email=email, password = password_hashed)

    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Successfully created user", 
                    "user":user.serialize()}), 201

#Login

@api.route('/login', methods=['POST'])
def handle_login():
    body = request.get_json()
        
    if body is None or "username" not in body or "password" not in body:
        return jsonify({"msg": "Access data is missing"}), 400
    
    username = body.get("username")
    web_password = body.get("password")

    # Filtrar usuario por nombre
    query = select(User).where(User.username == username)
    user = db.session.execute(query).scalar_one_or_none()
    
    if user is None:
        return jsonify({"msg": "User not found"}), 401
    
    #Comparacion de la clave que llega con el HASH guardado
    is_valid = bcrypt.check_password_hash(user.password, web_password)

    if not is_valid:
        return jsonify({"msg": "password not valid"}), 401

    # Creamos la pulsera (Token) usando el ID del usuario
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"msg": "Successful login", "token":access_token, "user_id": user.id}), 200

# 3. Perfil propio(/me)
# Requiere token JWT en el header: Authorization: Bearer <token>
@api.route('/me', methods=['GET'])
@jwt_required()
def handle_me():
    user_id = get_get_jwt_identity()
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"msg": "User nor found"}), 404
    return jsonify(user.serialize()), 200

#4 Listar Juegos(/games)
# Devuelve todos los juegos de la base de datos.
# No requiere autenticación — cualquiera puede ver los juegos.
@api.route('/games', methods=['GET'])
def handle_games()
    query = select(Game)
    games = db.session.execute(query).scalars().all()

     # Convertimos cada objeto Game a JSON usando su método serialize()
    return jsonify([game.serialize() for game in games]), 200

#5 Detalles de juegos(/games/<id>)
# Devuelve un solo juego por su ID.
@api.route('/game/<int:game_id>', methods=['GET'])
def handle_game(game_id):
    # db.session.get() busca por primary key
    game = db.session.get(Game, game_id)

    if game is None:
        return jsonify({"msg": "Game not found"}), 404
    
    return jsonify(game.serialize()),200
