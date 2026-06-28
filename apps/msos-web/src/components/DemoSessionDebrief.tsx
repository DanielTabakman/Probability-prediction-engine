"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "msos.demo.debrief.draft.v1";

export type DemoDebriefDraft = {
  profile: string;
  clarity: "Y" | "N" | "";
  returnAgain: "Y" | "N" | "";
  asset: string;
  notes: string;
};

const EMPTY: DemoDebriefDraft = {
  profile: "",
  clarity: "",
  returnAgain: "",
  asset: "BTC",
  notes: "",
};

function loadDraft(): DemoDebriefDraft {
  if (typeof window === "undefined") return EMPTY;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return EMPTY;
    const parsed = JSON.parse(raw) as Partial<DemoDebriefDraft>;
    return { ...EMPTY, ...parsed };
  } catch {
    return EMPTY;
  }
}

function saveDraft(draft: DemoDebriefDraft): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
  } catch {
    /* ignore */
  }
}

function buildLogCommand(draft: DemoDebriefDraft): string {
  const parts = [
    "log_demo_session.cmd",
    `--profile "${draft.profile.replace(/"/g, '\\"')}"`,
  ];
  if (draft.clarity) parts.push(`--clarity ${draft.clarity}`);
  if (draft.returnAgain) parts.push(`--return ${draft.returnAgain}`);
  if (draft.asset.trim()) parts.push(`--asset ${draft.asset.trim().toUpperCase()}`);
  if (draft.notes.trim()) parts.push(`--notes "${draft.notes.replace(/"/g, '\\"')}"`);
  return parts.join(" ");
}

function buildMarkdownRow(draft: DemoDebriefDraft): string {
  const date = new Date().toISOString().slice(0, 10);
  const pass = draft.clarity || "—";
  const noteParts = [draft.profile || "tester"];
  if (draft.asset && draft.asset.toUpperCase() !== "BTC") noteParts.push(`asset=${draft.asset.toUpperCase()}`);
  if (draft.returnAgain) noteParts.push(`return=${draft.returnAgain}`);
  if (draft.notes.trim()) noteParts.push(draft.notes.trim());
  return `| ${date} | Demo session (MSOS walkthrough) | ${pass} | ${noteParts.join(" · ")} |`;
}

type DemoSessionDebriefProps = {
  highlight?: boolean;
};

export function DemoSessionDebrief({ highlight = false }: DemoSessionDebriefProps) {
  const [draft, setDraft] = useState<DemoDebriefDraft>(EMPTY);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    setDraft(loadDraft());
  }, []);

  useEffect(() => {
    saveDraft(draft);
  }, [draft]);

  const logCommand = useMemo(() => buildLogCommand(draft), [draft]);
  const markdownRow = useMemo(() => buildMarkdownRow(draft), [draft]);

  const copyText = useCallback(async (label: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(label);
      window.setTimeout(() => setCopied(null), 2000);
    } catch {
      setCopied("error");
    }
  }, []);

  return (
    <section
      className={`panel demo-debrief${highlight ? " demo-debrief-highlight" : ""}`}
      aria-label="Log this session"
    >
      <div className="panel-head">
        <h2>Log this session</h2>
        <div className="panel-sub">
          60 seconds after a demo — capture what worked. Copy the row or run the command on your
          desktop repo.
        </div>
      </div>

      <div className="demo-debrief-grid">
        <label className="demo-debrief-field">
          <span>Who watched</span>
          <input
            type="text"
            value={draft.profile}
            placeholder="e.g. BTC options trader, fund PM"
            onChange={(e) => setDraft({ ...draft, profile: e.target.value })}
          />
        </label>
        <label className="demo-debrief-field">
          <span>Primary asset shown</span>
          <input
            type="text"
            value={draft.asset}
            placeholder="BTC, ETH, NVDA"
            onChange={(e) => setDraft({ ...draft, asset: e.target.value })}
          />
        </label>
        <fieldset className="demo-debrief-field">
          <legend>Understood chart / disagreement?</legend>
          <label>
            <input
              type="radio"
              name="clarity"
              checked={draft.clarity === "Y"}
              onChange={() => setDraft({ ...draft, clarity: "Y" })}
            />{" "}
            Yes
          </label>
          <label>
            <input
              type="radio"
              name="clarity"
              checked={draft.clarity === "N"}
              onChange={() => setDraft({ ...draft, clarity: "N" })}
            />{" "}
            No
          </label>
        </fieldset>
        <fieldset className="demo-debrief-field">
          <legend>Would open again this week?</legend>
          <label>
            <input
              type="radio"
              name="returnAgain"
              checked={draft.returnAgain === "Y"}
              onChange={() => setDraft({ ...draft, returnAgain: "Y" })}
            />{" "}
            Yes
          </label>
          <label>
            <input
              type="radio"
              name="returnAgain"
              checked={draft.returnAgain === "N"}
              onChange={() => setDraft({ ...draft, returnAgain: "N" })}
            />{" "}
            No
          </label>
        </fieldset>
        <label className="demo-debrief-field demo-debrief-notes">
          <span>Friction / quotes (optional)</span>
          <textarea
            rows={3}
            value={draft.notes}
            placeholder="e.g. lost NVDA after confirm; wanted replay scrubber"
            onChange={(e) => setDraft({ ...draft, notes: e.target.value })}
          />
        </label>
      </div>

      <div className="demo-debrief-actions">
        <button
          type="button"
          className="btn slim primary"
          disabled={!draft.profile.trim()}
          onClick={() => void copyText("row", markdownRow)}
        >
          {copied === "row" ? "Copied row" : "Copy validation row"}
        </button>
        <button
          type="button"
          className="btn slim"
          disabled={!draft.profile.trim()}
          onClick={() => void copyText("cmd", logCommand)}
        >
          {copied === "cmd" ? "Copied command" : "Copy log command"}
        </button>
      </div>

      <pre className="demo-debrief-preview micro" aria-live="polite">
        {markdownRow}
      </pre>
      <p className="micro">
        Desktop: paste command in repo root, or run{" "}
        <code>python scripts/log_demo_session.py --append-validation-md …</code>. See{" "}
        <Link href="/strategy-lab">Strategy Lab</Link> to replay the tour.
      </p>
    </section>
  );
}
