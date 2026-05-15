// Import necessary hooks and functions from React.
import { useContext, useReducer, createContext, useEffect } from "react";
import storeReducer, { initialStore } from "../store"; // Import the reducer and the initial state.

// Create a context to hold the global state of the application.
const StoreContext = createContext();

// Provider que envuelve la app y comparte el store + dispatch.
export function StoreProvider({ children }) {
  const [store, dispatch] = useReducer(storeReducer, initialStore());

  // 👇 Al cargar la página, restaura la sesión desde sessionStorage
  //    (para que al refrescar no se pierda el login)
  useEffect(() => {
    dispatch({ type: "restore_auth" });
  }, []);

  return (
    <StoreContext.Provider value={{ store, dispatch }}>
      {children}
    </StoreContext.Provider>
  );
}

// Hook personalizado para acceder al store desde cualquier componente.
export default function useGlobalReducer() {
  const { store, dispatch } = useContext(StoreContext);
  return { store, dispatch };
}
