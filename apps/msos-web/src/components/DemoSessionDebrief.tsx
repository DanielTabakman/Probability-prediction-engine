"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  CONFUSION_CATEGORIES,
  ynToLikert,
  type FeedbackSubmitPayload,
} from "@/lib/feedbackForm";
import { MSOS_ROUTES } from "@/lib/msosPublicUrls";

const STORAGE_KEY = "msos.demo.debrief.draft.v1";

export type DemoDebriefDraft = {
  profile: string;
  clarity: "Y" | "N" | "";
  returnAgain: "Y" | "N" | "";
  asset: string;
  notes: string;
  confusionCategory: string;
};

const EMPTY: DemoDebriefDraft = {
  profile: "",
  clarity: "",
  returnAgain: "",
  asset: "BTC",
  notes: "",
  confusionCategory: CONFUSION_CATEGORIES[7],
};

type SubmitState = "idle" | "sending" | "sent" | "error";

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
  const [submitState, setSubmitState] = useState<SubmitState>("idle");

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

  const submitFeedback = useCallback(async () => {
    if (!draft.profile.trim()) return;
    setSubmitState("sending");
    const payload: FeedbackSubmitPayload = {
      source: "learn_debrief",
      tester_profile: draft.profile.trim(),
      confusion_category: draft.confusionCategory,
      usefulness: ynToLikert(draft.clarity),
      repeat_use_intent: ynToLikert(draft.returnAgain),
      objections_text: draft.notes.trim() || undefined,
      reality_check_row: buildMarkdownRow(draft),
    };
    if (draft.clarity) payload.comprehension = draft.clarity;
    if (draft.returnAgain) payload.return_intent = draft.returnAgain;
    if (draft.notes.trim()) {
      payload.session_note = `asset=${draft.asset.trim().toUpperCase()}`;
    }

    try {
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        setSubmitState("error");
        return;
      }
      setSubmitState("sent");
    } catch {
      setSubmitState("error");
    }
  }, [draft]);

  return (
    <section
      className={`panel demo-debrief${highlight ? " demo-debrief-highlight" : ""}`}
      aria-label="Log this session"
    >
      <div className="panel-head">
        <h2>Log this session</h2>
        <div className="panel-sub">
          After a demo or solo walkthrough — submit feedback or copy a row for your desktop repo.
        </div>
      </div>

      {submitState === "sent" ? (
        <p className="feedback-success" role="status">
          Feedback saved. Copy the validation row below if you want it in{" "}
          <code>VALIDATION_REALITY_CHECKS.md</code>.
        </p>
      ) : null}

      <div className="demo-debrief-grid">
        <label className="demo-debrief-field">
          <span>Who watched (or solo note)</span>
          <input
            type="text"
            value={draft.profile}
            placeholder="e.g. BTC options trader, solo walkthrough"
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
        <label className="demo-debrief-field">
          <span>Main signal (optional)</span>
          <select
            value={draft.confusionCategory}
            onChange={(e) => setDraft({ ...draft, confusionCategory: e.target.value })}
          >
            {CONFUSION_CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>
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
          disabled={!draft.profile.trim() || submitState === "sending"}
          onClick={() => void submitFeedback()}
        >
          {submitState === "sending" ? "Sending…" : "Submit feedback"}
        </button>
        <button
          type="button"
          className="btn slim"
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
        <Link href={MSOS_ROUTES.feedback} className="btn slim">
          Public feedback form
        </Link>
      </div>

      {submitState === "error" ? (
        <p className="modal-error" role="alert">
          Could not save remotely — use copy buttons or try{" "}
          <Link href={MSOS_ROUTES.feedback}>the public form</Link>.
        </p>
      ) : null}

      <pre className="demo-debrief-preview micro" aria-live="polite">
        {markdownRow}
      </pre>
      <p className="micro">
        Export: <code>python scripts/ppe_export_web_feedback.py --markdown</code> · Operator inbox:{" "}
        <code>/operator/feedback</code> (Cloudflare Access)
      </p>
    </section>
  );
}
