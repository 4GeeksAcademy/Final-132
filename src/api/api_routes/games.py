from api.routes import api
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Game, GameTier, UserGameTier, UserGameList
from sqlalchemy import select
from datetime import datetime, timezone


# ─── Helper: calcular tier desde average rating ───
def _calcular_tier(avg):
    """Convierte promedio (1-5) a tier: S/A/B/C/D/F"""
    if avg is None:
        return "Undefined"
    if avg >= 4.5:
        return "S"
    if avg >= 3.5:
        return "A"
    if avg >= 2.5:
        return "B"
    if avg >= 1.5:
        return "C"
    if avg >= 0.5:
        return "D"
    return "F"


def _recalcular_game_tier(game_tier):
    """Recalcula average_rating y tier desde todos los votos de usuarios"""
    votes = db.session.execute(
        select(UserGameTier).where(UserGameTier.game_tier_id == game_tier.id)
    ).scalars().all()

    if not votes:
        game_tier.average_rating = 0.0
        game_tier.tier = "Undefined"
    else:
        total = sum(v.rating for v in votes)
        game_tier.average_rating = round(total / len(votes), 2)
        game_tier.tier = _calcular_tier(game_tier.average_rating)

    game_tier.updated_at = datetime.now(timezone.utc)
    db.session.commit()


# ═══════════════════════════════════════════
# GAMES TIER CRUD
# ═══════════════════════════════════════════
# (definidos ANTES de /games/<id> para evitar conflictos de ruta)

@api.route('/games/tiers', methods=['GET'])
def get_game_tiers():
    """Listar todos los tiers de juegos"""
    tiers = db.session.execute(select(GameTier)).scalars().all()
    return jsonify([t.serialize() for t in tiers]), 200


@api.route('/games/tiers/<int:tier_id>', methods=['GET'])
def get_game_tier(tier_id):
    """Obtener un tier por ID"""
    tier = db.session.get(GameTier, tier_id)
    if not tier:
        return jsonify({"msg": "Game tier not found"}), 404
    return jsonify(tier.serialize()), 200


@api.route('/games/tiers', methods=['POST'])
@jwt_required()
def create_game_tier():
    """Crear un GameTier para un juego"""
    body = request.get_json()
    if not body or "game_id" not in body:
        return jsonify({"msg": "game_id is required"}), 400

    game = db.session.get(Game, body["game_id"])
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    existing = db.session.execute(
        select(GameTier).where(GameTier.game_id == body["game_id"])
    ).scalar_one_or_none()
    if existing:
        return jsonify({"msg": "Game tier already exists for this game"}), 400

    tier = GameTier(game_id=body["game_id"])
    db.session.add(tier)
    db.session.commit()

    return jsonify({"msg": "Game tier created", "tier": tier.serialize()}), 201


@api.route('/games/tiers/<int:tier_id>', methods=['PUT'])
@jwt_required()
def update_game_tier(tier_id):
    """Recalcular tiers desde los votos de usuarios"""
    tier = db.session.get(GameTier, tier_id)
    if not tier:
        return jsonify({"msg": "Game tier not found"}), 404

    _recalcular_game_tier(tier)

    return jsonify({"msg": "Game tier recalculated", "tier": tier.serialize()}), 200


@api.route('/games/tiers/<int:tier_id>', methods=['DELETE'])
@jwt_required()
def delete_game_tier(tier_id):
    """Eliminar un GameTier"""
    tier = db.session.get(GameTier, tier_id)
    if not tier:
        return jsonify({"msg": "Game tier not found"}), 404

    db.session.delete(tier)
    db.session.commit()

    return jsonify({"msg": "Game tier deleted"}), 200


# ═══════════════════════════════════════════
# GAMES CRUD
# ═══════════════════════════════════════════

@api.route('/games', methods=['GET'])
def get_games():
    """Listar todos los juegos"""
    games = db.session.execute(select(Game)).scalars().all()
    return jsonify([g.serialize() for g in games]), 200


@api.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """Obtener un juego por ID"""
    game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"msg": "Game not found"}), 404
    return jsonify(game.serialize()), 200


@api.route('/games', methods=['POST'])
@jwt_required()
def create_game():
    """Crear un nuevo juego (admin)"""
    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400

    required = ["title", "description", "release_date",
                "developer", "publisher", "cover_img_url",
                "genres", "platforms"]
    missing = [f for f in required if f not in body]
    if missing:
        return jsonify({"msg": f"Missing fields: {', '.join(missing)}"}), 400

    release = body["release_date"]
    if isinstance(release, str):
        release = datetime.fromisoformat(release).date()

    game = Game(
        title=body["title"],
        description=body["description"],
        release_date=release,
        developer=body["developer"],
        publisher=body["publisher"],
        cover_img_url=body["cover_img_url"],
        genres=body["genres"],
        platforms=body["platforms"]
    )
    db.session.add(game)
    db.session.flush()  # para obtener game.id

    # Auto-crear GameTier asociado
    tier = GameTier(game_id=game.id)
    db.session.add(tier)
    db.session.commit()

    return jsonify({"msg": "Game created", "game": game.serialize()}), 201


@api.route('/games/<int:game_id>', methods=['PUT'])
@jwt_required()
def update_game(game_id):
    """Actualizar un juego (admin)"""
    game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400

    updatable = ["title", "description", "developer",
                 "publisher", "cover_img_url", "genres", "platforms"]
    for field in updatable:
        if field in body:
            setattr(game, field, body[field])

    if "release_date" in body:
        release = body["release_date"]
        if isinstance(release, str):
            release = datetime.fromisoformat(release).date()
        game.release_date = release

    db.session.commit()
    return jsonify({"msg": "Game updated", "game": game.serialize()}), 200


@api.route('/games/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_game(game_id):
    """Eliminar un juego (admin)"""
    game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    db.session.delete(game)
    db.session.commit()

    return jsonify({"msg": "Game deleted"}), 200


# ═══════════════════════════════════════════
# USER GAME TIER CRUD (voto 1-5 del usuario)
# ═══════════════════════════════════════════

@api.route('/user/game-tiers', methods=['GET'])
@jwt_required()
def get_user_game_tiers():
    """Listar votos del usuario logueado"""
    user_id = get_jwt_identity()
    votes = db.session.execute(
        select(UserGameTier).where(UserGameTier.user_id == user_id)
    ).scalars().all()
    return jsonify([v.serialize() for v in votes]), 200


@api.route('/user/game-tiers/<int:vote_id>', methods=['GET'])
@jwt_required()
def get_user_game_tier(vote_id):
    """Obtener un voto específico"""
    user_id = get_jwt_identity()
    vote = db.session.execute(
        select(UserGameTier).where(
            UserGameTier.id == vote_id,
            UserGameTier.user_id == user_id
        )
    ).scalar_one_or_none()
    if not vote:
        return jsonify({"msg": "Vote not found"}), 404
    return jsonify(vote.serialize()), 200


@api.route('/user/game-tiers', methods=['POST'])
@jwt_required()
def create_user_game_tier():
    """Votar un juego (rating 1-5)"""
    user_id = get_jwt_identity()
    body = request.get_json()

    if not body or "game_tier_id" not in body or "rating" not in body:
        return jsonify({"msg": "game_tier_id and rating are required"}), 400

    rating = body["rating"]
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"msg": "Rating must be an integer between 1 and 5"}), 400

    game_tier = db.session.get(GameTier, body["game_tier_id"])
    if not game_tier:
        return jsonify({"msg": "Game tier not found"}), 404

    existing = db.session.execute(
        select(UserGameTier).where(
            UserGameTier.user_id == user_id,
            UserGameTier.game_tier_id == body["game_tier_id"]
        )
    ).scalar_one_or_none()
    if existing:
        return jsonify({"msg": "You already voted for this game"}), 400

    vote = UserGameTier(
        user_id=user_id,
        game_tier_id=body["game_tier_id"],
        rating=rating
    )
    db.session.add(vote)
    db.session.commit()

    # Recalcular el tier del juego
    _recalcular_game_tier(game_tier)

    return jsonify({"msg": "Vote created", "vote": vote.serialize()}), 201


@api.route('/user/game-tiers/<int:vote_id>', methods=['PUT'])
@jwt_required()
def update_user_game_tier(vote_id):
    """Actualizar un voto (cambiar rating)"""
    user_id = get_jwt_identity()
    vote = db.session.execute(
        select(UserGameTier).where(
            UserGameTier.id == vote_id,
            UserGameTier.user_id == user_id
        )
    ).scalar_one_or_none()

    if not vote:
        return jsonify({"msg": "Vote not found"}), 404

    body = request.get_json()
    if not body or "rating" not in body:
        return jsonify({"msg": "rating is required"}), 400

    rating = body["rating"]
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"msg": "Rating must be an integer between 1 and 5"}), 400

    vote.rating = rating
    db.session.commit()

    game_tier = db.session.get(GameTier, vote.game_tier_id)
    if game_tier:
        _recalcular_game_tier(game_tier)

    return jsonify({"msg": "Vote updated", "vote": vote.serialize()}), 200


@api.route('/user/game-tiers/<int:vote_id>', methods=['DELETE'])
@jwt_required()
def delete_user_game_tier(vote_id):
    """Eliminar un voto"""
    user_id = get_jwt_identity()
    vote = db.session.execute(
        select(UserGameTier).where(
            UserGameTier.id == vote_id,
            UserGameTier.user_id == user_id
        )
    ).scalar_one_or_none()

    if not vote:
        return jsonify({"msg": "Vote not found"}), 404

    game_tier_id = vote.game_tier_id
    db.session.delete(vote)
    db.session.commit()

    game_tier = db.session.get(GameTier, game_tier_id)
    if game_tier:
        _recalcular_game_tier(game_tier)

    return jsonify({"msg": "Vote deleted"}), 200


# ═══════════════════════════════════════════
# USER GAME LIST CRUD (lista personal)
# ═══════════════════════════════════════════

@api.route('/user/games', methods=['GET'])
@jwt_required()
def get_user_game_list():
    """Listar juegos en la lista del usuario"""
    user_id = get_jwt_identity()
    entries = db.session.execute(
        select(UserGameList).where(UserGameList.user_id == user_id)
    ).scalars().all()
    return jsonify([e.serialize() for e in entries]), 200


@api.route('/user/games/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_user_game_entry(entry_id):
    """Obtener una entrada de la lista"""
    user_id = get_jwt_identity()
    entry = db.session.execute(
        select(UserGameList).where(
            UserGameList.id == entry_id,
            UserGameList.user_id == user_id
        )
    ).scalar_one_or_none()
    if not entry:
        return jsonify({"msg": "Entry not found"}), 404
    return jsonify(entry.serialize()), 200


@api.route('/user/games', methods=['POST'])
@jwt_required()
def add_user_game():
    """Agregar juego a la lista personal"""
    user_id = get_jwt_identity()
    body = request.get_json()

    if not body or "game_id" not in body:
        return jsonify({"msg": "game_id is required"}), 400

    game = db.session.get(Game, body["game_id"])
    if not game:
        return jsonify({"msg": "Game not found"}), 404

    existing = db.session.execute(
        select(UserGameList).where(
            UserGameList.user_id == user_id,
            UserGameList.game_id == body["game_id"]
        )
    ).scalar_one_or_none()
    if existing:
        return jsonify({"msg": "Game already in your list"}), 400

    entry = UserGameList(
        user_id=user_id,
        game_id=body["game_id"],
        status=body.get("status", "want_to_play"),
        rating=body.get("rating", 0),
        review=body.get("review", "no review")
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({"msg": "Game added to your list", "entry": entry.serialize()}), 201


@api.route('/user/games/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_user_game_entry(entry_id):
    """Actualizar una entrada de la lista"""
    user_id = get_jwt_identity()
    entry = db.session.execute(
        select(UserGameList).where(
            UserGameList.id == entry_id,
            UserGameList.user_id == user_id
        )
    ).scalar_one_or_none()

    if not entry:
        return jsonify({"msg": "Entry not found"}), 404

    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400

    valid_statuses = ["want_to_play", "playing", "completed", "dropped"]
    if "status" in body:
        if body["status"] not in valid_statuses:
            return jsonify({"msg": f"Invalid status. Valid: {', '.join(valid_statuses)}"}), 400
        entry.status = body["status"]
        if body["status"] == "completed":
            entry.completed_at = datetime.now(timezone.utc)

    if "rating" in body:
        entry.rating = body["rating"]
    if "review" in body:
        entry.review = body["review"]

    db.session.commit()
    return jsonify({"msg": "Entry updated", "entry": entry.serialize()}), 200


@api.route('/user/games/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_user_game_entry(entry_id):
    """Eliminar juego de la lista personal"""
    user_id = get_jwt_identity()
    entry = db.session.execute(
        select(UserGameList).where(
            UserGameList.id == entry_id,
            UserGameList.user_id == user_id
        )
    ).scalar_one_or_none()

    if not entry:
        return jsonify({"msg": "Entry not found"}), 404

    db.session.delete(entry)
    db.session.commit()

    return jsonify({"msg": "Entry deleted"}), 200
