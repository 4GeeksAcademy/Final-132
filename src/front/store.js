export const initialStore = () => {
  return {
    // ─── Mensaje ───
    message: null,

    // ─── Auth ───
    user: null,
    token: null,
    isAuthenticated: false,

    // ─── Juegos ───
    games: [],
  };
};

export default function storeReducer(store, action = {}) {
  switch (action.type) {
    // ─── Juegos ───
    case "set_games":
      return { ...store, games: action.payload };

    // ─── Auth ───
    case "set_auth":
      return {
        ...store,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
      };

    case "logout":
      sessionStorage.removeItem("token");
      sessionStorage.removeItem("user");
      return {
        ...store,
        user: null,
        token: null,
        isAuthenticated: false,
      };

    case "restore_auth":
      const token = sessionStorage.getItem("token");
      const user = JSON.parse(sessionStorage.getItem("user") || "null");
      return {
        ...store,
        user,
        token,
        isAuthenticated: !!token && !!user,
      };

    default:
      throw Error("Unknown action.");
  }
}
