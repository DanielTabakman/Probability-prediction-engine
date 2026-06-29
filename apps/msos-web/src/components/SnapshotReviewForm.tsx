"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  POST_MORTEM_STATUSES,
  type ReviewStatus,
  reviewStatusLabel,
  type SnapshotReviewRow,
} from "@/lib/snapshotReview";

type Props = {
  snapshotId: string;
  initialReview: SnapshotReviewRow | null;
};

export function SnapshotReviewForm({ snapshotId, initialReview }: Props) {
  const router = useRouter();
  const initialStatus =
    initialReview?.reviewStatus && POST_MORTEM_STATUSES.includes(initialReview.reviewStatus)
      ? initialReview.reviewStatus
      : POST_MORTEM_STATUSES[0];

  const [reviewStatus, setReviewStatus] = useState<ReviewStatus>(initialStatus);
  const [outcomeNotes, setOutcomeNotes] = useState(initialReview?.outcomeNotes ?? "");
  const [paperTag, setPaperTag] = useState(initialReview?.paperTag ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setSaved(false);
    try {
      const response = await fetch(`/api/snapshots/${encodeURIComponent(snapshotId)}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          review_status: reviewStatus,
          outcome_notes: outcomeNotes.trim() || null,
          paper_tag: paperTag.trim() || null,
        }),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) {
        setError(payload.error ?? "Could not save review");
        return;
      }
      setSaved(true);
      router.refresh();
    } catch {
      setError("Could not save review — try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="snapshot-review-form" onSubmit={(event) => void handleSubmit(event)}>
      <div className="panel-head compact">
        <h2>Post-mortem</h2>
        <span className="tag">Review</span>
      </div>
      <p className="panel-sub">
        Record whether this saved read held up — research and paper workflows only, not trade advice.
      </p>

      <label className="demo-debrief-field" htmlFor="review-status">
        <span>Outcome</span>
        <select
          id="review-status"
          value={reviewStatus}
          onChange={(event) => setReviewStatus(event.target.value as ReviewStatus)}
          disabled={busy}
        >
          {POST_MORTEM_STATUSES.map((status) => (
            <option key={status} value={status}>
              {reviewStatusLabel(status)}
            </option>
          ))}
        </select>
      </label>

      <label className="demo-debrief-field demo-debrief-notes" htmlFor="outcome-notes">
        <span>Notes (optional)</span>
        <textarea
          id="outcome-notes"
          rows={4}
          value={outcomeNotes}
          onChange={(event) => setOutcomeNotes(event.target.value)}
          disabled={busy}
          placeholder="What happened vs what you expected?"
        />
      </label>

      <label className="demo-debrief-field" htmlFor="paper-tag">
        <span>Paper tag (optional)</span>
        <input
          id="paper-tag"
          type="text"
          maxLength={120}
          value={paperTag}
          onChange={(event) => setPaperTag(event.target.value)}
          disabled={busy}
          placeholder="e.g. width-trade rehearsal"
        />
      </label>

      {initialReview?.reviewHorizonRef ? (
        <p className="micro">Horizon ref: {initialReview.reviewHorizonRef}</p>
      ) : null}

      {error ? (
        <p className="panel-sub degraded-feed-note" role="alert">
          {error}
        </p>
      ) : null}
      {saved ? (
        <p className="panel-sub" role="status">
          Review saved — Command Center counts refresh on next load.
        </p>
      ) : null}

      <div className="demo-debrief-actions">
        <button type="submit" className="btn slim primary" disabled={busy}>
          {busy ? "Saving…" : "Save review"}
        </button>
      </div>
    </form>
  );
}
