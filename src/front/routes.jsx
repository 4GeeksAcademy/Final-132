import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
} from "react-router-dom";
import { Layout } from "./pages/Layout";
import { Home } from "./pages/Home";

// ─── 👇 AGREGADO: importar las páginas nuevas ───
import { Login } from "./pages/login/Login";
import { Signup } from "./pages/signup/Signup";
import { Profile } from "./pages/profile/Profile";
import { GameDetail } from "./pages/game-detail/GameDetail";
import { Survey } from "./pages/survey/Survey";
import { TierList } from "./pages/tier-list/TierList";
import { RequireAuth } from "./components/RequireAuth";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route
      path="/"
      element={<Layout />}
      errorElement={<h1>Not found!</h1>}
    >
      {/* ─── Ruta original ─── */}
      <Route path="/" element={<Home />} />

      {/* ─── 👇 AGREGADO: rutas de auth ─── */}
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* ─── 👇 Ruta protegida (solo si está logueado) ─── */}
      <Route element={<RequireAuth />}>
        <Route path="/profile" element={<Profile />} />
        <Route path="/game-detail/:id" element={<GameDetail />} />
        <Route path="/survey/:gameId" element={<Survey />} />
        <Route path="/tier-list" element={<TierList />} />
      </Route>
    </Route>
  )
);
