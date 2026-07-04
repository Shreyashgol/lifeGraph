import { useState } from "react";
import {
  Brain,
  CalendarDays,
  HelpCircle,
  Lightbulb,
  PencilLine,
  Sparkles,
} from "lucide-react";

import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";

const STEPS = [
  {
    icon: PencilLine,
    title: "1. Log your activities",
    body: "On the Log Activity page, write what you did in plain language — “Worked on the API for 2 hours”, “Team standup”, “Went for a run”. LifeGraph structures each entry automatically.",
  },
  {
    icon: CalendarDays,
    title: "2. Build your day",
    body: "Your entries flow into the Timeline, grouped into sessions. The Dashboard shows live stats: focused minutes, activities, and context switches.",
  },
  {
    icon: Sparkles,
    title: "3. Generate a daily summary",
    body: "Open Summary and pick a day on the calendar, then hit Generate. LifeGraph analyzes that day and writes an end-of-day review with insights and recommendations.",
  },
  {
    icon: Lightbulb,
    title: "4. Review insights & recommendations",
    body: "Each summary explains what changed in your behaviour and suggests personalized next steps — grounded in your own history, never generic advice.",
  },
  {
    icon: Brain,
    title: "5. Watch your Memory grow",
    body: "Over time, repeated evidence becomes lasting Memory about your goals, routines, and preferences — making every future summary sharper.",
  },
];

/** "How to use" trigger + walkthrough modal for the dashboard header. */
export function HowToUse() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
        <HelpCircle className="mr-2 h-4 w-4" />
        How to use
      </Button>

      <Modal open={open} onClose={() => setOpen(false)} title="How LifeGraph works">
        <p className="mb-5 text-sm text-muted-foreground">
          LifeGraph turns what you do each day into a personal intelligence engine.
          Five steps get you the full picture:
        </p>
        <ol className="space-y-4">
          {STEPS.map(({ icon: Icon, title, body }) => (
            <li key={title} className="flex gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                <Icon className="h-4 w-4" />
              </span>
              <div>
                <div className="text-sm font-semibold">{title}</div>
                <p className="mt-0.5 text-sm leading-relaxed text-muted-foreground">{body}</p>
              </div>
            </li>
          ))}
        </ol>
        <div className="mt-6 flex justify-end">
          <Button onClick={() => setOpen(false)}>Got it</Button>
        </div>
      </Modal>
    </>
  );
}
