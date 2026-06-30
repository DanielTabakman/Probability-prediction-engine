import type { Metadata } from "next";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { WebFeedbackForm } from "@/components/WebFeedbackForm";

export const metadata: Metadata = {
  title: "Share feedback | Market Structure OS",
  description:
    "Tell us what worked or confused you on the BTC options research demo — helps improve clarity for new traders.",
};

export default function FeedbackPage() {
  return (
    <AppShell activeNavId="learn">
      <header className="topline">
        <div>
          <div className="crumb">Research preview</div>
          <h1 className="title">Share feedback</h1>
        </div>
        <div className="tools">
          <Link href="/strategy-lab" className="btn slim">
            Back to Strategy Lab
          </Link>
        </div>
      </header>

      <section className="panel">
        <div className="panel-head">
          <h2>Quick feedback (~2 min)</h2>
          <div className="panel-sub">
            Exploration only — not investment advice. No login or email required; responses help us
            improve the demo for options traders.
          </div>
        </div>
        <WebFeedbackForm source="public_feedback" variant="full" />
      </section>

      <p className="footer-note micro">
        Prefer a guided walkthrough?{" "}
        <Link href="/learn?debrief=1">Reflect on your session</Link> or explore{" "}
        <Link href="/strategy-lab">Strategy Lab</Link>.
      </p>
    </AppShell>
  );
}
