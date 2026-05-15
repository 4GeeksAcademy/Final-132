import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../../hooks/useGlobalReducer.jsx";

const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

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
      errs.username = "Username must be 3–20 alphanumeric characters";
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
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow-sm">
            <div className="card-body p-4">
              <h1 className="card-title text-center mb-1">Create Account</h1>
              <p className="text-muted text-center mb-4">
                Join Game-Side today
              </p>

              <form onSubmit={handleSubmit} noValidate>
                {apiError && (
                  <div className="alert alert-danger" role="alert">
                    {apiError}
                  </div>
                )}

                <div className="mb-3">
                  <label htmlFor="username" className="form-label">
                    Username
                  </label>
                  <input
                    id="username"
                    type="text"
                    className={`form-control ${errors.username ? "is-invalid" : ""}`}
                    placeholder="Your username"
                    value={form.username}
                    onChange={handleChange("username")}
                  />
                  {errors.username && (
                    <div className="invalid-feedback">{errors.username}</div>
                  )}
                </div>

                <div className="mb-3">
                  <label htmlFor="email" className="form-label">
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    className={`form-control ${errors.email ? "is-invalid" : ""}`}
                    placeholder="you@example.com"
                    value={form.email}
                    onChange={handleChange("email")}
                  />
                  {errors.email && (
                    <div className="invalid-feedback">{errors.email}</div>
                  )}
                </div>

                <div className="mb-3">
                  <label htmlFor="password" className="form-label">
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    className={`form-control ${errors.password ? "is-invalid" : ""}`}
                    placeholder="At least 8 characters"
                    value={form.password}
                    onChange={handleChange("password")}
                  />
                  {errors.password && (
                    <div className="invalid-feedback">{errors.password}</div>
                  )}
                </div>

                <div className="mb-3">
                  <label htmlFor="confirmPassword" className="form-label">
                    Confirm Password
                  </label>
                  <input
                    id="confirmPassword"
                    type="password"
                    className={`form-control ${errors.confirmPassword ? "is-invalid" : ""}`}
                    placeholder="Repeat your password"
                    value={form.confirmPassword}
                    onChange={handleChange("confirmPassword")}
                  />
                  {errors.confirmPassword && (
                    <div className="invalid-feedback">
                      {errors.confirmPassword}
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" />
                      Creating account…
                    </>
                  ) : (
                    "Sign Up"
                  )}
                </button>
              </form>

              <p className="text-center mt-4 mb-0">
                Already have an account?{" "}
                <Link to="/login" className="text-decoration-none">
                  Log in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
