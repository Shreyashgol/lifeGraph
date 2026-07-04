import { GoogleLogin } from "@react-oauth/google";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { ThemeToggle } from "@/components/theme-toggle";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";

export default function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  return (
    <main className="relative flex min-h-screen items-center justify-center p-6">
      <div className="absolute right-4 top-4">
        <ThemeToggle />
      </div>
      <Card className="w-full max-w-sm text-center">
        <CardHeader>
          <CardTitle className="text-2xl">LifeGraph</CardTitle>
          <CardDescription>AI-Powered Personal Intelligence Engine</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center gap-3">
          <GoogleLogin
            onSuccess={(credentialResponse) => {
              const credential = credentialResponse.credential;
              if (!credential || !login(credential)) {
                setError("This Google account is not allowed.");
                return;
              }
              navigate("/dashboard");
            }}
            onError={() => setError("Google sign-in failed. Please try again.")}
          />
          {error && <p className="text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>
    </main>
  );
}
