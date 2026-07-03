"use client";

import { Empty, ErrorState, Loading, PageHeader } from "@/components/states";
import { Card, CardContent } from "@/components/ui/card";
import type { SummaryResponse } from "@/lib/types";
import { useApi } from "@/lib/use-api";

export default function SummaryPage() {
  const { data, loading, error } = useApi<SummaryResponse>("/summary");

  return (
    <div className="max-w-3xl">
      <PageHeader title="Daily Summary" description="Your AI-generated end-of-day review." />

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error} />
      ) : !data ? (
        <Empty message="No summary yet. Log activities to generate one." />
      ) : (
        <Card>
          <CardContent className="py-6">
            <article className="whitespace-pre-wrap text-sm leading-relaxed">
              {data.overview}
            </article>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
