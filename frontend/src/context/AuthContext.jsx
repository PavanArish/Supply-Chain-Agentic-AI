import { createContext, useContext, useEffect, useState } from "react";
import { auth } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("sca_token");
    if (!token) {
      setLoading(false);
      return;
    }
    auth
      .me()
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem("sca_token"))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const res = await auth.login(email, password);
    localStorage.setItem("sca_token", res.data.access_token);
    const me = await auth.me();
    setUser(me.data);
  };

  const signup = async (name, email, password) => {
    const res = await auth.signup(name, email, password);
    localStorage.setItem("sca_token", res.data.access_token);
    const me = await auth.me();
    setUser(me.data);
  };

  const logout = () => {
    localStorage.removeItem("sca_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
