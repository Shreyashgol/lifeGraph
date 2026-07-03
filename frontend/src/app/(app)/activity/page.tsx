"use client";

import { useState } from "react";

import { ErrorState, PageHeader } from "@/components/states";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, apiPost } from "@/lib/api";
import type { ActivityResponse } from "@/lib/types";

export default function ActivityPage() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ActivityResponse | null>(null);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await apiPost<ActivityResponse>("/activity", { activity: text });
      setResult(res);
      setText("");
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 503
          ? "The reasoning engine is unavailable — check GROQ_API_KEY on the backend."
          : "Failed to log activity. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  const activity = result?.activity;

  return (
    <div className="max-w-2xl">
      <PageHeader title="Log Activity" description="Describe what you did in natural language." />

      <form onSubmit={submit} className="space-y-3">
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          placeholder="e.g. Worked on the authentication module for two hours"
        />
        <Button type="submit" disabled={loading || !text.trim()}>
          {loading ? "Understanding…" : "Log activity"}
        </Button>
      </form>

      {error && (
        <div className="mt-4">
          <ErrorState message={error} />
        </div>
      )}

      {activity && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              Understood
              <Badge variant={activity.validated ? "default" : "secondary"}>
                {activity.validated ? "validated" : "unverified"}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div>
              <span className="text-muted-foreground">Category:</span> {activity.category}
            </div>
            {activity.project && (
              <div>
                <span className="text-muted-foreground">Project:</span> {activity.project}
              </div>
            )}
            <div>
              <span className="text-muted-foreground">Duration:</span> {activity.duration} min
            </div>
            <div>
              <span className="text-muted-foreground">Confidence:</span>{" "}
              {(activity.confidence * 100).toFixed(0)}%
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
