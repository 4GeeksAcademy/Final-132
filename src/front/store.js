export const initialStore = () => {
  return {
    // ─── Datos del template original (no borrar) ───
    message: null,
    todos: [
      {
        id: 1,
        title: "Make the bed",
        background: null,
      },
      {
        id: 2,
        title: "Do my homework",
        background: null,
      },
    ],

    // ─── 👇 AGREGADO para auth (Login / Signup / Profile) ───
    user: null, // datos del usuario: { id, username, email }
    token: null, // JWT para autenticar peticiones
    isAuthenticated: false, // true si hay sesión activa
  };
};

export default function storeReducer(store, action = {}) {
  switch (action.type) {
    // ─── Del template original ───
    case "set_hello":
      return {
        ...store,
        message: action.payload,
      };

    case "add_task":
      const { id, color } = action.payload;
      return {
        ...store,
        todos: store.todos.map((todo) =>
          todo.id === id ? { ...todo, background: color } : todo
        ),
      };

    // ─── 👇 AGREGADO para auth ───

    // Después de login exitoso: guarda user + token en el store
    case "set_auth":
      return {
        ...store,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
      };

    // Cerrar sesión: limpia store y sessionStorage
    case "logout":
      sessionStorage.removeItem("token");
      sessionStorage.removeItem("user");
      return {
        ...store,
        user: null,
        token: null,
        isAuthenticated: false,
      };

    // Al recargar la página: recupera token desde sessionStorage
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
