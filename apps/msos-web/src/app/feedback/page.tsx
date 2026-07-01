import type { Metadata } from "next";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { WebFeedbackForm } from "@/components/WebFeedbackForm";
import { MSOS_ROUTES } from "@/lib/msosPublicUrls";
import { isTourFeedbackEntry, resolveTourFeedbackReturnTo } from "@/lib/platformTutorial";

export const metadata: Metadata = {
  title: "Share feedback | Market Structure OS",
  description:
    "Tell us what worked or confused you on the BTC options research demo — helps improve clarity for new traders.",
};

type FeedbackPageProps = {
  searchParams: Promise<{ from?: string; returnTo?: string }>;
};

export default async function FeedbackPage({ searchParams }: FeedbackPageProps) {
  const params = await searchParams;
  const query = new URLSearchParams();
  if (params.from) query.set("from", params.from);
  if (params.returnTo) query.set("returnTo", params.returnTo);

  const fromTour = isTourFeedbackEntry(query);
  const returnHref = resolveTourFeedbackReturnTo(query, MSOS_ROUTES.strategyLab);

  return (
    <AppShell activeNavId="learn">
      <header className="topline">
        <div>
          <div className="crumb">Research preview</div>
          <h1 className="title">Share feedback</h1>
        </div>
        <div className="tools">
          <Link href={fromTour ? returnHref : MSOS_ROUTES.strategyLab} className="btn slim">
            {fromTour ? "Skip feedback — go back" : "Back to Strategy Lab"}
          </Link>
        </div>
      </header>

      {fromTour ? (
        <div className="feedback-tour-banner panel" role="status">
          <p>
            Feedback is optional. Skip anytime to return to where you were in Strategy Lab.
          </p>
          <Link href={returnHref} className="btn slim">
            Skip feedback — go back
          </Link>
        </div>
      ) : null}

      <section className="panel">
        <div className="panel-head">
          <h2>{fromTour ? "Quick feedback after the tour" : "Quick feedback (~2 min)"}</h2>
          <div className="panel-sub">
            {fromTour
              ? "Only if you want to — no login or email required."
              : "Exploration only — not investment advice. No login or email required."}
          </div>
        </div>
        <WebFeedbackForm
          source={fromTour ? "tour_feedback" : "public_feedback"}
          variant="full"
          skipHref={fromTour ? returnHref : undefined}
          skipLabel="Skip feedback — go back"
        />
      </section>

      <p className="footer-note micro">
        Prefer a guided walkthrough?{" "}
        <Link href="/learn?debrief=1">Reflect on your session</Link> or explore{" "}
        <Link href="/strategy-lab">Strategy Lab</Link>.
      </p>
    </AppShell>
  );
}
