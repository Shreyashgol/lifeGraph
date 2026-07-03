"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ErrorState, PageHeader } from "@/components/states";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiPost } from "@/lib/api";
import type { ProfileResponse } from "@/lib/types";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium">{label}</span>
      {children}
    </label>
  );
}

export default function OnboardingPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const [name, setName] = useState("");
  const [occupation, setOccupation] = useState("");
  const [timezone, setTimezone] = useState("");
  const [goals, setGoals] = useState("");
  const [projects, setProjects] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (session?.user?.name) setName(session.user.name);
    try {
      setTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone);
    } catch {
      // Leave blank; the user can fill it in.
    }
  }, [session]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await apiPost<ProfileResponse>("/onboarding", {
        name,
        occupation,
        timezone,
        goals: goals.split(",").map((s) => s.trim()).filter(Boolean),
        active_projects: projects.split(",").map((s) => s.trim()).filter(Boolean),
      });
      router.push("/dashboard");
    } catch {
      setError("Could not save your profile. Ensure goals and timezone are valid, then retry.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg">
      <PageHeader
        title="Complete your profile"
        description="This helps LifeGraph personalize your intelligence."
      />
      <form onSubmit={submit} className="space-y-4">
        <Field label="Name">
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </Field>
        <Field label="Occupation">
          <Input
            value={occupation}
            onChange={(e) => setOccupation(e.target.value)}
            placeholder="AI Engineer"
            required
          />
        </Field>
        <Field label="Timezone (IANA)">
          <Input
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            placeholder="Asia/Kolkata"
            required
          />
        </Field>
        <Field label="Goals (comma-separated)">
          <Input
            value={goals}
            onChange={(e) => setGoals(e.target.value)}
            placeholder="Build AI products, Learn RL"
          />
        </Field>
        <Field label="Active projects (comma-separated)">
          <Input
            value={projects}
            onChange={(e) => setProjects(e.target.value)}
            placeholder="LifeGraph"
          />
        </Field>
        {error && <ErrorState message={error} />}
        <Button type="submit" disabled={loading}>
          {loading ? "Saving…" : "Save profile"}
        </Button>
      </form>
    </div>
  );
}
