import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import useGlobalReducer from "../../hooks/useGlobalReducer.jsx";
import "./Login.css";

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

export const Login = () => {
  const { store, dispatch } = useGlobalReducer();
  const navigate = useNavigate();
  const location = useLocation();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);
  const successMessage = location.state?.message || "";

  useEffect(() => {
    if (store.isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [store.isAuthenticated, navigate]);

  const validate = () => {
    const errs = {};
    if (!username.trim()) {
      errs.username = "Username is required";
    }
    if (!password) {
      errs.password = "Password is required";
    }
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError("");

    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setLoading(true);
    try {
      const resp = await fetch(`${VITE_BACKEND_URL}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await resp.json();

      if (!resp.ok) {
        setApiError(data.msg || "Invalid email or password.");
        return;
      }

      const { token, user_id } = data;
      const userData = { id: user_id, username };

      sessionStorage.setItem("token", token);
      sessionStorage.setItem("user", JSON.stringify(userData));

      dispatch({
        type: "set_auth",
        payload: { token, user: userData },
      });

      navigate("/", { replace: true });
    } catch (err) {
      setApiError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login">
      <div className="login__inner">
        <div className="login__card">
          <div className="login__card-body">
            <h1 className="login__title">Welcome Back</h1>
            <p className="login__subtitle">
              Log in to your Game-Side account
            </p>

            <form onSubmit={handleSubmit} noValidate>
              {successMessage && (
                <div className="login__alert login__alert--success" role="alert">
                  {successMessage}
                </div>
              )}
              {apiError && (
                <div className="login__alert login__alert--error" role="alert">
                  {apiError}
                </div>
              )}

              <div className="login__field">
                <label htmlFor="username" className="login__label">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  className={`login__input ${errors.username ? "login__input--error" : ""}`}
                  placeholder="Your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
                {errors.username && (
                  <div className="login__error">{errors.username}</div>
                )}
              </div>

              <div className="login__field">
                <label htmlFor="password" className="login__label">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  className={`login__input ${errors.password ? "login__input--error" : ""}`}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                {errors.password && (
                  <div className="login__error">{errors.password}</div>
                )}
              </div>

              <button
                type="submit"
                className="login__btn login__btn--submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="login__spinner" role="status" />
                    Logging in…
                  </>
                ) : (
                  "Log In"
                )}
              </button>
            </form>

            <p className="login__footer">
              Don&apos;t have an account?{" "}
              <Link to="/signup" className="login__link">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
