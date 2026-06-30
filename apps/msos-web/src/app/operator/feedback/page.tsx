import type { Metadata } from "next";
import Link from "next/link";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { isOperatorIdentity } from "@/lib/operatorAuth";
import { resolveMsosIdentityFromHeaders } from "@/lib/msosIdentityCore";
import { MSOS_ROUTES } from "@/lib/msosPublicUrls";
import { readWebFeedbackRecords } from "@/lib/webFeedback";

export const metadata: Metadata = {
  title: "Feedback inbox | Operator",
  description: "Operator-only view of MSOS web feedback submissions.",
  robots: { index: false, follow: false },
};

function formatWhen(iso: string | undefined): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 19);
}

export default async function OperatorFeedbackPage() {
  const requestHeaders = await headers();
  const email = resolveMsosIdentityFromHeaders(requestHeaders);
  if (!isOperatorIdentity(email)) {
    redirect(MSOS_ROUTES.home);
  }

  const records = await readWebFeedbackRecords(100);
  const avgUse =
    records.length > 0
      ? records.reduce((sum, row) => sum + (row.usefulness ?? 0), 0) / records.length
      : null;
  const avgRepeat =
    records.length > 0
      ? records.reduce((sum, row) => sum + (row.repeat_use_intent ?? 0), 0) / records.length
      : null;

  return (
    <AppShell activeNavId="learn">
      <header className="topline">
        <div>
          <div className="crumb">Operator only</div>
          <h1 className="title">Feedback inbox</h1>
        </div>
        <div className="tools">
          <Link href={MSOS_ROUTES.feedback} className="btn slim">
            Public form
          </Link>
        </div>
      </header>

      <section className="panel">
        <div className="panel-head">
          <h2>Summary</h2>
          <div className="panel-sub">
            {records.length} submission(s)
            {avgUse != null ? ` · avg usefulness ${avgUse.toFixed(1)}/5` : ""}
            {avgRepeat != null ? ` · avg repeat ${avgRepeat.toFixed(1)}/5` : ""}
          </div>
        </div>
        <p className="micro">
          Export: <code>python scripts/ppe_export_web_feedback.py --markdown</code>
        </p>
      </section>

      <section className="panel operator-feedback-table-wrap">
        <div className="panel-head">
          <h2>Recent submissions</h2>
        </div>
        {records.length === 0 ? (
          <p className="bodycopy">No submissions yet — share https://marketstructureos.com/feedback</p>
        ) : (
          <div className="operator-feedback-scroll">
            <table className="operator-feedback-table">
              <thead>
                <tr>
                  <th>When (UTC)</th>
                  <th>Source</th>
                  <th>Profile</th>
                  <th>Comp</th>
                  <th>Return</th>
                  <th>Category</th>
                  <th>Use</th>
                  <th>Repeat</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {records.map((row) => (
                  <tr key={row.id}>
                    <td>{formatWhen(row.created_at_utc)}</td>
                    <td>{row.source}</td>
                    <td>{row.tester_profile ?? "—"}</td>
                    <td>{row.comprehension ?? "—"}</td>
                    <td>{row.return_intent ?? "—"}</td>
                    <td>{row.confusion_category ?? "—"}</td>
                    <td>{row.usefulness ?? "—"}</td>
                    <td>{row.repeat_use_intent ?? "—"}</td>
                    <td>{row.objections_text ?? row.session_note ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </AppShell>
  );
}
