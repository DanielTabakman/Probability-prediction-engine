"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  thesisCompareColumns,
  thesisConfirmChecklist,
  thesisConfirmHeadline,
  thesisConfirmPageHeader,
  thesisConfirmSidebar,
  thesisContextLocks,
  thesisLifecycleSteps,
  thesisRestatement,
} from "@/content/thesisConfirm";
import { defaultThesisRecord } from "@/data/thesisConfirmFixtures";
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
          <div className="crumb">{thesisConfirmPageHeader.crumb}</div>
          <h1 className="title">{thesisConfirmPageHeader.title}</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {WORKSPACE_SAVED_LABEL}
          </span>
          <Link href="/strategy-lab" className="btn slim">
            {thesisConfirmPageHeader.backToLab}
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
            {thesisCompareColumns.map((col) => (
              <div key={col.label} className="compare-box">
                <div className="k">{col.label}</div>
                <div className={`v ${col.tone ?? ""}`.trim()}>{col.value}</div>
              </div>
            ))}
          </div>

          <div className="semantic-lock" aria-label="Context">
            <div className="lock">
              <h3>{thesisContextLocks.market}</h3>
              <p>{record.referenceLabel}</p>
            </div>
            <div className="lock">
              <h3>{thesisContextLocks.dataQuality}</h3>
              <p>{record.trustLabel}</p>
            </div>
            <div className="lock">
              <h3>{thesisContextLocks.timeframe}</h3>
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
                <h2>{thesisConfirmSidebar.beforeContinueTitle}</h2>
                <div className="panel-sub">{thesisConfirmSidebar.beforeContinueSub}</div>
              </div>
            </div>
            {thesisConfirmChecklist.map((item) => (
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
              <h2>{thesisConfirmSidebar.statusTitle}</h2>
            </div>
            <div className="state-timeline" role="list" aria-label="Thesis lifecycle">
              {thesisLifecycleSteps.map((step) => (
                <div
                  key={step.id}
                  role="listitem"
                  className={`state-step${record.lifecycle === step.id ? " active" : ""}${
                    thesisLifecycleSteps.findIndex((s) => s.id === record.lifecycle) >
                    thesisLifecycleSteps.findIndex((s) => s.id === step.id)
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
            <h3>{thesisConfirmSidebar.nextStepTitle}</h3>
            <p>{thesisConfirmSidebar.nextStepBody}</p>
            <div className="confirm-actions">
              <button
                type="button"
                className="btn slim"
                disabled={!hydrated || isConfirmed}
                onClick={() => persist("draft")}
              >
                {thesisConfirmSidebar.saveDraft}
              </button>
              <button
                type="button"
                className="btn slim primary"
                disabled={!hydrated || isConfirmed}
                onClick={() => persist("confirmed")}
              >
                {thesisConfirmSidebar.confirmView}
              </button>
            </div>
            {isConfirmed ? (
              <Link href="/strategy-lab/expression" className="btn slim primary proceed-cta">
                {thesisConfirmSidebar.planPaperTrade}
              </Link>
            ) : (
              <span
                className="btn slim primary proceed-cta muted"
                title={thesisConfirmSidebar.confirmFirstTitle}
              >
                {thesisConfirmSidebar.planPaperTrade}
              </span>
            )}
          </div>
        </aside>
      </div>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
