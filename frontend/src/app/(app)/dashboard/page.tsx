"use client";

import Link from "next/link";

import { PageHeader } from "@/components/states";
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
      <PageHeader title="Dashboard" description="Your day at a glance." />

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
            <Link href="/activity" className="text-sm text-primary underline">
              Record what you did &rarr;
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Latest summary</CardTitle>
          </CardHeader>
          <CardContent>
            {summary.data ? (
              <Link href="/summary" className="text-sm text-primary underline">
                View today&apos;s summary &rarr;
              </Link>
            ) : (
              <p className="text-sm text-muted-foreground">
                No summary yet. Log activities to generate one.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
