import { Fragment, type ReactNode } from "react";

/** Render inline **bold** and `code` within a line of text. */
function renderInline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-foreground">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={i} className="rounded bg-muted px-1 py-0.5 font-mono text-xs">
          {part.slice(1, -1)}
        </code>
      );
    }
    return <Fragment key={i}>{part}</Fragment>;
  });
}

/**
 * Minimal, dependency-free Markdown renderer for the summary format
 * (headings, bullet/numbered lists, bold, code, horizontal rules, paragraphs).
 */
export function Markdown({ children }: { children: string }) {
  const lines = children.replace(/\r\n/g, "\n").split("\n");
  const blocks: ReactNode[] = [];
  let list: string[] = [];
  let key = 0;

  const flushList = () => {
    if (list.length) {
      const items = list;
      blocks.push(
        <ul key={key++} className="mb-3 list-disc space-y-1 pl-5 text-muted-foreground">
          {items.map((item, i) => (
            <li key={i} className="leading-relaxed">
              {renderInline(item)}
            </li>
          ))}
        </ul>,
      );
      list = [];
    }
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      flushList();
      continue;
    }
    if (/^#{1,6}\s/.test(line)) {
      flushList();
      const level = (line.match(/^#+/) as RegExpMatchArray)[0].length;
      const text = line.replace(/^#+\s*/, "");
      blocks.push(
        level <= 2 ? (
          <h2
            key={key++}
            className="mb-2 mt-6 border-b pb-1 text-lg font-semibold tracking-tight first:mt-0"
          >
            {renderInline(text)}
          </h2>
        ) : (
          <h3 key={key++} className="mb-1 mt-4 text-base font-semibold">
            {renderInline(text)}
          </h3>
        ),
      );
      continue;
    }
    if (/^[-*]\s+/.test(line)) {
      list.push(line.replace(/^[-*]\s+/, ""));
      continue;
    }
    if (/^\d+\.\s+/.test(line)) {
      list.push(line.replace(/^\d+\.\s+/, ""));
      continue;
    }
    if (/^-{3,}$/.test(line)) {
      flushList();
      blocks.push(<hr key={key++} className="my-5 border-border" />);
      continue;
    }
    flushList();
    blocks.push(
      <p key={key++} className="mb-3 leading-relaxed text-muted-foreground">
        {renderInline(line)}
      </p>,
    );
  }
  flushList();

  return <div className="text-sm text-foreground">{blocks}</div>;
}
