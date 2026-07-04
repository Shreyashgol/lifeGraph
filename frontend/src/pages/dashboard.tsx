import { Link } from "react-router-dom";

import { GenerateAnalysisButton } from "@/components/generate-analysis-button";
import { HowToUse } from "@/components/how-to-use";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { MemoryResponse, SummaryResponse, TimelineResponse } from "@/lib/types";
import { useApi } from "@/lib/use-api";

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{value}</div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const timeline = useApi<TimelineResponse>("/timeline");
  const memory = useApi<MemoryResponse>("/memory");
  const summary = useApi<SummaryResponse>("/summary");
  const t = timeline.data;

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Your day at a glance.</p>
        </div>
        <HowToUse />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Activities today" value={t?.activities.length ?? 0} />
        <Stat label="Focused minutes" value={t?.total_duration ?? 0} />
        <Stat label="Context switches" value={t?.context_switches ?? 0} />
        <Stat label="Memories" value={memory.data?.count ?? 0} />
      </div>

      <div className="mt-8 grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Log an activity</CardTitle>
          </CardHeader>
          <CardContent>
            <Link to="/activity" className="text-sm text-primary underline">
              Record what you did &rarr;
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Today&apos;s analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Insights, recommendations, and the summary are generated on demand
              from the day&apos;s activities.
            </p>
            <GenerateAnalysisButton onDone={summary.reload} />
            {summary.data && (
              <Link to="/summary" className="block text-sm text-primary underline">
                View today&apos;s summary &rarr;
              </Link>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
