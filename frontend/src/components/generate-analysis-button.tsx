import { useState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError, apiPost } from "@/lib/api";
import type { SummaryResponse } from "@/lib/types";

/**
 * Runs the on-demand analysis graph (POST /summary), which generates the day's
 * insights, recommendations, and summary together. Calls `onDone` on success so
 * the page can refresh.
 */
export function GenerateAnalysisButton({
  onDone,
  label = "Generate today's analysis",
  date,
}: {
  onDone?: () => void;
  label?: string;
  /** Day to analyze (`YYYY-MM-DD`); defaults to today when omitted. */
  date?: string;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const query = date ? `?date=${date}` : "";
      await apiPost<SummaryResponse>(`/summary${query}`, {});
      onDone?.();
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setError("Log some activities first, then generate.");
      } else if (err instanceof ApiError && err.status === 429) {
        setError("AI daily token limit reached. Try again later or switch to a lighter model.");
      } else if (err instanceof ApiError && err.status === 503) {
        setError("Reasoning engine unavailable — check GROQ_API_KEY.");
      } else {
        setError("Failed to generate analysis. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <Button onClick={run} disabled={loading}>
        {loading ? "Analyzing…" : label}
      </Button>
      {error && <span className="text-xs text-destructive">{error}</span>}
    </div>
  );
}
