import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Survey.css";

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

const GENRES = [
  "Acci\u00f3n",
  "Aventura",
  "RPG",
  "Estrategia",
  "Simulaci\u00f3n",
  "Deportes",
  "Carreras",
  "Lucha",
  "Shooter",
  "Terror",
  "Plataformas",
  "Puzzle",
  "Musical",
  "MMO",
];

const PLATFORMS = [
  "PC",
  "PlayStation 4",
  "PlayStation 5",
  "Xbox One",
  "Xbox Series X|S",
  "Nintendo Switch",
  "iOS",
  "Android",
];

const PLAY_STYLES = [
  { value: "casual", label: "Casual — sesiones cortas y relax" },
  { value: "competitive", label: "Competitivo — me gusta ganar" },
  { value: "immersive", label: "Inmersivo — historias profundas" },
  { value: "social", label: "Social — jugar con amigos" },
  { value: "exploration", label: "Explorador — mundos abiertos" },
];

export const Survey = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [playStyle, setPlayStyle] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const totalSteps = 3;

  const toggleGenre = (genre) => {
    setSelectedGenres((prev) =>
      prev.includes(genre)
        ? prev.filter((g) => g !== genre)
        : [...prev, genre]
    );
  };

  const togglePlatform = (platform) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platform)
        ? prev.filter((p) => p !== platform)
        : [...prev, platform]
    );
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError("");

    const payload = {
      genres: selectedGenres,
      platforms: selectedPlatforms,
      play_style: playStyle,
    };

    try {
      const token = sessionStorage.getItem("token");
      const res = await fetch(`${VITE_BACKEND_URL}/api/users/survey`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Error al enviar la encuesta");

      navigate("/?survey=done");
    } catch (err) {
      setError(err.message || "Ocurri\u00f3 un error al enviar tus preferencias.");
    } finally {
      setSubmitting(false);
    }
  };

  const progressPercent = ((step + 1) / totalSteps) * 100;

  return (
    <div className="survey">
      <div className="survey__inner">
        {/* ── Header ── */}
        <div className="survey__header">
          <h1 className="survey__title">
            Tu pr&oacute;ximo descubrimiento est&aacute; aqu&iacute;
          </h1>
          <p className="survey__subtitle">
            Responde unas preguntas r&aacute;pidas y recibe recomendaciones
            hechas para ti.
          </p>
          <div className="survey__progress">
            <div
              className="survey__progress-bar"
              style={{ width: `${progressPercent}%` }}
            />
            <span className="survey__progress-text">
              Paso {step + 1} de {totalSteps}
            </span>
          </div>
        </div>

        {/* ── Content ── */}
        <div className="survey__card">
          {error && <div className="survey__error">{error}</div>}

          {/* Step 1: Genres */}
          {step === 0 && (
            <div className="survey__step">
              <h2 className="survey__step-title">
                &iquest;Qu&eacute; g&eacute;neros te gustan?
              </h2>
              <p className="survey__step-desc">
                Selecciona todos los que m&aacute;s disfrutes.
              </p>
              <div className="survey__chips">
                {GENRES.map((genre) => (
                  <button
                    key={genre}
                    className={`survey__chip ${selectedGenres.includes(genre) ? "survey__chip--selected" : ""}`}
                    onClick={() => toggleGenre(genre)}
                  >
                    {genre}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Platforms */}
          {step === 1 && (
            <div className="survey__step">
              <h2 className="survey__step-title">
                &iquest;En qu&eacute; plataformas juegas?
              </h2>
              <p className="survey__step-desc">
                Selecciona las que uses con frecuencia.
              </p>
              <div className="survey__chips">
                {PLATFORMS.map((platform) => (
                  <button
                    key={platform}
                    className={`survey__chip ${selectedPlatforms.includes(platform) ? "survey__chip--selected" : ""}`}
                    onClick={() => togglePlatform(platform)}
                  >
                    {platform}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Play Style */}
          {step === 2 && (
            <div className="survey__step">
              <h2 className="survey__step-title">
                &iquest;C&oacute;mo te gusta jugar?
              </h2>
              <p className="survey__step-desc">
                Elige la opci&oacute;n que mejor te describa.
              </p>
              <div className="survey__styles">
                {PLAY_STYLES.map((style) => (
                  <button
                    key={style.value}
                    className={`survey__style ${playStyle === style.value ? "survey__style--selected" : ""}`}
                    onClick={() => setPlayStyle(style.value)}
                  >
                    {style.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ── Navigation ── */}
          <div className="survey__nav">
            {step > 0 ? (
              <button
                className="survey__btn survey__btn--back"
                onClick={() => setStep((prev) => prev - 1)}
              >
                &larr; Anterior
              </button>
            ) : (
              <div />
            )}

            {step < totalSteps - 1 ? (
              <button
                className="survey__btn survey__btn--next"
                onClick={() => setStep((prev) => prev + 1)}
                disabled={
                  (step === 0 && selectedGenres.length === 0) ||
                  (step === 1 && selectedPlatforms.length === 0)
                }
              >
                Siguiente &rarr;
              </button>
            ) : (
              <button
                className="survey__btn survey__btn--submit"
                onClick={handleSubmit}
                disabled={submitting || !playStyle}
              >
                {submitting ? "Enviando..." : "Descubrir juegos &rarr;"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
