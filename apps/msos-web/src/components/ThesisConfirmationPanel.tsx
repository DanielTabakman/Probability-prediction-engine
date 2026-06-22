"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  compareColumns,
  confirmationChecklist,
  defaultThesisRecord,
  lifecycleSteps,
  thesisConfirmHeadline,
  thesisRestatement,
} from "@/data/thesisConfirmFixtures";
import {
  THESIS_PERSISTENCE_LABEL,
  fetchThesisRecord,
  persistThesisRecord,
  type ThesisLifecycle,
  withLifecycle,
} from "@/lib/thesisPersistence";
import { DEMO_FOOTER, WORKSPACE_SAVED_LABEL } from "@/lib/publicCopy";

export function ThesisConfirmationPanel() {
  const [record, setRecord] = useState(defaultThesisRecord);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    void fetchThesisRecord(defaultThesisRecord).then((loaded) => {
      setRecord(loaded);
      setHydrated(true);
    });
  }, []);

  function persist(nextLifecycle: ThesisLifecycle) {
    const next = withLifecycle(record, nextLifecycle);
    setRecord(next);
    void persistThesisRecord(next);
  }

  const isConfirmed = record.lifecycle === "confirmed";

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Strategy Lab · Confirm</div>
          <h1 className="title">Confirm your view</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {WORKSPACE_SAVED_LABEL}
          </span>
          <Link href="/strategy-lab" className="btn slim">
            Back to lab
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      <div className="confirm-wrap">
        <section className="panel truth">
          <h2 className="question">{thesisConfirmHeadline}</h2>
          <p className="thesis">
            {thesisRestatement.prefix}{" "}
            <em>{thesisRestatement.emphasis}</em> {thesisRestatement.suffix}{" "}
            <em>{thesisRestatement.horizon}</em>.
          </p>

          <div className="compare-row" aria-label="Market vs thesis comparison">
            {compareColumns.map((col) => (
              <div key={col.label} className="compare-box">
                <div className="k">{col.label}</div>
                <div className={`v ${col.tone ?? ""}`.trim()}>{col.value}</div>
              </div>
            ))}
          </div>

          <div className="semantic-lock" aria-label="Context">
            <div className="lock">
              <h3>Market</h3>
              <p>{record.referenceLabel}</p>
            </div>
            <div className="lock">
              <h3>Data quality</h3>
              <p>{record.trustLabel}</p>
            </div>
            <div className="lock">
              <h3>Timeframe</h3>
              <p>
                {record.instrument} · {record.horizonDays} days
              </p>
            </div>
          </div>
        </section>

        <aside className="confirm-right">
          <div className="panel">
            <div className="panel-head">
              <div>
                <h2>Before you continue</h2>
                <div className="panel-sub">Quick sanity checks — no hidden “AI says buy.”</div>
              </div>
            </div>
            {confirmationChecklist.map((item) => (
              <div key={item.id} className="check-row">
                <span className="checkmark" aria-hidden="true">
                  ✓
                </span>
                <span>{item.label}</span>
              </div>
            ))}
          </div>

          <div className="panel">
            <div className="panel-head compact">
              <h2>Status</h2>
            </div>
            <div className="state-timeline" role="list" aria-label="Thesis lifecycle">
              {lifecycleSteps.map((step) => (
                <div
                  key={step.id}
                  role="listitem"
                  className={`state-step${record.lifecycle === step.id ? " active" : ""}${
                    lifecycleSteps.findIndex((s) => s.id === record.lifecycle) >
                    lifecycleSteps.findIndex((s) => s.id === step.id)
                      ? " done"
                      : ""
                  }`}
                >
                  <span className="state-dot" aria-hidden="true" />
                  <span>{step.label}</span>
                </div>
              ))}
            </div>
            <p className="micro persistence-note">{THESIS_PERSISTENCE_LABEL}</p>
          </div>

          <div className="proceed">
            <h3>Next step</h3>
            <p>Plan a paper trade after you confirm — no live orders on this demo.</p>
            <div className="confirm-actions">
              <button
                type="button"
                className="btn slim"
                disabled={!hydrated || isConfirmed}
                onClick={() => persist("draft")}
              >
                Save draft
              </button>
              <button
                type="button"
                className="btn slim primary"
                disabled={!hydrated || isConfirmed}
                onClick={() => persist("confirmed")}
              >
                Confirm view
              </button>
            </div>
            {isConfirmed ? (
              <Link href="/strategy-lab/expression" className="btn slim primary proceed-cta">
                Plan a paper trade
              </Link>
            ) : (
              <span className="btn slim primary proceed-cta muted" title="Confirm your view first">
                Plan a paper trade
              </span>
            )}
          </div>
        </aside>
      </div>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
