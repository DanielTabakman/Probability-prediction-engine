"use client";

import { useCallback, useState } from "react";

import { ActionButton } from "@/components/ActionLink";
import { resolveResearchOfferCta } from "@/lib/researchOfferCta";

type ResearchBetaModalProps = {
  open: boolean;
  onClose: () => void;
};

type SubmitState = "idle" | "sending" | "sent" | "error";

export function ResearchBetaModal({ open, onClose }: ResearchBetaModalProps) {
  const [email, setEmail] = useState("");
  const [note, setNote] = useState("");
  const [state, setState] = useState<SubmitState>("idle");
  const external = resolveResearchOfferCta();

  const handleSubmit = useCallback(async () => {
    setState("sending");
    try {
      const response = await fetch("/api/research-interest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() || undefined, note: note.trim() || undefined }),
      });
      if (!response.ok) {
        setState("error");
        return;
      }
      setState("sent");
      if (external?.url.startsWith("mailto:")) {
        window.location.href = external.url;
      }
    } catch {
      setState("error");
    }
  }, [email, external?.url, note]);

  if (!open) {
    return null;
  }

  return (
    <div className="modal-root" role="presentation">
      <button type="button" className="modal-scrim" aria-label="Close" onClick={onClose} />
      <div className="modal-card" role="dialog" aria-labelledby="research-beta-title">
        <h2 id="research-beta-title">Request research beta access</h2>
        <p className="modal-lead">
          Get early access to advanced belief modes (fat tails, skew overlays, unlimited-upside views) and
          walkthroughs with the team.
        </p>
        {state === "sent" ? (
          <p className="modal-success" role="status">
            Thanks — we logged your interest{external ? " and opened your mail client if configured" : ""}.
          </p>
        ) : (
          <>
            <label className="modal-field">
              <span>Email (optional)</span>
              <input
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@fund.com"
              />
            </label>
            <label className="modal-field">
              <span>What are you trying to express?</span>
              <textarea
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="e.g. unlimited upside above 80k, crash below 50k…"
                rows={3}
              />
            </label>
            {state === "error" ? (
              <p className="modal-error" role="alert">
                Could not save — try again or email us directly.
              </p>
            ) : null}
            <div className="modal-actions">
              <button type="button" className="btn slim" onClick={onClose}>
                Cancel
              </button>
              <ActionButton
                className="btn slim primary"
                disabled={state === "sending"}
                onClick={() => void handleSubmit()}
              >
                {state === "sending" ? "Sending…" : "Send request"}
              </ActionButton>
            </div>
          </>
        )}
        {external?.url.startsWith("https://") ? (
          <p className="modal-foot">
            Or{" "}
            <a href={external.url} target="_blank" rel="noreferrer">
              open the signup link
            </a>
            .
          </p>
        ) : null}
      </div>
    </div>
  );
}
