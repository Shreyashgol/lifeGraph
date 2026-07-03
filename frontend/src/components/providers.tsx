"use client";

import { SessionProvider } from "next-auth/react";
import { ThemeProvider } from "next-themes";

/** Client-side providers: auth session + light/dark theme. */
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        {children}
      </ThemeProvider>
    </SessionProvider>
  );
}
