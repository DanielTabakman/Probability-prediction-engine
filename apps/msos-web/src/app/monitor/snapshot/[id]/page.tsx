import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { SnapshotReviewForm } from "@/components/SnapshotReviewForm";
import { DEMO_FOOTER } from "@/lib/publicCopy";
import { resolveWorkflowOwnerId } from "@/lib/msosWorkflowOwner";
import {
  classificationLine,
  loadSnapshotDetail,
  reviewTagForStatus,
} from "@/lib/snapshotReview";

export const metadata: Metadata = {
  title: "Saved read | Monitor | Market Structure OS",
  description: "Frozen market read and post-mortem review.",
};

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function SnapshotDetailPage({ params }: PageProps) {
  const { id } = await params;
  const ownerId = await resolveWorkflowOwnerId();
  const detail = loadSnapshotDetail(id, ownerId);
  if (!detail) {
    redirect("/monitor");
  }

  const { tag, tone } = reviewTagForStatus(detail.review?.reviewStatus);
  const classification = classificationLine(detail.record);
  const operatorNote =
    typeof detail.record.operator_note === "string" ? detail.record.operator_note.trim() : "";

  return (
    <AppShell activeNavId="monitor">
      <header className="topline">
        <div>
          <div className="crumb">Monitor · Saved read</div>
          <h1 className="title">{detail.summaryLine}</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className={`dot ${tone ?? "amber"}`} aria-hidden="true" />
            {tag}
          </span>
          <Link href="/monitor" className="btn slim">
            Back to monitor
          </Link>
        </div>
      </header>

      <section className="panel paper-trade-detail snapshot-detail">
        <div className="panel-head">
          <div>
            <h2>Frozen summary</h2>
            <div className="panel-sub">
              Persisted market read — not live exchange marks. Paper / research only.
            </div>
          </div>
          <span className="tag teal">Snapshot</span>
        </div>

        <div className="semantic-lock">
          <div className="lock">
            <h3>Expiry</h3>
            <p>{detail.expiry}</p>
          </div>
          <div className="lock">
            <h3>Saved</h3>
            <p>{detail.createdAt}</p>
          </div>
          {classification ? (
            <div className="lock">
              <h3>Category</h3>
              <p>{classification}</p>
            </div>
          ) : null}
        </div>

        {operatorNote ? (
          <div className="panel compact">
            <h3>Operator note</h3>
            <p>{operatorNote}</p>
          </div>
        ) : null}

        {detail.review?.reviewedAtUtc && detail.review.reviewStatus !== "pending" ? (
          <p className="micro">
            Last reviewed {detail.review.reviewedAtUtc} · {tag}
          </p>
        ) : null}

        <SnapshotReviewForm snapshotId={detail.snapshotId} initialReview={detail.review} />
      </section>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </AppShell>
  );
}
