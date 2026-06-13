import type { Metadata } from "next";
import { headers } from "next/headers";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { listFeedback } from "@/lib/webFeedbackStore";
import { TRADER_PROFILE_LABELS } from "@/lib/webFeedbackTypes";

export const metadata: Metadata = {
  title: "Feedback inbox | MSOS operator",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

function operatorAllowed(emailHeader: string | null): boolean {
  const allowed = (process.env.MSOS_OPERATOR_EMAIL ?? "").trim().toLowerCase();
  if (!allowed) {
    return process.env.NODE_ENV === "development";
  }
  return (emailHeader ?? "").trim().toLowerCase() === allowed;
}

function ynLabel(value: string): string {
  if (value === "yes") return "Y";
  if (value === "no") return "N";
  if (value === "not_yet") return "Not yet";
  return value;
}

export default async function OperatorFeedbackPage() {
  const hdrs = await headers();
  const email = hdrs.get("cf-access-authenticated-user-email");
  if (!operatorAllowed(email)) {
    notFound();
  }

  const rows = listFeedback(100);

  return (
    <AppShell activeNavId="operator-feedback">
      <header className="topline">
        <div>
          <div className="crumb">Operator / Validation</div>
          <h1 className="title">Web feedback inbox</h1>
        </div>
        <span className="pill">
          <span className="dot" aria-hidden="true" />
          {rows.length} recent
        </span>
      </header>

      <section className="panel feedback-inbox">
        <p className="micro">
          Public submissions from <code>/feedback</code> and Strategy Lab. Export with{" "}
          <code>python scripts/ppe_export_web_feedback.py</code> for reality-check sync.
        </p>
        {rows.length === 0 ? (
          <p className="feedback-empty">No submissions yet.</p>
        ) : (
          <div className="feedback-table-wrap">
            <table className="feedback-table">
              <thead>
                <tr>
                  <th>When (UTC)</th>
                  <th>Understood</th>
                  <th>Return</th>
                  <th>Trader profile</th>
                  <th>Note</th>
                  <th>Page</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.id}>
                    <td>{row.created_at_utc.replace("T", " ").replace("Z", "")}</td>
                    <td>{ynLabel(row.understood)}</td>
                    <td>{ynLabel(row.would_return)}</td>
                    <td>{TRADER_PROFILE_LABELS[row.trader_profile] ?? row.trader_profile}</td>
                    <td>{row.note ?? "—"}</td>
                    <td>{row.page_path}</td>
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
