"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  expressionFamilies,
  expressionRiskNote,
  optimizationBasis,
  venueRails,
} from "@/data/expressionPlanningFixtures";
import { defaultThesisRecord } from "@/data/thesisConfirmFixtures";
import {
  EXPRESSION_PERSISTENCE_LABEL,
  defaultExpressionRecord,
  loadExpressionRecord,
  saveExpressionRecord,
  statusGridForLifecycle,
  withExpressionLifecycle,
} from "@/lib/expressionPersistence";
import { loadThesisRecord } from "@/lib/thesisPersistence";

export function ExpressionPlanningPanel() {
  const [record, setRecord] = useState(defaultExpressionRecord);
  const [thesisConfirmed, setThesisConfirmed] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const thesis = loadThesisRecord(defaultThesisRecord);
    setThesisConfirmed(thesis.lifecycle === "confirmed");
    setRecord(loadExpressionRecord(defaultExpressionRecord));
    setHydrated(true);
  }, []);

  function simulateExpression() {
    const next = withExpressionLifecycle(record, "simulated");
    setRecord(next);
    saveExpressionRecord(next);
  }

  const statusGrid = statusGridForLifecycle(record.lifecycle);
  const isSimulated = record.lifecycle === "simulated";

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Expression &amp; Execution / Planning</div>
          <h1 className="title">Expression &amp; Execution Planning</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot amber" aria-hidden="true" />
            Order not transmitted
          </span>
          <Link href="/strategy-lab/confirm" className="btn slim">
            Back to thesis
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      {!thesisConfirmed && hydrated ? (
        <div className="panel thesis-gate">
          <h2>Confirm thesis first</h2>
          <p>
            Expression planning opens after thesis confirmation. No live execution or order
            placement on this screen.
          </p>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            Go to thesis confirmation
          </Link>
        </div>
      ) : (
        <section className="exec-layout" aria-label="Expression planning layout">
          <div className="panel">
            <div className="panel-head">
              <div>
                <h2>Expression families</h2>
                <div className="panel-sub">The system explains fit before any venue routing.</div>
              </div>
            </div>
            {expressionFamilies.map((family) => (
              <div
                key={family.id}
                className={`option-row${family.dimmed ? " dimmed" : ""}`}
              >
                <div>
                  <h3>{family.title}</h3>
                  <p>{family.description}</p>
                </div>
                <span
                  className={`tag${family.tagTone === "selected" ? " amber" : ""}${
                    family.tagTone === "excluded" ? " red" : ""
                  }`}
                >
                  {family.tag}
                </span>
              </div>
            ))}
            <div className="side-label rails-label">Eligible rails</div>
            {venueRails.map((venue) => (
              <div key={venue.id} className={`venue${venue.dimmed ? " dimmed" : ""}`}>
                <div>
                  <h3>{venue.title}</h3>
                  <p>{venue.description}</p>
                </div>
                <span className="tag">{venue.tag}</span>
              </div>
            ))}
          </div>

          <div className="panel ticket">
            <div className="route">
              <div className="best">Optimized expression plan</div>
              <h2>{record.planHeadline}</h2>
              <p>{record.planSummary}</p>
              <div className="legs" aria-label="Expression legs">
                {record.legs.map((leg) => (
                  <div key={`${leg.side}-${leg.strike}`} className="leg">
                    <span className={leg.side === "BUY" ? "buy" : "sell"}>{leg.side}</span>
                    <span>{leg.instrument}</span>
                    <span>{leg.strike}</span>
                    <span>{leg.tenor}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="status-grid" aria-label="Lifecycle status">
              {statusGrid.map((cell) => (
                <div key={cell.label} className="status-cell">
                  <div className="k">{cell.label}</div>
                  <div className={`v${cell.tone ? ` ${cell.tone}` : ""}`.trim()}>{cell.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel execution-metrics">
            <div className="panel-head">
              <div>
                <h2>Optimization basis</h2>
                <div className="panel-sub">Fit under selected constraints.</div>
              </div>
            </div>
            {optimizationBasis.map((line) => (
              <div key={line.label} className="line">
                <span>{line.label}</span>
                <strong className={line.tone ?? ""}>{line.value}</strong>
              </div>
            ))}
            <div className="risk-note">{expressionRiskNote}</div>
            <div className="exec-actions">
              <button type="button" className="btn slim" disabled={!hydrated}>
                Monitor without trading
              </button>
              <button
                type="button"
                className="btn slim primary"
                disabled={!hydrated || isSimulated}
                onClick={simulateExpression}
              >
                {isSimulated ? "Expression simulated" : "Simulate expression"}
              </button>
              <button type="button" className="btn slim dark" disabled={!hydrated}>
                Prepare order review
              </button>
            </div>
            {isSimulated ? (
              <p className="micro persistence-note">{EXPRESSION_PERSISTENCE_LABEL}</p>
            ) : null}
          </div>
        </section>
      )}

      <p className="footer-note">
        Research demo — expression planning is sim-only; no live order transmitted
      </p>
    </>
  );
}
