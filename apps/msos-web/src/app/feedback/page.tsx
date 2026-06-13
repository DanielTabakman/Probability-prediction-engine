import type { Metadata } from "next";
import Link from "next/link";

import { FeedbackForm } from "@/components/FeedbackForm";
import { PublicNav } from "@/components/PublicNav";

export const metadata: Metadata = {
  title: "Feedback | Market Structure OS",
  description: "Quick feedback on the MSOS research demo — helps prioritize the beta.",
};

export default function FeedbackPage() {
  return (
    <div className="page feedback-page">
      <PublicNav />
      <main className="feedback-main">
        <div className="feedback-intro">
          <div className="crumb">Research beta</div>
          <h1 className="title">Tell us what landed</h1>
          <p className="feedback-lead wide">
            Your answers shape what we build next. We do not ask for email on this form — optional follow-up
            happens only if you reach out.
          </p>
          <Link href="/strategy-lab" className="btn slim dark">
            Back to Strategy Lab
          </Link>
        </div>
        <FeedbackForm pagePath="/feedback" />
      </main>
    </div>
  );
}
