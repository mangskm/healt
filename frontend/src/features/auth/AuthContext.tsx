import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { getCurrentUser, login as loginRequest, logout as logoutRequest, type AuthUser, unauthorizedEvent } from "../../services/api";

type AuthState = "loading" | "anonymous" | "authenticated";

interface AuthContextValue {
  state: AuthState;
  user: AuthUser | null;
  login(email: string, password: string): Promise<void>;
  logout(): Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>("loading");
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    let active = true;
    getCurrentUser().then((currentUser) => {
      if (!active) return;
      setUser(currentUser);
      setState(currentUser ? "authenticated" : "anonymous");
    }).catch(() => {
      if (active) setState("anonymous");
    });
    const recoverFromUnauthorized = () => {
      setUser(null);
      setState("anonymous");
    };
    window.addEventListener(unauthorizedEvent, recoverFromUnauthorized);
    return () => {
      active = false;
      window.removeEventListener(unauthorizedEvent, recoverFromUnauthorized);
    };
  }, []);

  const value: AuthContextValue = {
    state,
    user,
    async login(email, password) {
      const currentUser = await loginRequest(email, password);
      setUser(currentUser);
      setState("authenticated");
    },
    async logout() {
      await logoutRequest();
      setUser(null);
      setState("anonymous");
    },
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider.");
  return value;
}
