"use client";

import { Empty, ErrorState, Loading, PageHeader } from "@/components/states";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { InsightsResponse, RecommendationsResponse } from "@/lib/types";
import { useApi } from "@/lib/use-api";

export default function InsightsPage() {
  const insights = useApi<InsightsResponse>("/insights");
  const recs = useApi<RecommendationsResponse>("/recommendations");

  return (
    <div className="max-w-2xl space-y-10">
      <section>
        <PageHeader title="Insights" description="What changed in how you work." />
        {insights.loading ? (
          <Loading />
        ) : insights.error ? (
          <ErrorState message={insights.error} />
        ) : !insights.data || insights.data.count === 0 ? (
          <Empty message="No insights yet." />
        ) : (
          <div className="space-y-3">
            {insights.data.insights.map((i) => (
              <Card key={i.id}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">{i.title}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">{i.description}</CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold tracking-tight">Recommendations</h2>
        {recs.loading ? (
          <Loading />
        ) : recs.error ? (
          <ErrorState message={recs.error} />
        ) : !recs.data || recs.data.count === 0 ? (
          <Empty message="No recommendations yet." />
        ) : (
          <div className="space-y-3">
            {recs.data.recommendations.map((r) => (
              <Card key={r.id}>
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between gap-3 text-base">
                    {r.title}
                    <Badge>{r.priority}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-1 text-sm text-muted-foreground">
                  <p>{r.reason}</p>
                  <p className="text-foreground">Expected impact: {r.expected_impact}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
