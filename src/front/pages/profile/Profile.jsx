import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import useGlobalReducer from "../../hooks/useGlobalReducer.jsx";

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const STATUS_LABELS = {
  want_to_play: "Quiero jugar",
  playing: "Jugando",
  completed: "Completado",
  dropped: "Abandonado",
};

const STATUS_BADGES = {
  want_to_play: "bg-primary",
  playing: "bg-success",
  completed: "bg-warning text-dark",
  dropped: "bg-danger",
};

export const Profile = () => {
  const { store } = useGlobalReducer();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!store.user?.id) {
      setLoading(false);
      setError("No se encontr\u00f3 informaci\u00f3n del usuario.");
      return;
    }

    fetch(`${VITE_BACKEND_URL}/api/users/${store.user.id}`, {
      headers: {
        Authorization: `Bearer ${store.token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Error ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setUserData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [store.user?.id, store.token]);

  const userGames = userData?.games || [];
  const stats = {
    total: userGames.length,
    comments: userData?.comment_count ?? userData?.comments?.length ?? 0,
    favorites: userData?.favorite_count ?? userData?.favorites?.length ?? 0,
  };

  // ═══════════════ LOADING ═══════════════
  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  // ═══════════════ ERROR ═══════════════
  if (error) {
    return (
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-6 text-center">
            <div className="alert alert-danger">
              <h4 className="alert-heading">Something went wrong</h4>
              <p className="mb-0">{error}</p>
            </div>
            <Link to="/" className="btn btn-primary">
              Volver al inicio
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const user = userData || store.user;

  return (
    <div className="container py-4">
      {/* ═══ Profile Header ═══ */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body d-flex align-items-center gap-4 p-4">
              <div
                className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center"
                style={{ width: "64px", height: "64px", fontSize: "1.5rem", fontWeight: "bold" }}
              >
                {user?.username?.charAt(0).toUpperCase() || "?"}
              </div>
              <div>
                <h1 className="h4 mb-1">{user?.username || "Usuario"}</h1>
                <p className="text-muted mb-0">{user?.email || ""}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ═══ Stats ═══ */}
      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="card text-center shadow-sm">
            <div className="card-body">
              <h3 className="text-primary mb-1">{stats.total}</h3>
              <span className="text-muted">Juegos</span>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-center shadow-sm">
            <div className="card-body">
              <h3 className="text-primary mb-1">{stats.comments}</h3>
              <span className="text-muted">Comentarios</span>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-center shadow-sm">
            <div className="card-body">
              <h3 className="text-primary mb-1">{stats.favorites}</h3>
              <span className="text-muted">Favoritos</span>
            </div>
          </div>
        </div>
      </div>

      {/* ═══ Game List ═══ */}
      <div className="card shadow-sm">
        <div className="card-header">
          <h2 className="h5 mb-0">Mis Juegos</h2>
        </div>
        <div className="card-body">
          {userGames.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-muted mb-3">
                No tienes juegos registrados a\u00fan.
              </p>
              <Link to="/" className="btn btn-outline-primary">
                Explorar juegos
              </Link>
            </div>
          ) : (
            <div className="row g-3">
              {userGames.map((entry) => {
                const game = entry.game || entry;
                const status = entry.status || entry.user_status;
                return (
                  <div key={game.id || entry.id} className="col-md-6 col-lg-4">
                    <div className="card h-100 shadow-sm">
                      <Link to={`/games/${game.id}`} className="text-decoration-none">
                        <div
                          className="card-img-top d-flex align-items-center justify-content-center bg-light"
                          style={{ height: "160px", overflow: "hidden" }}
                        >
                          <img
                            src={game.cover_img_url}
                            alt={game.title}
                            className="img-fluid"
                            style={{ objectFit: "cover", height: "100%", width: "100%" }}
                            onError={(e) => {
                              e.target.style.display = "none";
                              e.target.nextSibling.style.display = "flex";
                            }}
                          />
                          <span
                            className="text-muted d-none"
                            style={{ fontSize: "2rem", fontWeight: "bold" }}
                          >
                            {game.title?.slice(0, 2).toUpperCase() || "??"}
                          </span>
                        </div>
                      </Link>
                      <div className="card-body">
                        <Link
                          to={`/games/${game.id}`}
                          className="text-decoration-none text-dark"
                        >
                          <h5 className="card-title">{game.title}</h5>
                        </Link>
                        {status && (
                          <span className={`badge ${STATUS_BADGES[status] || "bg-secondary"}`}>
                            {STATUS_LABELS[status] || status}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
