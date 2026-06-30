import Link from "next/link";

import type { CommandCenterSummary } from "@/lib/commandCenterSummary";
import { buildCalibrationStrip, type CalibrationStrip } from "@/lib/monitorHistoryFeed";
import type { WorkflowSummary, WorkflowSummaryWorkItem } from "@/lib/msosWorkflowStore";
import { moduleCards, plannedModules } from "@/data/commandCenterFixtures";
import { MSOS_ROUTES } from "@/lib/msosPublicUrls";
import { DEMO_FOOTER, friendlySnapshotFeedMessage } from "@/lib/publicCopy";

type Props = {
  summary: CommandCenterSummary;
  workflow: WorkflowSummary;
};

type ResumeItem = {
  key: string;
  name: string;
  tag: string;
  detail: string;
  tagTone?: string;
  href: string;
};

const RESUME_LIMIT = 2;

function reviewsDueCount(summary: CommandCenterSummary): number {
  const raw = summary.kpis.find((k) => k.label === "Reviews due")?.value ?? "0";
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : 0;
}

function dataTrustLabel(summary: CommandCenterSummary): string {
  if (summary.status === "degraded") return "Saved reads offline";
  if (summary.status === "live") return "Saved reads live";
  if (summary.status === "empty") return "No saved reads yet";
  return "Ready";
}

function heroStatLine(summary: CommandCenterSummary, workflow: WorkflowSummary): string | null {
  const pending = reviewsDueCount(summary);
  if (pending > 0) return `${pending} review${pending === 1 ? "" : "s"} due`;

  if (summary.status === "live") {
    const saved = summary.kpis.find((k) => k.label === "Saved snapshots");
    const total = Number(saved?.value ?? "0");
    if (total > 0) return `${total} saved view${total === 1 ? "" : "s"}`;
  }

  if (workflow.currentWork.length > 0) {
    return `${workflow.currentWork.length} in progress`;
  }

  return null;
}

function resolveHeroPrimary(
  summary: CommandCenterSummary,
  workflow: WorkflowSummary,
  calibration: CalibrationStrip,
): { cta: string; href: string } {
  if (reviewsDueCount(summary) > 0) {
    return { cta: calibration.cta, href: calibration.href };
  }
  if (workflow.currentWork.some((item) => item.tag === "Draft")) {
    return { cta: "Resume in Strategy Lab", href: MSOS_ROUTES.strategyLab };
  }
  if (summary.status === "empty" && workflow.currentWork.length === 0) {
    return { cta: "Open Strategy Lab", href: MSOS_ROUTES.strategyLab };
  }
  return { cta: calibration.cta, href: calibration.href };
}

function buildResumeItems(summary: CommandCenterSummary, workflow: WorkflowSummary): ResumeItem[] {
  const items: ResumeItem[] = [];

  workflow.currentWork.forEach((item: WorkflowSummaryWorkItem, index) => {
    items.push({
      key: `wf-${index}-${item.name}`,
      name: item.name,
      tag: item.tag,
      detail: item.detail,
      tagTone: item.tagTone,
      href: MSOS_ROUTES.strategyLab,
    });
  });

  summary.currentWork.forEach((item) => {
    items.push({
      key: item.snapshotId,
      name: item.name,
      tag: item.tag,
      detail: item.detail,
      tagTone: item.tagTone,
      href: `/monitor/snapshot/${item.snapshotId}`,
    });
  });

  return items.slice(0, RESUME_LIMIT);
}

export function CommandCenterContent({ summary, workflow }: Props) {
  const calibrationStrip = buildCalibrationStrip(summary);
  const heroPrimary = resolveHeroPrimary(summary, workflow, calibrationStrip);
  const heroStat = heroStatLine(summary, workflow);
  const resumeItems = buildResumeItems(summary, workflow);
  const hasResume = resumeItems.length > 0;

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Home</div>
          <h1 className="title">Home</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span
              className={`dot ${summary.status === "degraded" ? "red" : summary.status === "live" ? "teal" : ""}`}
              aria-hidden="true"
            />
            {dataTrustLabel(summary)}
          </span>
        </div>
      </header>

      <section className="command-hero panel compact" aria-label="Your status">
        <div className="command-hero-main">
          <h2>{calibrationStrip.title}</h2>
          <p>{calibrationStrip.body}</p>
          {heroStat ? <p className="command-hero-stat">{heroStat}</p> : null}
          {summary.status === "degraded" ? (
            <p className="command-hero-note" role="status">
              {friendlySnapshotFeedMessage(summary.degradedReason)}
            </p>
          ) : null}
        </div>
        <div className="command-hero-actions">
          <Link href={heroPrimary.href} className="btn slim primary">
            {heroPrimary.cta}
          </Link>
          <Link href={MSOS_ROUTES.history} className="command-hero-secondary">
            History
          </Link>
        </div>
      </section>

      <section className="module-card-grid" aria-label="Open a tool">
        {moduleCards.map((card) => (
          <Link key={card.title} href={card.href} className="module-card panel">
            <div className="module-card-mark" aria-hidden="true">
              {card.mark}
            </div>
            <h2>{card.title}</h2>
            <p>{card.description}</p>
            <span className="module-card-cta btn slim primary">{card.cta}</span>
            {card.live ? <span className="module-card-badge tiny-pill teal">Live</span> : null}
          </Link>
        ))}
      </section>

      <details className="planned-modules panel compact">
        <summary>More modules coming</summary>
        <ul className="planned-modules-list">
          {plannedModules.map((item) => (
            <li key={item.label}>
              <span>{item.label}</span>
              <span className="tag muted">{item.status}</span>
            </li>
          ))}
        </ul>
      </details>

      <section className="command-resume panel" aria-label="Resume">
        <div className="panel-head">
          <div>
            <h2>Resume</h2>
            <div className="panel-sub">Pick up a draft, paper trade, or saved read.</div>
          </div>
          {hasResume ? (
            <Link href={MSOS_ROUTES.monitor} className="command-resume-all">
              See all in Monitor →
            </Link>
          ) : null}
        </div>
        {!hasResume ? (
          <p className="panel-sub command-resume-empty">
            Nothing saved yet — open Strategy Lab and compare your view to the market.
          </p>
        ) : (
          resumeItems.map((item) => (
            <Link key={item.key} href={item.href} className="strategy strategy-link">
              <div className="row">
                <span className="name">{item.name}</span>
                <span className={`tag${item.tagTone ? ` ${item.tagTone}` : ""}`}>{item.tag}</span>
              </div>
              <p>{item.detail}</p>
            </Link>
          ))
        )}
      </section>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
