import { googleLogout } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { createContext, useContext, useEffect, useState } from "react";

interface AuthUser {
  name?: string;
  email?: string;
  picture?: string;
}

interface GoogleCredential {
  name?: string;
  email?: string;
  picture?: string;
  exp?: number;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  ready: boolean;
  login: (credential: string) => boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);
const STORAGE_KEY = "lifegraph.auth";

const allowedEmails = (import.meta.env.VITE_ALLOWED_EMAILS ?? "")
  .split(",")
  .map((email: string) => email.trim().toLowerCase())
  .filter(Boolean);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        setUser(JSON.parse(raw) as AuthUser);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setReady(true);
  }, []);

  /** Validate & store a Google ID-token credential. Returns false if not allowed. */
  function login(credential: string): boolean {
    const decoded = jwtDecode<GoogleCredential>(credential);
    const email = decoded.email?.toLowerCase();
    if (allowedEmails.length > 0 && (!email || !allowedEmails.includes(email))) {
      return false;
    }
    const nextUser: AuthUser = {
      name: decoded.name,
      email: decoded.email,
      picture: decoded.picture,
    };
    setUser(nextUser);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextUser));
    return true;
  }

  function logout() {
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
    googleLogout();
  }

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, ready, login, logout }}
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
