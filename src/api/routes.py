"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Game, UserGameList, Favorite, Profile
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


# =============================================================================
#  7 .   A C T U A L I Z A R   J U E G O   E N   L I S T A   ( P U T   / u s e r / g a m e s / < i d > )
# =============================================================================
# El usuario actualiza el estado, rating o review de un juego en su lista.
# Requiere token. Body: { "status": "playing", "rating": 8, "review": "Great game!" }
@api.route('/user/games/<int:entry_id>', methods=['PUT'])
@jwt_required()
def handle_update_user_game(entry_id):
    user_id = get_jwt_identity()
    body = request.get_json()

    # Buscar la entrada asegurándonos que sea del usuario logueado
    entry = db.session.execute(
        select(UserGameList).where(
            UserGameList.id == entry_id,
            UserGameList.user_id == user_id
        )
    ).scalar_one_or_none()

    if entry is None:
        return jsonify({"msg": "Entry not found"}), 404

    # Actualizar solo los campos que vienen en el body
    if body.get("status"):
        entry.status = body["status"]
    if body.get("rating") is not None:
        entry.rating = body["rating"]
    if body.get("review") is not None:
        entry.review = body["review"]

    db.session.commit()
    return jsonify({"msg": "Entry updated", "entry": entry.serialize()}), 200


# =============================================================================
#  8 .   F A V O R I T O S   ( G E T   / f a v o r i t e s )
# =============================================================================
# Devuelve todos los favoritos del usuario logueado.
@api.route('/favorites', methods=['GET'])
@jwt_required()
def handle_get_favorites():
    user_id = get_jwt_identity()
    favorites = db.session.execute(
        select(Favorite).where(Favorite.user_id == user_id)
    ).scalars().all()

    return jsonify([fav.serialize() for fav in favorites]), 200


# =============================================================================
#  9 .   A G R E G A R   F A V O R I T O   ( P O S T   / f a v o r i t e s )
# =============================================================================
# Agrega un juego a favoritos del usuario.
# Body: { "game_id": 1 }
@api.route('/favorites', methods=['POST'])
@jwt_required()
def handle_add_favorite():
    user_id = get_jwt_identity()
    body = request.get_json()

    if body is None or "game_id" not in body:
        return jsonify({"msg": "game_id is required"}), 400

    game_id = body["game_id"]

    game = db.session.get(Game, game_id)
    if game is None:
        return jsonify({"msg": "Game not found"}), 404

    existing = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.game_id == game_id
        )
    ).scalar_one_or_none()
    if existing:
        return jsonify({"msg": "Game already in favorites"}), 400

    fav = Favorite(user_id=user_id, game_id=game_id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({"msg": "Favorite added", "favorite": fav.serialize()}), 201


# =============================================================================
#  10 .   E L I M I N A R   F A V O R I T O   ( D E L E T E   / f a v o r i t e s / < g a m e _ i d > )
# =============================================================================
# Saca un juego de favoritos.
@api.route('/favorites/<int:game_id>', methods=['DELETE'])
@jwt_required()
def handle_delete_favorite(game_id):
    user_id = get_jwt_identity()

    fav = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.game_id == game_id
        )
    ).scalar_one_or_none()

    if fav is None:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"msg": "Favorite removed"}), 200


# =============================================================================
#  11 .   V E R   P E R F I L   ( G E T   / p r o f i l e )
# =============================================================================
# Devuelve el perfil del usuario logueado.
# Si no tiene perfil, lo crea automáticamente con valores por defecto.
@api.route('/profile', methods=['GET'])
@jwt_required()
def handle_get_profile():
    user_id = get_jwt_identity()
    profile = db.session.get(Profile, user_id)

    # Si no existe perfil, lo creamos con valores por defecto
    if profile is None:
        profile = Profile(id=user_id)
        db.session.add(profile)
        db.session.commit()

    return jsonify(profile.serialize()), 200


# =============================================================================
#  12 .   A C T U A L I Z A R   P E R F I L   ( P U T   / p r o f i l e )
# =============================================================================
# Actualiza los campos del perfil.
# Body: { "description": "...", "avatar_url": "...", "redes": {...} }
@api.route('/profile', methods=['PUT'])
@jwt_required()
def handle_update_profile():
    user_id = get_jwt_identity()
    body = request.get_json()

    profile = db.session.get(Profile, user_id)
    if profile is None:
        return jsonify({"msg": "Profile not found"}), 404

    if body is None:
        return jsonify({"msg": "No data provided"}), 400

    if body.get("description") is not None:
        profile.description = body["description"]
    if body.get("avatar_url") is not None:
        profile.avatar_url = body["avatar_url"]
    if body.get("redes") is not None:
        profile.redes = body["redes"]

    db.session.commit()
    return jsonify({"msg": "Profile updated", "profile": profile.serialize()}), 200
