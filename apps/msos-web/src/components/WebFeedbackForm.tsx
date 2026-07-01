"use client";

import Link from "next/link";
import { useCallback, useState } from "react";

import {
  CONFUSION_CATEGORIES,
  LIKERT_LABELS,
  LIKERT_MAX,
  LIKERT_MIN,
  type FeedbackSubmitPayload,
} from "@/lib/feedbackForm";

type SubmitState = "idle" | "sending" | "sent" | "error";

export type WebFeedbackFormProps = {
  source: string;
  variant?: "full" | "compact";
  initialProfile?: string;
  initialComprehension?: "Y" | "N" | "";
  initialReturnIntent?: "Y" | "N" | "";
  initialNotes?: string;
  showProfileField?: boolean;
  skipHref?: string;
  skipLabel?: string;
};

export function WebFeedbackForm({
  source,
  variant = "full",
  initialProfile = "",
  initialComprehension = "",
  initialReturnIntent = "",
  initialNotes = "",
  showProfileField,
  skipHref,
  skipLabel = "Skip for now",
}: WebFeedbackFormProps) {
  const [profile, setProfile] = useState(initialProfile);
  const [confusionCategory, setConfusionCategory] = useState<string>(CONFUSION_CATEGORIES[7]);
  const [usefulness, setUsefulness] = useState(3);
  const [repeatUseIntent, setRepeatUseIntent] = useState(3);
  const [objections, setObjections] = useState(initialNotes);
  const [state, setState] = useState<SubmitState>("idle");

  const profileVisible = showProfileField ?? variant === "full";

  const handleSubmit = useCallback(async () => {
    setState("sending");
    const payload: FeedbackSubmitPayload = {
      source,
      confusion_category: confusionCategory,
      usefulness,
      repeat_use_intent: repeatUseIntent,
      objections_text: objections.trim() || undefined,
    };
    if (profileVisible && profile.trim()) {
      payload.tester_profile = profile.trim();
    }
    if (initialComprehension) payload.comprehension = initialComprehension;
    if (initialReturnIntent) payload.return_intent = initialReturnIntent;

    try {
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        setState("error");
        return;
      }
      setState("sent");
    } catch {
      setState("error");
    }
  }, [
    confusionCategory,
    initialComprehension,
    initialReturnIntent,
    objections,
    profile,
    profileVisible,
    repeatUseIntent,
    source,
    usefulness,
  ]);

  if (state === "sent") {
    return (
      <div className="feedback-form">
        <p className="feedback-success" role="status">
          Thanks — your feedback goes straight to the team and helps us improve the demo for new
          traders.
        </p>
        {skipHref ? (
          <div className="demo-debrief-actions">
            <Link href={skipHref} className="btn slim primary">
              {skipLabel}
            </Link>
          </div>
        ) : null}
      </div>
    );
  }

  const rootClass = variant === "compact" ? "feedback-form feedback-form-compact" : "feedback-form";

  return (
    <div className={rootClass}>
      {profileVisible ? (
        <label className="demo-debrief-field">
          <span>Your role (optional)</span>
          <input
            type="text"
            value={profile}
            placeholder="e.g. BTC options trader"
            onChange={(event) => setProfile(event.target.value)}
          />
        </label>
      ) : null}

      <label className="demo-debrief-field">
        <span>What best describes your experience?</span>
        <select
          value={confusionCategory}
          onChange={(event) => setConfusionCategory(event.target.value)}
        >
          {CONFUSION_CATEGORIES.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </label>

      <label className="demo-debrief-field">
        <span>How useful was this for understanding the market read?</span>
        <input
          type="range"
          min={LIKERT_MIN}
          max={LIKERT_MAX}
          step={1}
          value={usefulness}
          onChange={(event) => setUsefulness(Number(event.target.value))}
        />
        <span className="micro">
          {usefulness} — {LIKERT_LABELS[usefulness] ?? usefulness}
        </span>
      </label>

      <label className="demo-debrief-field">
        <span>Would you want to use this again?</span>
        <input
          type="range"
          min={LIKERT_MIN}
          max={LIKERT_MAX}
          step={1}
          value={repeatUseIntent}
          onChange={(event) => setRepeatUseIntent(Number(event.target.value))}
        />
        <span className="micro">
          {repeatUseIntent} — {LIKERT_LABELS[repeatUseIntent] ?? repeatUseIntent}
        </span>
      </label>

      <label className="demo-debrief-field demo-debrief-notes">
        <span>Anything confusing or missing? (optional)</span>
        <textarea
          rows={variant === "compact" ? 2 : 3}
          value={objections}
          placeholder="Plain language — no account required."
          onChange={(event) => setObjections(event.target.value)}
        />
      </label>

      {state === "error" ? (
        <p className="modal-error" role="alert">
          Could not save — try again in a moment.
        </p>
      ) : null}

      <div className="demo-debrief-actions">
        {skipHref ? (
          <Link href={skipHref} className="btn slim">
            {skipLabel}
          </Link>
        ) : null}
        <button
          type="button"
          className="btn slim primary"
          disabled={state === "sending"}
          onClick={() => void handleSubmit()}
        >
          {state === "sending" ? "Sending…" : "Submit feedback"}
        </button>
      </div>
    </div>
  );
}
