"use client";

import React from "react";

// Minimal, dependency-free Markdown renderer for Grok answers.
// Supports headings, bullet/numbered lists, bold, inline code and paragraphs.

function renderInline(text: string, keyPrefix: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  const regex = /(\*\*[^*]+\*\*|`[^`]+`)/g;

  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let counter = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }

    const token = match[0];

    if (token.startsWith("**")) {
      nodes.push(
        <strong key={`${keyPrefix}-b${counter}`}>{token.slice(2, -2)}</strong>,
      );
    } else {
      nodes.push(
        <code key={`${keyPrefix}-c${counter}`}>{token.slice(1, -1)}</code>,
      );
    }

    lastIndex = regex.lastIndex;
    counter += 1;
  }

  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }

  return nodes;
}

export function Markdown({ content }: { content: string }) {
  const lines = (content || "").split("\n");
  const blocks: React.ReactNode[] = [];

  let paragraph: string[] = [];
  let list: { ordered: boolean; items: string[] } | null = null;
  let key = 0;

  const flushParagraph = () => {
    if (paragraph.length) {
      blocks.push(
        <p key={`p${key++}`}>{renderInline(paragraph.join(" "), `p${key}`)}</p>,
      );
      paragraph = [];
    }
  };

  const flushList = () => {
    if (list && list.items.length) {
      const Tag = list.ordered ? "ol" : "ul";
      blocks.push(
        <Tag key={`l${key++}`}>
          {list.items.map((item, index) => (
            <li key={index}>{renderInline(item, `l${key}-${index}`)}</li>
          ))}
        </Tag>,
      );
    }
    list = null;
  };

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();

    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }

    const heading = /^(#{1,6})\s+(.*)$/.exec(line);

    if (heading) {
      flushParagraph();
      flushList();
      const level = Math.min(heading[1].length, 3);
      const Tag = (`h${level}` as unknown) as "h1" | "h2" | "h3";
      blocks.push(
        <Tag key={`h${key++}`}>
          {renderInline(heading[2], `h${key}`)}
        </Tag>,
      );
      continue;
    }

    const bullet = /^\s*[-*]\s+(.*)$/.exec(line);
    const numbered = /^\s*\d+[.)]\s+(.*)$/.exec(line);

    if (bullet || numbered) {
      flushParagraph();
      const ordered = Boolean(numbered);
      const item = (bullet ? bullet[1] : numbered![1]).trim();

      if (!list || list.ordered !== ordered) {
        flushList();
        list = { ordered, items: [] };
      }

      list.items.push(item);
      continue;
    }

    flushList();
    paragraph.push(line.trim());
  }

  flushParagraph();
  flushList();

  return <div className="prose-answer">{blocks}</div>;
}
