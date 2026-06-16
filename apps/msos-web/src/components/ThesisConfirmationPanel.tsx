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
          <div className="crumb">Strategy Lab / Thesis confirmation</div>
          <h1 className="title">Thesis confirmation</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            MSOS workflow store
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
          <div className="panel-sub">Screen 04 — confirmation narrative</div>
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

          <div className="semantic-lock" aria-label="Reference context">
            <div className="lock">
              <h3>Reference</h3>
              <p>{record.referenceLabel}</p>
            </div>
            <div className="lock">
              <h3>Trust</h3>
              <p>{record.trustLabel} — preview fixture</p>
            </div>
            <div className="lock">
              <h3>Instrument</h3>
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
                <h2>Readiness checks</h2>
                <div className="panel-sub">Honest labels — no hidden authority.</div>
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
              <h2>Thesis lifecycle</h2>
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
            <p>Expression planning opens after confirmation — not live execution.</p>
            <div className="confirm-actions">
              <button
                type="button"
                className="btn slim"
                disabled={!hydrated || isConfirmed}
                onClick={() => persist("draft")}
              >
                Save draft thesis
              </button>
              <button
                type="button"
                className="btn slim primary"
                disabled={!hydrated || isConfirmed}
                onClick={() => persist("confirmed")}
              >
                Confirm thesis
              </button>
            </div>
            {isConfirmed ? (
              <Link href="/strategy-lab/expression" className="btn slim primary proceed-cta">
                Proceed to expression planning
              </Link>
            ) : (
              <span className="btn slim primary proceed-cta muted" title="Confirm thesis first">
                Proceed to expression planning
              </span>
            )}
          </div>
        </aside>
      </div>

      <p className="footer-note">
        Research demo — confirmation uses the MSOS workflow store; no live order transmitted
      </p>
    </>
  );
}
