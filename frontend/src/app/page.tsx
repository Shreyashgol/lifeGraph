import { redirect } from "next/navigation";

export default function Home() {
  // Middleware gates access; authenticated users land on the dashboard.
  redirect("/dashboard");
}
