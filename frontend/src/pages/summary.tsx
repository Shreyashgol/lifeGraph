import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CalendarPlus, Lightbulb, Target } from "lucide-react";

import { GenerateAnalysisButton } from "@/components/generate-analysis-button";
import { Markdown } from "@/components/markdown";
import { SummaryCalendar } from "@/components/summary-calendar";
import { ErrorState, Loading } from "@/components/states";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatLong, isFuture, todayKey } from "@/lib/dates";
import type {
  InsightView,
  RecommendationView,
  SummaryCalendarResponse,
  SummaryResponse,
} from "@/lib/types";
import { useApi } from "@/lib/use-api";

const PRIORITY_STYLES: Record<string, string> = {
  Critical: "bg-destructive text-destructive-foreground",
  High: "bg-amber-500 text-white",
  Medium: "bg-secondary text-secondary-foreground",
  Low: "bg-muted text-muted-foreground",
};

export default function SummaryPage() {
  const [selected, setSelected] = useState<string>(todayKey);
  const dates = useApi<SummaryCalendarResponse>("/summary/dates");
  const detail = useApi<SummaryResponse>(`/summary?date=${selected}`);

  const summaryDates = useMemo(
    () => new Set(dates.data?.summary_dates ?? []),
    [dates.data],
  );
  const activityDates = useMemo(
    () => new Set(dates.data?.activity_dates ?? []),
    [dates.data],
  );

  function refresh() {
    detail.reload();
    dates.reload();
  }

  return (
    <div className="max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Daily Summary</h1>
        <p className="text-muted-foreground">
          Pick any day to read its AI review — or generate one on the spot.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="lg:sticky lg:top-6 lg:self-start">
          <SummaryCalendar
            selected={selected}
            onSelect={setSelected}
            summaryDates={summaryDates}
            activityDates={activityDates}
          />
        </div>

        <SummaryDetail
          selected={selected}
          detail={detail}
          hasActivity={activityDates.has(selected)}
          onGenerated={refresh}
        />
      </div>
    </div>
  );
}

function SummaryDetail({
  selected,
  detail,
  hasActivity,
  onGenerated,
}: {
  selected: string;
  detail: ReturnType<typeof useApi<SummaryResponse>>;
  hasActivity: boolean;
  onGenerated: () => void;
}) {
  const { data, loading, error } = detail;
  const isToday = selected === todayKey();
  const future = isFuture(selected);

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <h2 className="text-lg font-semibold">{formatLong(selected)}</h2>
        {isToday && <Badge variant="secondary">Today</Badge>}
      </div>

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error} />
      ) : data ? (
        <ExistingSummary data={data} selected={selected} onGenerated={onGenerated} />
      ) : future ? (
        <EmptyCard message="This day hasn't happened yet." />
      ) : hasActivity ? (
        <EmptyCard message="No summary for this day yet.">
          <GenerateAnalysisButton
            date={selected}
            label="Generate this day's summary"
            onDone={onGenerated}
          />
        </EmptyCard>
      ) : (
        <EmptyCard message="No activity logged on this day.">
          <Link to="/activity" className="text-sm text-primary underline">
            Log an activity &rarr;
          </Link>
        </EmptyCard>
      )}
    </div>
  );
}

function ExistingSummary({
  data,
  selected,
  onGenerated,
}: {
  data: SummaryResponse;
  selected: string;
  onGenerated: () => void;
}) {
  const minutes = Number(data.metrics?.total_duration ?? 0);
  const activities = Number(data.metrics?.activities ?? 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <Metric label="Focused minutes" value={minutes} />
        <Metric label="Activities" value={activities} />
        <div className="ml-auto">
          <GenerateAnalysisButton
            date={selected}
            label="Regenerate"
            onDone={onGenerated}
          />
        </div>
      </div>

      <Card>
        <CardContent className="py-6">
          <Markdown>{data.overview}</Markdown>
        </CardContent>
      </Card>

      {data.insights.length > 0 && (
        <Section icon={<Lightbulb className="h-4 w-4" />} title="Insights">
          <div className="space-y-3">
            {data.insights.map((i) => (
              <InsightRow key={i.id} insight={i} />
            ))}
          </div>
        </Section>
      )}

      {data.recommendations.length > 0 && (
        <Section icon={<Target className="h-4 w-4" />} title="Recommendations">
          <div className="space-y-3">
            {data.recommendations.map((r) => (
              <RecommendationRow key={r.id} rec={r} />
            ))}
          </div>
        </Section>
      )}

      {data.tomorrow_focus && (
        <Section icon={<CalendarPlus className="h-4 w-4" />} title="Tomorrow's focus">
          <Card>
            <CardContent className="py-4">
              <Markdown>{data.tomorrow_focus}</Markdown>
            </CardContent>
          </Card>
        </Section>
      )}
    </div>
  );
}

function Section({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section>
      <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-muted-foreground">
        {icon}
        {title}
      </h3>
      {children}
    </section>
  );
}

function InsightRow({ insight }: { insight: InsightView }) {
  return (
    <Card>
      <CardContent className="py-4">
        <div className="font-medium">{insight.title}</div>
        <p className="mt-1 text-sm text-muted-foreground">{insight.description}</p>
      </CardContent>
    </Card>
  );
}

function RecommendationRow({ rec }: { rec: RecommendationView }) {
  return (
    <Card>
      <CardContent className="py-4">
        <div className="flex items-start justify-between gap-2">
          <div className="font-medium">{rec.title}</div>
          <Badge className={PRIORITY_STYLES[rec.priority] ?? PRIORITY_STYLES.Low}>
            {rec.priority}
          </Badge>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">{rec.reason}</p>
        {rec.expected_impact && (
          <p className="mt-2 text-sm">
            <span className="font-medium text-foreground">Expected impact: </span>
            <span className="text-muted-foreground">{rec.expected_impact}</span>
          </p>
        )}
      </CardContent>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border bg-card px-4 py-3">
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-xs text-muted-foreground">{label}</div>
    </div>
  );
}

function EmptyCard({
  message,
  children,
}: {
  message: string;
  children?: React.ReactNode;
}) {
  return (
    <Card>
      <CardContent className="flex flex-col items-start gap-3 py-8">
        <p className="text-sm text-muted-foreground">{message}</p>
        {children}
      </CardContent>
    </Card>
  );
}
