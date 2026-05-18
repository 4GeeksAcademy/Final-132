// ─── Hooks de React ───
import { useEffect, useState } from "react";
// ─── Hook del store global ───
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
// ─── Link para navegación interna ───
import { Link } from "react-router-dom";
// ─── Componente GameCard ───
import { GameCard } from "../components/GameCard";
// ─── Estilos Figma ───
import "./Home.css";

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

export const Home = () => {
  const { store, dispatch } = useGlobalReducer();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ─── Cargar juegos desde el backend ───
  const loadGames = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${VITE_BACKEND_URL}/api/games`);

      if (!response.ok)
        throw new Error(`Failed to fetch games (${response.status})`);

      const data = await response.json();

      dispatch({ type: "set_games", payload: data });
    } catch (err) {
      setError(
        err.message ||
          "Could not load games. Please check if the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGames();
  }, []);

  const games = store.games || [];

  // ═══════════════════════════════════════
  //  HERO
  // ═══════════════════════════════════════
  const HeroSection = () => (
    <section className="hero">
      <div className="hero__inner">
        <h1 className="hero__title">Tu Universo Gaming</h1>
        <p className="hero__subtitle">
          Descubre, rastrea y califica tus videojuegos favoritos. Únete a una
          comunidad apasionada de gamers.
        </p>
        <div className="hero__actions">
          <a href="#features" className="hero__btn hero__btn--primary">
            Comenzar ahora &rarr;
          </a>
          <a href="#trending" className="hero__btn hero__btn--secondary">
            Explorar juegos
          </a>
        </div>
      </div>
    </section>
  );

  // ═══════════════════════════════════════
  //  FEATURES
  // ═══════════════════════════════════════
  const FeaturesSection = () => (
    <section id="features" className="features">
      <div className="features__inner">
        <h2 className="features__title">Tu experiencia Game-side</h2>
        <div className="features__grid">
          <div className="feature-card">
            <span className="feature-card__icon">🔍</span>
            <h3 className="feature-card__title">Descubre</h3>
            <p className="feature-card__desc">Miles de juegos</p>
          </div>
          <div className="feature-card">
            <span className="feature-card__icon">📚</span>
            <h3 className="feature-card__title">Organiza</h3>
            <p className="feature-card__desc">Biblioteca personalizada</p>
          </div>
          <div className="feature-card">
            <span className="feature-card__icon">💬</span>
            <h3 className="feature-card__title">Comparte</h3>
            <p className="feature-card__desc">Tus gustos y opiniones</p>
          </div>
        </div>
      </div>
    </section>
  );

  // ═══════════════════════════════════════
  //  SURVEY CTA
  // ═══════════════════════════════════════
  const SurveyCTASection = () => (
    <section className="survey-cta">
      <div className="survey-cta__inner">
        <h2 className="survey-cta__title">
          Tu pr&oacute;ximo descubrimiento est&aacute; aqu&iacute;
        </h2>
        <p className="survey-cta__subtitle">
          Responde unas preguntas r&aacute;pidas y recibe recomendaciones
          hechas para ti.
        </p>
        <div className="survey-cta__grid">
          <div className="survey-cta__card">
            <h4 className="survey-cta__card-title">Personaliza</h4>
            <p className="survey-cta__card-desc">
              Recibe recomendaciones basadas en tus g&eacute;neros, estilo
              de juego y preferencias reales.
            </p>
          </div>
          <div className="survey-cta__card">
            <h4 className="survey-cta__card-title">Ahorra tiempo</h4>
            <p className="survey-cta__card-desc">
              Deja de perder horas buscando y encuentra t&iacute;tulos que
              encajen contigo al instante.
            </p>
          </div>
          <div className="survey-cta__card">
            <h4 className="survey-cta__card-title">Descubre</h4>
            <p className="survey-cta__card-desc">
              Explora juegos nuevos, joyas ocultas y experiencias que
              probablemente nunca has encontrado.
            </p>
          </div>
        </div>
        <Link to="/survey" className="survey-cta__btn">
          Comenzar encuesta &rarr;
        </Link>
      </div>
    </section>
  );

  // ═══════════════════  LOADING  ═══════════════════
  if (loading) {
    return (
      <>
        <HeroSection />
        <section className="section">
          <div className="section__inner">
            <h2 className="section__title">Tendencias Ahora</h2>
            <div className="skeleton-grid">
              {[1, 2, 3, 4].map((n) => (
                <div key={n} className="skeleton-card">
                  <div className="skeleton-card__cover" />
                  <div className="skeleton-card__body">
                    <div className="skeleton-card__line skeleton-card__line--medium" />
                    <div className="skeleton-card__line skeleton-card__line--short" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </>
    );
  }

  // ═══════════════════  ERROR  ═══════════════════
  if (error) {
    return (
      <>
        <HeroSection />
        <div className="error-state">
          <h4 className="error-state__title">Something went wrong</h4>
          <p className="error-state__desc">{error}</p>
          <button className="error-state__btn" onClick={loadGames}>
            Retry
          </button>
        </div>
        <SurveyCTASection />
      </>
    );
  }

  // ═══════════════════  MAIN CONTENT  ═══════════════════
  return (
    <>
      <HeroSection />
      <FeaturesSection />

      {/* ─── Trending ─── */}
      <section id="trending" className="section">
        <div className="section__inner">
          <h2 className="section__title">Tendencias Ahora</h2>
          {games.length > 0 ? (
            <div className="games-grid">
              {games.map((game) => (
                <GameCard key={game.id} game={game} />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <h4 className="empty-state__title">No games available</h4>
              <p className="empty-state__desc">Be the first to add one!</p>
            </div>
          )}
        </div>
      </section>

      {/* ─── Recommendations ─── */}
      <section
        className="section"
        style={{ background: "var(--color-surface)" }}
      >
        <div className="section__inner">
          <h2 className="section__title">Recomendaciones (para ti)</h2>
          {games.length > 0 ? (
            <div className="games-grid">
              {games.slice(0, 4).map((game) => (
                <GameCard key={game.id} game={game} />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <h4 className="empty-state__title">
                No hay recomendaciones a&uacute;n
              </h4>
              <p className="empty-state__desc">
                Completa tu perfil para recibir recomendaciones personalizadas.
              </p>
            </div>
          )}
        </div>
      </section>

      <SurveyCTASection />
    </>
  );
};
