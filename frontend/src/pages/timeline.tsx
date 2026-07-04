import { Empty, ErrorState, Loading, PageHeader } from "@/components/states";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { TimelineResponse } from "@/lib/types";
import { useApi } from "@/lib/use-api";

export default function TimelinePage() {
  const { data, loading, error } = useApi<TimelineResponse>("/timeline");

  return (
    <div className="max-w-2xl">
      <PageHeader title="Timeline" description="Today's activities, in order." />

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error} />
      ) : !data || data.activities.length === 0 ? (
        <Empty message="No activities logged today." />
      ) : (
        <div className="space-y-3">
          {data.activities.map((a) => (
            <Card key={a.id}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-medium">
                      {a.category}
                      {a.project ? ` · ${a.project}` : ""}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(a.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}{" "}
                      · {a.duration} min
                    </div>
                  </div>
                  <Badge variant={a.validated ? "secondary" : "outline"}>
                    {a.validated ? "validated" : "needs review"}
                  </Badge>
                </div>
                {!a.validated && a.evaluation_reason && (
                  <p className="mt-2 border-t pt-2 text-xs text-amber-600 dark:text-amber-500">
                    <span className="font-medium">Reviewer flagged:</span>{" "}
                    {a.evaluation_reason}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
