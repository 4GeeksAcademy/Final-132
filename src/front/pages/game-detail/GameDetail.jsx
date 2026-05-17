import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import "./GameDetail.css";

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

const TIER_COLORS = {
  S: "#FFD700",
  A: "#4CAF50",
  B: "#2196F3",
  C: "#9E9E9E",
  D: "#FF9800",
  F: "#F44336",
  Undefined: "#C0C0C0",
};

const PLATFORM_LABELS = {
  pc: "PC",
  windows: "PC",
  mac: "Mac",
  linux: "Linux",
  playstation: "PlayStation",
  ps4: "PlayStation 4",
  ps5: "PlayStation 5",
  xbox: "Xbox",
  xbox_one: "Xbox One",
  xbox_series: "Xbox Series X|S",
  nintendo: "Nintendo",
  switch: "Nintendo Switch",
  mobile: "Mobile",
  ios: "iOS",
  android: "Android",
};

export const GameDetail = () => {
  const { id } = useParams();
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [commentText, setCommentText] = useState("");
  const [comments, setComments] = useState([]);
  const [posting, setPosting] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const [favLoading, setFavLoading] = useState(false);
  const [userRating, setUserRating] = useState(0);
  const [ratingLoading, setRatingLoading] = useState(false);
  const [userVoteId, setUserVoteId] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const token = sessionStorage.getItem("token");
    const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

    Promise.all([
      fetch(`${VITE_BACKEND_URL}/api/games/${id}`),
      fetch(`${VITE_BACKEND_URL}/api/favorite/status/${id}`, {
        headers: authHeaders,
      }),
      fetch(`${VITE_BACKEND_URL}/api/user/game-tiers`, {
        headers: authHeaders,
      }),
    ])
      .then(async ([gameRes, favRes, voteRes]) => {
        if (!gameRes.ok) throw new Error(`Error ${gameRes.status}`);
        const gameData = await gameRes.json();
        setGame(gameData);
        setComments(gameData.comments || []);

        if (favRes.ok) {
          const favData = await favRes.json();
          setIsFavorite(favData.is_favorite);
        }

        // Check if user already voted for this game
        if (voteRes.ok) {
          const votes = await voteRes.json();
          if (gameData.game_tier?.id) {
            const myVote = (Array.isArray(votes) ? votes : []).find(
              (v) => v.game_tier_id === gameData.game_tier.id
            );
            if (myVote) {
              setUserRating(myVote.rating);
              setUserVoteId(myVote.id);
            }
          }
        }

        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  const handlePostComment = async () => {
    if (!commentText.trim()) return;
    setPosting(true);
    try {
      const token = sessionStorage.getItem("token");
      const res = await fetch(`${VITE_BACKEND_URL}/api/games/${id}/comments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ content: commentText }),
      });
      if (!res.ok) throw new Error("Failed to post comment");
      const newComment = await res.json();
      setComments((prev) => [...prev, newComment]);
      setCommentText("");
    } catch (err) {
      console.error("Error posting comment:", err);
    } finally {
      setPosting(false);
    }
  };

  const handleToggleFavorite = async () => {
    setFavLoading(true);
    try {
      const token = sessionStorage.getItem("token");
      const res = await fetch(`${VITE_BACKEND_URL}/api/favorite/change`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ game_id: parseInt(id) }),
      });
      if (res.ok) {
        const data = await res.json();
        setIsFavorite(data.is_favorite);
        const gameRes = await fetch(`${VITE_BACKEND_URL}/api/games/${id}`);
        if (gameRes.ok) setGame(await gameRes.json());
      }
    } catch (err) {
      console.error("Error toggling favorite:", err);
    } finally {
      setFavLoading(false);
    }
  };

  const handleRate = async (rating) => {
    setRatingLoading(true);
    try {
      const token = sessionStorage.getItem("token");
      const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
      const body = { game_id: parseInt(id), rating };

      if (userVoteId) {
        // Update existing vote
        const res = await fetch(
          `${VITE_BACKEND_URL}/api/user/game-tiers/${userVoteId}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              ...authHeaders,
            },
            body: JSON.stringify({ rating }),
          }
        );
        if (!res.ok) throw new Error("Failed to update vote");
      } else {
        // Create new vote
        const res = await fetch(`${VITE_BACKEND_URL}/api/user/game-tiers`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...authHeaders,
          },
          body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error("Failed to create vote");
      }

      // Refetch game to update average rating
      const gameRes = await fetch(`${VITE_BACKEND_URL}/api/games/${id}`);
      if (gameRes.ok) {
        const data = await gameRes.json();
        setGame(data);
      }
      setUserRating(rating);
    } catch (err) {
      console.error("Error rating game:", err);
    } finally {
      setRatingLoading(false);
    }
  };

  const renderStars = (rating) => {
    const displayRating = game?.average_rating ?? 0;
    const rounded = Math.round(displayRating);
    return (
      <div className="game-detail__rating-section">
        {/* Interactive stars for voting */}
        <div className="game-detail__stars-input">
          <span className="game-detail__stars-label">Tu valoración:</span>
          <div className="game-detail__stars-group">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                className={`game-detail__star-btn ${star <= userRating ? "game-detail__star-btn--active" : ""}`}
                onClick={() => handleRate(star)}
                disabled={ratingLoading}
                title={`${star} estrella${star > 1 ? "s" : ""}`}
              >
                {star <= userRating ? "★" : "☆"}
              </button>
            ))}
          </div>
          {ratingLoading && <span className="game-detail__rating-loading">...</span>}
        </div>
        {/* Display average rating */}
        <span className="game-detail__stars">
          {"★".repeat(rounded)}
          {"☆".repeat(5 - rounded)}
          <span className="game-detail__rating-value">
            {" "}({Number(displayRating).toFixed(1)})
          </span>
        </span>
      </div>
    );
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  // ═══════════════════════════════════════
  //  LOADING STATE
  // ═══════════════════════════════════════
  if (loading) {
    return (
      <div className="game-detail">
        <div className="game-detail__inner">
          <div className="skeleton-detail">
            <div className="skeleton-detail__back" />
            <div className="skeleton-detail__hero" />
            <div className="skeleton-detail__body">
              <div className="skeleton-detail__line skeleton-detail__line--title" />
              <div className="skeleton-detail__line skeleton-detail__line--medium" />
              <div className="skeleton-detail__line skeleton-detail__line--long" />
              <div className="skeleton-detail__line skeleton-detail__line--long" />
              <div className="skeleton-detail__line skeleton-detail__line--medium" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════
  //  ERROR / 404 STATE
  // ═══════════════════════════════════════
  if (error || !game) {
    const is404 = error?.includes("404") || error?.includes("404");
    return (
      <div className="game-detail">
        <div className="game-detail__inner">
          <div className="error-state">
            <h2 className="error-state__title">
              {is404 ? "Juego no encontrado" : "Algo sali\u00f3 mal"}
            </h2>
            <p className="error-state__desc">
              {is404
                ? "El juego que buscas no existe o ha sido eliminado."
                : error || "No se pudo cargar la informaci\u00f3n del juego."}
            </p>
            <Link to="/" className="error-state__btn">
              Volver al inicio
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════
  //  MAIN CONTENT
  // ═══════════════════════════════════════
  const platforms = game.platforms || [];
  const genres = game.genres || [];
  const features = game.features || [
    "Cooperativo online hasta 4 jugadores",
    "Gran variedad de Warframes",
    "Sistema avanzado de movimiento",
    "Misiones \u00e9picas y eventos en vivo",
    "Personalizaci\u00f3n completa de personajes",
    "Actualizaciones gratuitas constantes",
  ];

  return (
    <div className="game-detail">
      <div className="game-detail__inner">
        {/* ── Back Link ── */}
        <Link to="/" className="game-detail__back">
          &larr; Volver a Games
        </Link>

        {/* ── Hero Section ── */}
        <div className="game-detail__hero">
          <img
            className="game-detail__cover"
            src={game.cover_img_url}
            alt={game.title}
            onError={(e) => {
              e.target.style.display = "none";
              e.target.nextSibling.style.display = "flex";
            }}
          />
          <div className="game-detail__hero-fallback">
            {game.title?.slice(0, 2).toUpperCase() || "??"}
          </div>
          {game.tier && game.tier !== "Undefined" && (
            <span
              className="game-detail__tier"
              style={{
                backgroundColor: TIER_COLORS[game.tier] || "#C0C0C0",
              }}
            >
              {game.tier}
            </span>
          )}
        </div>

        {/* ── Info Section ── */}
        <div className="game-detail__info">
          <h1 className="game-detail__title">{game.title}</h1>
          {renderStars(game.average_rating)}

          <div className="game-detail__metadata">
            {game.developer && (
              <div className="game-detail__meta-item">
                <span className="game-detail__meta-label">Desarrollador</span>
                <span className="game-detail__meta-value">
                  {game.developer}
                </span>
              </div>
            )}
            {game.release_date && (
              <div className="game-detail__meta-item">
                <span className="game-detail__meta-label">
                  Fecha de lanzamiento
                </span>
                <span className="game-detail__meta-value">
                  {formatDate(game.release_date)}
                </span>
              </div>
            )}
            {platforms.length > 0 && (
              <div className="game-detail__meta-item">
                <span className="game-detail__meta-label">Plataformas</span>
                <span className="game-detail__meta-value">
                  {platforms
                    .map(
                      (p) =>
                        PLATFORM_LABELS[p.toLowerCase()] || p
                    )
                    .join(" | ")}
                </span>
              </div>
            )}
          </div>

          {/* ── Description ── */}
          {(game.description || game.summary) && (
            <p className="game-detail__description">
              {game.description || game.summary}
            </p>
          )}

          {/* ── Genres ── */}
          {genres.length > 0 && (
            <div className="game-detail__genres">
              {genres.map((genre, i) => (
                <span key={i} className="game-detail__genre">
                  {genre}
                </span>
              ))}
            </div>
          )}

          {/* ── Caracter\u00edsticas ── */}
          <div className="game-detail__section">
            <h2 className="game-detail__section-title">Caracter\u00edsticas</h2>
            <ul className="game-detail__features">
              {features.map((feature, i) => (
                <li key={i} className="game-detail__feature">
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          {/* ── Stats ── */}
          <div className="game-detail__stats">
            <span className="game-detail__stat">
              💬 {game.comment_count ?? 0} comentarios
            </span>
            <span className="game-detail__stat">
              ❤️ {game.favorite_count ?? 0} favoritos
            </span>
            <button
              className={`game-detail__fav-btn ${isFavorite ? "game-detail__fav-btn--active" : ""}`}
              onClick={handleToggleFavorite}
              disabled={favLoading}
            >
              {isFavorite ? "★" : "☆"} {isFavorite ? "Favorito" : "Favoritos"}
            </button>
          </div>

          {/* ── Comments Section ── */}
          <div className="game-detail__section">
            <h2 className="game-detail__section-title">
              Comentarios ({comments.length})
            </h2>

            <div className="game-detail__comment-form">
              <textarea
                className="game-detail__comment-input"
                placeholder="Escribe tu opini\u00f3n sobre este juego..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                rows={3}
              />
              <button
                className="game-detail__comment-btn"
                onClick={handlePostComment}
                disabled={posting || !commentText.trim()}
              >
                {posting ? "Publicando..." : "Publicar comentario"}
              </button>
            </div>

            {comments.length === 0 ? (
              <p className="game-detail__no-comments">
                No hay comentarios a\u00fan. S\u00e9 el primero en opinar.
              </p>
            ) : (
              <div className="game-detail__comments-list">
                {comments.map((comment, i) => (
                  <div key={comment.id || i} className="game-detail__comment">
                    <span className="game-detail__comment-author">
                      {comment.username || comment.user?.username || "An\u00f3nimo"}
                    </span>
                    <p className="game-detail__comment-text">
                      {comment.content || comment.text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
