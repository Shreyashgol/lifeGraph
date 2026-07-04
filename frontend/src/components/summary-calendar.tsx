import { useState } from "react";
import { CalendarCheck, ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  MONTHS,
  WEEKDAYS,
  addDays,
  fromKey,
  isFuture,
  monthGrid,
  startOfWeek,
  toKey,
  todayKey,
} from "@/lib/dates";
import { cn } from "@/lib/utils";

type View = "week" | "month" | "year";

interface CalendarProps {
  selected: string;
  onSelect: (dateKey: string) => void;
  summaryDates: Set<string>;
  activityDates: Set<string>;
}

const VIEWS: View[] = ["week", "month", "year"];

/**
 * Google-Calendar-style day picker for browsing daily summaries. Days that
 * already have a summary are marked, as are days with logged activity (which
 * can still be summarized). Selecting a day lifts the choice to the parent.
 */
export function SummaryCalendar({
  selected,
  onSelect,
  summaryDates,
  activityDates,
}: CalendarProps) {
  const [view, setView] = useState<View>("month");
  const [cursor, setCursor] = useState<Date>(() => fromKey(selected));
  const today = todayKey();

  function shift(direction: 1 | -1) {
    if (view === "week") setCursor((c) => addDays(c, 7 * direction));
    else if (view === "month")
      setCursor((c) => new Date(c.getFullYear(), c.getMonth() + direction, 1));
    else setCursor((c) => new Date(c.getFullYear() + direction, c.getMonth(), 1));
  }

  function goToday() {
    setCursor(new Date());
    onSelect(today);
  }

  function pick(d: Date) {
    const key = toKey(d);
    if (isFuture(key)) return;
    setCursor(d);
    onSelect(key);
  }

  const label =
    view === "year"
      ? String(cursor.getFullYear())
      : `${MONTHS[cursor.getMonth()]} ${cursor.getFullYear()}`;

  return (
    <div className="rounded-xl border bg-card p-4">
      {/* Toolbar */}
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" aria-label="Previous" onClick={() => shift(-1)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div className="min-w-[9rem] text-center text-sm font-semibold">{label}</div>
          <Button variant="ghost" size="sm" aria-label="Next" onClick={() => shift(1)}>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" className="ml-1" onClick={goToday}>
            Today
          </Button>
        </div>

        <div className="inline-flex rounded-md border p-0.5">
          {VIEWS.map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={cn(
                "rounded px-3 py-1 text-xs font-medium capitalize transition-colors",
                view === v
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      {view === "week" && (
        <WeekView
          cursor={cursor}
          selected={selected}
          today={today}
          summaryDates={summaryDates}
          activityDates={activityDates}
          onPick={pick}
        />
      )}
      {view === "month" && (
        <MonthView
          cursor={cursor}
          selected={selected}
          today={today}
          summaryDates={summaryDates}
          activityDates={activityDates}
          onPick={pick}
        />
      )}
      {view === "year" && (
        <YearView
          cursor={cursor}
          selected={selected}
          today={today}
          summaryDates={summaryDates}
          onPickMonth={(m) => {
            setCursor(new Date(cursor.getFullYear(), m, 1));
            setView("month");
          }}
        />
      )}

      <Legend />
    </div>
  );
}

interface DayViewProps {
  cursor: Date;
  selected: string;
  today: string;
  summaryDates: Set<string>;
  activityDates: Set<string>;
  onPick: (d: Date) => void;
}

function WeekdayHeader() {
  return (
    <div className="mb-1 grid grid-cols-7 text-center text-xs font-medium text-muted-foreground">
      {WEEKDAYS.map((w) => (
        <div key={w} className="py-1">
          {w}
        </div>
      ))}
    </div>
  );
}

function MonthView({ cursor, ...rest }: DayViewProps) {
  const days = monthGrid(cursor);
  return (
    <div>
      <WeekdayHeader />
      <div className="grid grid-cols-7 gap-1">
        {days.map((d) => (
          <DayCell
            key={toKey(d)}
            day={d}
            inMonth={d.getMonth() === cursor.getMonth()}
            {...rest}
          />
        ))}
      </div>
    </div>
  );
}

function WeekView({ cursor, ...rest }: DayViewProps) {
  const start = startOfWeek(cursor);
  const days = Array.from({ length: 7 }, (_, i) => addDays(start, i));
  return (
    <div>
      <WeekdayHeader />
      <div className="grid grid-cols-7 gap-1">
        {days.map((d) => (
          <DayCell key={toKey(d)} day={d} inMonth tall {...rest} />
        ))}
      </div>
    </div>
  );
}

function DayCell({
  day,
  inMonth,
  selected,
  today,
  summaryDates,
  activityDates,
  onPick,
  tall = false,
}: {
  day: Date;
  inMonth: boolean;
  tall?: boolean;
} & Omit<DayViewProps, "cursor">) {
  const key = toKey(day);
  const isSelected = key === selected;
  const isToday = key === today;
  const future = isFuture(key);
  const hasSummary = summaryDates.has(key);
  const hasActivity = activityDates.has(key);

  return (
    <button
      disabled={future}
      onClick={() => onPick(day)}
      aria-label={key}
      aria-pressed={isSelected}
      className={cn(
        "relative flex flex-col items-center justify-start rounded-md border text-sm transition-colors",
        tall ? "h-20 py-2" : "h-12 py-1.5",
        isSelected
          ? "border-primary bg-primary text-primary-foreground"
          : "border-transparent hover:border-border hover:bg-accent",
        !inMonth && "text-muted-foreground/40",
        future && "cursor-not-allowed opacity-40 hover:border-transparent hover:bg-transparent",
        isToday && !isSelected && "ring-1 ring-inset ring-primary/50",
      )}
    >
      <span className={cn("leading-none", isToday && !isSelected && "font-bold")}>
        {day.getDate()}
      </span>
      {(hasSummary || hasActivity) && (
        <span
          className={cn(
            "mt-1 h-1.5 w-1.5 rounded-full",
            hasSummary
              ? isSelected
                ? "bg-primary-foreground"
                : "bg-emerald-500"
              : isSelected
                ? "bg-primary-foreground/60"
                : "bg-muted-foreground/50 ring-1 ring-muted-foreground/40",
          )}
        />
      )}
      {tall && hasSummary && (
        <span
          className={cn(
            "mt-1 text-[10px] font-medium",
            isSelected ? "text-primary-foreground" : "text-emerald-600 dark:text-emerald-400",
          )}
        >
          summary
        </span>
      )}
    </button>
  );
}

function YearView({
  cursor,
  selected,
  today,
  summaryDates,
  onPickMonth,
}: {
  cursor: Date;
  selected: string;
  today: string;
  summaryDates: Set<string>;
  onPickMonth: (month: number) => void;
}) {
  const year = cursor.getFullYear();
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {MONTHS.map((name, m) => {
        const days = monthGrid(new Date(year, m, 1));
        const count = days.filter(
          (d) => d.getMonth() === m && summaryDates.has(toKey(d)),
        ).length;
        return (
          <button
            key={name}
            onClick={() => onPickMonth(m)}
            className="rounded-lg border p-2 text-left transition-colors hover:border-primary hover:bg-accent"
          >
            <div className="mb-1 flex items-center justify-between">
              <span className="text-xs font-semibold">{name}</span>
              {count > 0 && (
                <span className="flex items-center gap-1 text-[10px] text-emerald-600 dark:text-emerald-400">
                  <CalendarCheck className="h-3 w-3" />
                  {count}
                </span>
              )}
            </div>
            <div className="grid grid-cols-7 gap-px">
              {days.map((d) => {
                const key = toKey(d);
                const dim = d.getMonth() !== m;
                return (
                  <span
                    key={key}
                    className={cn(
                      "flex h-3 items-center justify-center rounded-sm text-[8px] leading-none",
                      dim && "opacity-30",
                      summaryDates.has(key) && "bg-emerald-500 text-white",
                      key === selected && "ring-1 ring-primary",
                      key === today && "font-bold underline",
                    )}
                  >
                    {d.getDate()}
                  </span>
                );
              })}
            </div>
          </button>
        );
      })}
    </div>
  );
}

function Legend() {
  return (
    <div className="mt-4 flex flex-wrap items-center gap-4 border-t pt-3 text-xs text-muted-foreground">
      <span className="flex items-center gap-1.5">
        <span className="h-2 w-2 rounded-full bg-emerald-500" /> Has summary
      </span>
      <span className="flex items-center gap-1.5">
        <span className="h-2 w-2 rounded-full bg-muted-foreground/50 ring-1 ring-muted-foreground/40" />
        Activity logged
      </span>
      <span className="flex items-center gap-1.5">
        <span className="h-3 w-3 rounded-full ring-1 ring-inset ring-primary/50" /> Today
      </span>
    </div>
  );
}
