"use client";

import Link from "next/link";

import { WebFeedbackForm } from "@/components/WebFeedbackForm";

export function StrategyLabFeedbackStrip() {
  return (
    <section className="panel feedback-strip" aria-label="Share feedback">
      <details className="feedback-strip-details">
        <summary className="feedback-strip-summary">
          Share quick feedback
          <span className="micro"> ~2 min · helps improve the demo</span>
        </summary>
        <div className="feedback-strip-body">
          <WebFeedbackForm source="strategy_lab_compact" variant="compact" showProfileField={false} />
          <p className="micro">
            Full form: <Link href="/feedback">/feedback</Link>
          </p>
        </div>
      </details>
    </section>
  );
}
