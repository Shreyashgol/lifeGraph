// Local-date helpers for the summary calendar. All keys are `YYYY-MM-DD` in the
// user's local timezone — never use `toISOString()`, which is UTC and can shift
// the day across midnight boundaries.

/** Format a Date as a local `YYYY-MM-DD` key. */
export function toKey(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** Parse a `YYYY-MM-DD` key into a local Date (midnight). */
export function fromKey(key: string): Date {
  const [y, m, d] = key.split("-").map(Number);
  return new Date(y, m - 1, d);
}

/** Today's local date key. */
export function todayKey(): string {
  return toKey(new Date());
}

/** True if the given day key is after today. */
export function isFuture(key: string): boolean {
  return key > todayKey();
}

const LONG = new Intl.DateTimeFormat(undefined, {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric",
});

/** "Friday, July 4, 2026" */
export function formatLong(key: string): string {
  return LONG.format(fromKey(key));
}

/** Add whole days to a date (returns a new Date). */
export function addDays(d: Date, n: number): Date {
  const next = new Date(d);
  next.setDate(next.getDate() + n);
  return next;
}

/** Sunday that starts the week containing `d`. */
export function startOfWeek(d: Date): Date {
  return addDays(d, -d.getDay());
}

/** The 42-day (6-week) grid covering the month of `d`, starting on Sunday. */
export function monthGrid(d: Date): Date[] {
  const first = new Date(d.getFullYear(), d.getMonth(), 1);
  const start = startOfWeek(first);
  return Array.from({ length: 42 }, (_, i) => addDays(start, i));
}

export const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
export const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
