import { googleLogout } from "@react-oauth/google";
import { createContext, useContext, useEffect, useState } from "react";
import { apiPost, apiGet } from "@/lib/api";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  picture?: string | null;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  loginWithGoogle: (credential: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);
const TOKEN_KEY = "lifegraph.token";
const USER_KEY = "lifegraph.user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser) as AuthUser);

        // Refresh user info from /auth/me
        apiGet<AuthUser>("/auth/me")
          .then((freshUser) => {
            setUser(freshUser);
            localStorage.setItem(USER_KEY, JSON.stringify(freshUser));
          })
          .catch(() => {
            // Token likely expired; apiGet handles cleaning up storage and redirection.
          });
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      }
    }
    setReady(true);
  }, []);

  async function login(email: string, password: string): Promise<void> {
    const res = await apiPost<AuthResponse>("/auth/login", { email, password });
    setUser(res.user);
    localStorage.setItem(TOKEN_KEY, res.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(res.user));
  }

  async function register(email: string, password: string, name?: string): Promise<void> {
    const res = await apiPost<AuthResponse>("/auth/register", { email, password, name });
    setUser(res.user);
    localStorage.setItem(TOKEN_KEY, res.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(res.user));
  }

  async function loginWithGoogle(credential: string): Promise<void> {
    const res = await apiPost<AuthResponse>("/auth/google", { id_token: credential });
    setUser(res.user);
    localStorage.setItem(TOKEN_KEY, res.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(res.user));
  }

  function logout() {
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    googleLogout();
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        ready,
        login,
        register,
        loginWithGoogle,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
