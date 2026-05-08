"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Game, UserGameList
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import select


api = Blueprint('api', __name__)


CORS(api)



@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200



#  1 .REGISTRO( Signup )
# El usuario crea su cuenta por primera vez.

@api.route('/signup', methods=['POST'])
def handle_signup():
    body = request.get_json()

    # ── Validación 1: ¿el body existe?
    if body is None:
        return jsonify({"msg": "No enviaste datos en el cuerpo"}), 400
    # ── Validación 2: ¿tiene todos los campos obligatorios?
    if "username" not in body or "password" not in body or "email" not in body:
        return jsonify({"msg": "Debes enviar email, username y password"}), 400

    username = body.get("username")
    password = body.get("password")
    email = body.get("email")

    # ── Validación 3: ¿ya existe ese usuario o email?
    # scalar_one_or_none() devuelve el usuario si existe, o None si no.
    
    email_exists = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    user_exists = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user_exists or email_exists:
        return jsonify({"msg": "The username or email already exists"}), 400

    #Hasheamos la contraseña para que sea segura.
    password_hashed = generate_password_hash(password)


    user = User(username=username, email=email, password_hash=password_hashed, is_active=True)

    db.session.add(user)      
    db.session.commit()       

    return jsonify({"msg": "Successfully created user", "user": user.serialize()}), 201



#  2 .   L O G I N

@api.route('/login', methods=['POST'])
def handle_login():
    body = request.get_json()

    if body is None or "username" not in body or "password" not in body:
        return jsonify({"msg": "Access data is missing"}), 400

    username = body.get("username")
    web_password = body.get("password")

    # ── Buscar usuario en la BD por username
    query = select(User).where(User.username == username)
    user = db.session.execute(query).scalar_one_or_none()

    if user is None:
        return jsonify({"msg": "User not found"}), 401

    # ── Verificar contraseña

    if not check_password_hash(user.password_hash, web_password):
        return jsonify({"msg": "password not valid"}), 401

    # Creamos la pulsera (Token) usando el ID del usuario
    access_token = create_access_token(identity=str(user.id))

    return jsonify({"msg": "Successful login", "token": access_token, "user_id": user.id}), 200


#  3 .   P E R F I L   P R O P I O   ( / m e )
# Requiere token JWT en el header: Authorization: Bearer <token>
@api.route('/me', methods=['GET'])
@jwt_required()
def handle_me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(user.serialize()), 200


# =============================================================================
#  4 .   L I S T A R   J U E G O S   ( / g a m e s )
# =============================================================================
# Devuelve todos los juegos de la base de datos.
# No requiere autenticación — cualquiera puede ver los juegos.
@api.route('/games', methods=['GET'])
def handle_games():
    # select(Game) genera: SELECT * FROM game
    # scalars().all() ejecuta y devuelve todos los resultados como objetos Game
    query = select(Game)
    games = db.session.execute(query).scalars().all()

    # Convertimos cada objeto Game a JSON usando su método serialize()
    return jsonify([game.serialize() for game in games]), 200


# =============================================================================
#  5 .   D E T A L L E   D E   J U E G O   ( / g a m e s / < i d > )
# =============================================================================
# Devuelve un solo juego por su ID.
# Ej: GET /api/games/1 → devuelve el juego con id=1
@api.route('/games/<int:game_id>', methods=['GET'])
def handle_game(game_id):
    # db.session.get() busca por primary key (más rápido que hacer un select)
    game = db.session.get(Game, game_id)

    if game is None:
        return jsonify({"msg": "Game not found"}), 404

    return jsonify(game.serialize()), 200


# =============================================================================
#  6 .   A G R E G A R   J U E G O   A   L I S T A   ( P O S T   / u s e r / g a m e s )
# =============================================================================
# El usuario logueado agrega un juego a su lista personal.
# Requiere token. Body: { "game_id": 1, "status": "want_to_play", "rating": 0, "review": "" }
@api.route('/user/games', methods=['POST'])
@jwt_required()
def handle_add_user_game():
    user_id = get_jwt_identity()
    body = request.get_json()

    if body is None or "game_id" not in body:
        return jsonify({"msg": "game_id is required"}), 400

    game_id = body.get("game_id")
    status = body.get("status", "want_to_play")
    rating = body.get("rating", 0)
    review = body.get("review", "")

    # Verificar que el juego existe
    game = db.session.get(Game, game_id)
    if game is None:
        return jsonify({"msg": "Game not found"}), 404

    # Verificar que no lo tenga ya en su lista
    existing = db.session.execute(
        select(UserGameList).where(
            UserGameList.user_id == user_id,
            UserGameList.game_id == game_id
        )
    ).scalar_one_or_none()
    if existing:
        return jsonify({"msg": "Game already in your list"}), 400

    entry = UserGameList(
        user_id=user_id, game_id=game_id,
        status=status, rating=rating, review=review
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({"msg": "Game added to your list", "entry": entry.serialize()}), 201
