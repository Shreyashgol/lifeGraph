import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

/**
 * NextAuth (Auth.js v5) configuration.
 *
 * Version 1 is login-gated single-tenant: any Google account may sign in and
 * access the single dataset. Restrict access by setting AUTH_ALLOWED_EMAILS to a
 * comma-separated allowlist.
 */
const allowedEmails = (process.env.AUTH_ALLOWED_EMAILS ?? "")
  .split(",")
  .map((email) => email.trim().toLowerCase())
  .filter(Boolean);

export const { handlers, signIn, signOut, auth } = NextAuth({
  trustHost: true,
  secret: process.env.NEXTAUTH_SECRET ?? process.env.AUTH_SECRET,
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
  ],
  pages: { signIn: "/login" },
  callbacks: {
    signIn({ user }) {
      if (allowedEmails.length === 0) return true;
      return !!user.email && allowedEmails.includes(user.email.toLowerCase());
    },
  },
});
