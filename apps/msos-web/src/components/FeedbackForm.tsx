"use client";

import { useState } from "react";

import {
  TRADER_PROFILES,
  TRADER_PROFILE_LABELS,
  type TraderProfile,
  type UnderstoodAnswer,
  type WouldReturnAnswer,
} from "@/lib/webFeedbackTypes";

type FeedbackFormProps = {
  pagePath?: string;
  compact?: boolean;
};

export function FeedbackForm({ pagePath = "/feedback", compact = false }: FeedbackFormProps) {
  const [understood, setUnderstood] = useState<UnderstoodAnswer | "">("");
  const [wouldReturn, setWouldReturn] = useState<WouldReturnAnswer | "">("");
  const [traderProfile, setTraderProfile] = useState<TraderProfile | "">("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "done" | "error">("idle");
  const [error, setError] = useState("");

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!understood || !wouldReturn || !traderProfile) {
      setError("Please answer all three questions.");
      setStatus("error");
      return;
    }
    setStatus("submitting");
    setError("");
    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          understood,
          would_return: wouldReturn,
          trader_profile: traderProfile,
          note: note.trim() || undefined,
          page_path: pagePath,
        }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as { error?: string };
        throw new Error(data.error ?? `Request failed (${res.status})`);
      }
      setStatus("done");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Could not submit feedback.");
    }
  }

  if (status === "done") {
    return (
      <div className={`feedback-panel ${compact ? "compact" : ""}`}>
        <div className="feedback-success">
          <span className="tag teal">Thanks</span>
          <p>We read every response. It helps prioritize the research beta.</p>
        </div>
      </div>
    );
  }

  return (
    <form className={`feedback-panel ${compact ? "compact" : ""}`} onSubmit={onSubmit}>
      {!compact && (
        <>
          <h2>Quick feedback</h2>
          <p className="feedback-lead">Three questions — about 30 seconds. No account required.</p>
        </>
      )}

      <fieldset className="feedback-fieldset">
        <legend>I understood what the chart was showing (market-implied vs belief).</legend>
        <div className="feedback-options">
          <label className="feedback-option">
            <input
              type="radio"
              name="understood"
              value="yes"
              checked={understood === "yes"}
              onChange={() => setUnderstood("yes")}
            />
            Yes
          </label>
          <label className="feedback-option">
            <input
              type="radio"
              name="understood"
              value="not_yet"
              checked={understood === "not_yet"}
              onChange={() => setUnderstood("not_yet")}
            />
            Not yet
          </label>
        </div>
      </fieldset>

      <fieldset className="feedback-fieldset">
        <legend>I&apos;d use this again before my next trade or vol decision.</legend>
        <div className="feedback-options">
          <label className="feedback-option">
            <input
              type="radio"
              name="would_return"
              value="yes"
              checked={wouldReturn === "yes"}
              onChange={() => setWouldReturn("yes")}
            />
            Yes
          </label>
          <label className="feedback-option">
            <input
              type="radio"
              name="would_return"
              value="no"
              checked={wouldReturn === "no"}
              onChange={() => setWouldReturn("no")}
            />
            No
          </label>
        </div>
      </fieldset>

      <fieldset className="feedback-fieldset">
        <legend>What do you mainly trade?</legend>
        <select
          className="feedback-select"
          value={traderProfile}
          onChange={(e) => setTraderProfile(e.target.value as TraderProfile)}
          required
        >
          <option value="" disabled>
            Select one
          </option>
          {TRADER_PROFILES.map((id) => (
            <option key={id} value={id}>
              {TRADER_PROFILE_LABELS[id]}
            </option>
          ))}
        </select>
      </fieldset>

      <label className="feedback-fieldset">
        <span className="feedback-legend">Anything confusing? (optional)</span>
        <textarea
          className="feedback-textarea"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          maxLength={300}
          rows={3}
          placeholder="One line is enough."
        />
      </label>

      {error ? <p className="feedback-error">{error}</p> : null}

      <button type="submit" className="btn primary" disabled={status === "submitting"}>
        {status === "submitting" ? "Sending…" : "Submit feedback"}
      </button>
    </form>
  );
}
