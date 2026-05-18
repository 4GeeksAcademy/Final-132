import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../../hooks/useGlobalReducer.jsx";
import "./Signup.css";

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

export const Signup = () => {
  const { store } = useGlobalReducer();
  const navigate = useNavigate();

  useEffect(() => {
    if (store.isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [store.isAuthenticated, navigate]);

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    if (errors[field]) {
      setErrors((prev) => {
        const copy = { ...prev };
        delete copy[field];
        return copy;
      });
    }
  };

  const validate = () => {
    const errs = {};

    if (!form.username.trim()) {
      errs.username = "Username is required";
    } else if (!/^[a-zA-Z0-9_]{3,20}$/.test(form.username)) {
      errs.username = "Username must be 3\u201320 alphanumeric characters";
    }

    if (!form.email.trim()) {
      errs.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      errs.email = "Invalid email format";
    }

    if (!form.password) {
      errs.password = "Password is required";
    } else if (form.password.length < 8) {
      errs.password = "Password must be at least 8 characters";
    }

    if (!form.confirmPassword) {
      errs.confirmPassword = "Please confirm your password";
    } else if (form.password !== form.confirmPassword) {
      errs.confirmPassword = "Passwords do not match";
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
      const resp = await fetch(`${VITE_BACKEND_URL}/api/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          password: form.password,
        }),
      });

      const data = await resp.json();

      if (!resp.ok) {
        setApiError(data.msg || "Registration failed. Please try again.");
        return;
      }

      navigate("/login", {
        state: { message: "Account created. Please log in." },
      });
    } catch (err) {
      setApiError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup">
      <div className="signup__inner">
        <div className="signup__card">
          <div className="signup__card-body">
            <h1 className="signup__title">Create Account</h1>
            <p className="signup__subtitle">Join Game-Side today</p>

            <form onSubmit={handleSubmit} noValidate>
              {apiError && (
                <div className="signup__alert signup__alert--error" role="alert">
                  {apiError}
                </div>
              )}

              <div className="signup__field">
                <label htmlFor="username" className="signup__label">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  className={`signup__input ${errors.username ? "signup__input--error" : ""}`}
                  placeholder="Your username"
                  value={form.username}
                  onChange={handleChange("username")}
                />
                {errors.username && (
                  <div className="signup__error">{errors.username}</div>
                )}
              </div>

              <div className="signup__field">
                <label htmlFor="email" className="signup__label">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  className={`signup__input ${errors.email ? "signup__input--error" : ""}`}
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={handleChange("email")}
                />
                {errors.email && (
                  <div className="signup__error">{errors.email}</div>
                )}
              </div>

              <div className="signup__field">
                <label htmlFor="password" className="signup__label">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  className={`signup__input ${errors.password ? "signup__input--error" : ""}`}
                  placeholder="At least 8 characters"
                  value={form.password}
                  onChange={handleChange("password")}
                />
                {errors.password && (
                  <div className="signup__error">{errors.password}</div>
                )}
              </div>

              <div className="signup__field">
                <label htmlFor="confirmPassword" className="signup__label">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  className={`signup__input ${errors.confirmPassword ? "signup__input--error" : ""}`}
                  placeholder="Repeat your password"
                  value={form.confirmPassword}
                  onChange={handleChange("confirmPassword")}
                />
                {errors.confirmPassword && (
                  <div className="signup__error">
                    {errors.confirmPassword}
                  </div>
                )}
              </div>

              <button
                type="submit"
                className="signup__btn signup__btn--submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="signup__spinner" role="status" />
                    Creating account\u2026
                  </>
                ) : (
                  "Sign Up"
                )}
              </button>
            </form>

            <p className="signup__footer">
              Already have an account?{" "}
              <Link to="/login" className="signup__link">
                Log in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
