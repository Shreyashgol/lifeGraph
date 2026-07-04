import { GoogleLogin } from "@react-oauth/google";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { ThemeToggle } from "@/components/theme-toggle";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/auth-context";

export default function LoginPage() {
  const { isAuthenticated, login, register, loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (isRegister) {
        await register(email, password, name || undefined);
      } else {
        await login(email, password);
      }
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center p-6 bg-gradient-to-br from-background via-muted/50 to-background">
      <div className="absolute right-4 top-4">
        <ThemeToggle />
      </div>
      <Card className="w-full max-w-md shadow-xl border border-muted/85 backdrop-blur-sm bg-card/90">
        <CardHeader className="space-y-1">
          <CardTitle className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80">
            LifeGraph
          </CardTitle>
          <CardDescription className="text-sm text-muted-foreground">
            {isRegister
              ? "Create your account to start charting your life"
              : "Welcome back. Log in to access your personal intelligence engine"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSubmit} className="space-y-3">
            {isRegister && (
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground" htmlFor="name">Name</label>
                <Input
                  id="name"
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="bg-background/50 focus-visible:ring-primary"
                />
              </div>
            )}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground" htmlFor="email">Email</label>
              <Input
                id="email"
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-background/50 focus-visible:ring-primary"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground" htmlFor="password">Password</label>
              <Input
                id="password"
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-background/50 focus-visible:ring-primary"
              />
            </div>
            {error && <p className="text-xs text-destructive mt-1">{error}</p>}
            <Button
              type="submit"
              disabled={loading}
              className="w-full font-semibold transition-all shadow-md hover:shadow-lg active:scale-[0.98] mt-2"
            >
              {loading ? "Please wait..." : isRegister ? "Sign Up" : "Log In"}
            </Button>
          </form>

          <div className="relative flex items-center justify-center py-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-muted-foreground/20"></div>
            </div>
            <span className="relative bg-card px-3 text-xs uppercase text-muted-foreground font-medium">
              Or continue with
            </span>
          </div>

          <div className="flex justify-center w-full">
            <GoogleLogin
              onSuccess={async (credentialResponse) => {
                const credential = credentialResponse.credential;
                if (!credential) {
                  setError("Google sign-in failed. Please try again.");
                  return;
                }
                setLoading(true);
                try {
                  await loginWithGoogle(credential);
                  navigate("/dashboard");
                } catch (err: any) {
                  setError(err?.message || "Google authentication failed.");
                } finally {
                  setLoading(false);
                }
              }}
              onError={() => setError("Google sign-in failed. Please try again.")}
              useOneTap
            />
          </div>

          <p className="text-center text-xs text-muted-foreground pt-2">
            {isRegister ? "Already have an account?" : "Don't have an account yet?"}{" "}
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError(null);
              }}
              className="font-semibold text-primary hover:underline focus:outline-none"
            >
              {isRegister ? "Log In" : "Sign Up"}
            </button>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
