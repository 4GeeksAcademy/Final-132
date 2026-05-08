"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

# ─── SEGURIDAD ───────────────────────────────────────────────────────────────
# Werkzeug ya viene instalado con Flask. No necesitamos flask-bcrypt.
# generate_password_hash  → hashea la contraseña (SHA256 + salt automático)
# check_password_hash     → compara contraseña contra el hash guardado
from werkzeug.security import generate_password_hash, check_password_hash

# ─── JWT (JSON Web Tokens) ────────────────────────────────────────────────────
# create_access_token  → genera un token de acceso (como una "pulsera" de disco)
# get_jwt_identity     → obtiene el ID del usuario desde el token (para rutas protegidas)
# jwt_required         → decorador que protege rutas (sin token válido → 401)
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

# select nos permite hacer consultas a la BD con SQLAlchemy
from sqlalchemy import select


# =============================================================================
#  B LU E P R I N T
# =============================================================================
# Un Blueprint es como un "mini-app" dentro de Flask.
# Agrupa rutas relacionadas (auth, juegos, perfil...).
# Después se registra en app.py con un prefijo: /api
# Así todas las rutas quedan como /api/signup, /api/login, etc.
api = Blueprint('api', __name__)

# CORS = Permite que el frontend (React en otro puerto) haga peticiones al backend
CORS(api)


# =============================================================================
#  R U T A   D E   P R U E B A
# =============================================================================
@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


# =============================================================================
#  1 .   R E G I S T R O   ( S i g n u p )
# =============================================================================
# El usuario crea su cuenta por primera vez.
# Espera: { "username": "...", "email": "...", "password": "..." }
@api.route('/signup', methods=['POST'])
def handle_signup():
    body = request.get_json()

    # ── Validación 1: ¿el body existe? ──────────────────────────────────────
    if body is None:
        return jsonify({"msg": "No enviaste datos en el cuerpo"}), 400
    # ── Validación 2: ¿tiene todos los campos obligatorios? ────────────────
    if "username" not in body or "password" not in body or "email" not in body:
        return jsonify({"msg": "Debes enviar email, username y password"}), 400

    username = body.get("username")
    password = body.get("password")
    email = body.get("email")

    # ── Validación 3: ¿ya existe ese usuario o email? ──────────────────────
    # scalar_one_or_none() devuelve el usuario si existe, o None si no.
    # Es más seguro que first() porque tira error si hay duplicados (nunca debería pasar porque tenemos unique, pero por las dudas).
    email_exists = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    user_exists = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user_exists or email_exists:
        return jsonify({"msg": "The username or email already exists"}), 400

    # ── Hash de contraseña ───────────────────────────────────────────────────
    # NUNCA guardamos la contraseña en texto plano. La hasheamos con werkzeug.
    # El hash incluye un salt automático, así que aunque dos usuarios tengan
    # la misma contraseña, los hashes serán diferentes.
    password_hashed = generate_password_hash(password)

    # ⚠️ OJO: el modelo User tiene el campo "password_hash", NO "password"
    # Si ponés password=... tira error porque ese campo no existe en la tabla.
    # También seteamos is_active=True para que el usuario pueda loguearse.
    user = User(username=username, email=email, password_hash=password_hashed, is_active=True)

    db.session.add(user)      # Agrega a la sesión de la BD (pendiente)
    db.session.commit()       # Guarda en la BD (ejecuta el INSERT)

    return jsonify({"msg": "Successfully created user", "user": user.serialize()}), 201


# =============================================================================
#  2 .   L O G I N
# =============================================================================
# El usuario inicia sesión.
# Espera: { "username": "...", "password": "..." }
# Devuelve: { "token": "...", "user_id": ... }
@api.route('/login', methods=['POST'])
def handle_login():
    body = request.get_json()

    if body is None or "username" not in body or "password" not in body:
        return jsonify({"msg": "Access data is missing"}), 400

    username = body.get("username")
    web_password = body.get("password")

    # ── Buscar usuario en la BD por username ────────────────────────────────
    query = select(User).where(User.username == username)
    user = db.session.execute(query).scalar_one_or_none()

    if user is None:
        # No decimos "usuario no encontrado" de forma específica para no dar
        # pistas sobre qué usuarios existen. Seguridad por oscuridad.
        return jsonify({"msg": "User not found"}), 401

    # ── Verificar contraseña ─────────────────────────────────────────────────
    # check_password_hash(hash_guardado, contraseña_que_llega)
    # Devuelve True si coincide, False si no.
    # ⚠️ OJO: el modelo guarda en "password_hash", NO en "password"
    if not check_password_hash(user.password_hash, web_password):
        return jsonify({"msg": "password not valid"}), 401

    # ── Generar token JWT ────────────────────────────────────────────────────
    # El token es como una pulsera de identificacion.
    # identity = lo que guardamos dentro del token (generalmente el user.id)
    # Con ese token, el frontend puede acceder a rutas protegidas.
    access_token = create_access_token(identity=str(user.id))

    return jsonify({"msg": "Successful login", "token": access_token, "user_id": user.id}), 200
