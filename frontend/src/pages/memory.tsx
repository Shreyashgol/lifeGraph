import { Empty, ErrorState, Loading, PageHeader } from "@/components/states";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { MemoryResponse } from "@/lib/types";
import { useApi } from "@/lib/use-api";

export default function MemoryPage() {
  const { data, loading, error } = useApi<MemoryResponse>("/memory");

  return (
    <div className="max-w-2xl">
      <PageHeader title="Memory" description="What LifeGraph has learned about you." />

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error} />
      ) : !data || data.count === 0 ? (
        <Empty message="No memories yet. Keep logging — memory is earned from repeated evidence." />
      ) : (
        <div className="space-y-3">
          {data.memories.map((m) => (
            <Card key={m.id}>
              <CardContent className="space-y-1 py-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-medium">{m.statement}</span>
                  <Badge variant="outline">{m.type}</Badge>
                </div>
                <div className="text-xs text-muted-foreground">
                  {m.status} · {(m.confidence * 100).toFixed(0)}% · {m.evidence_count} observation
                  {m.evidence_count === 1 ? "" : "s"}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
