"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  confirmationChecklist,
  defaultThesisRecord,
  lifecycleDisplayId,
  thesisConfirmHeadline,
} from "@/data/thesisConfirmFixtures";
import {
  buildCompareColumnsFromLab,
  buildConfirmChecklist,
  buildThesisDraftFromLab,
  buildThesisRestatement,
} from "@/lib/buildThesisLabContext";
import { loadStoredBeliefTuning, type BeliefTuning } from "@/lib/beliefTuning";
import { fetchDisplayPayloadClient, type DisplayPayload } from "@/lib/ppeDisplayPayload";
import { loadStoredStrategyLabExpiry } from "@/lib/strategyLabExpiry";
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
  const [persistError, setPersistError] = useState<string | null>(null);
  const [displayPayload, setDisplayPayload] = useState<DisplayPayload | null>(null);
  const [tuning, setTuning] = useState<BeliefTuning>(loadStoredBeliefTuning());
  const [expiry, setExpiry] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      const [loaded, payload] = await Promise.all([
        fetchThesisRecord(defaultThesisRecord),
        fetchDisplayPayloadClient(),
      ]);
      const storedExpiry =
        loadStoredStrategyLabExpiry() ||
        payload?.series_by_expiry?.[0]?.expiry_date ||
        loaded.expiryDate ||
        null;
      const storedTuning = loadStoredBeliefTuning();
      const draft = buildThesisDraftFromLab(payload, storedTuning, storedExpiry);
      setDisplayPayload(payload);
      setTuning(storedTuning);
      setExpiry(storedExpiry);
      setRecord({ ...loaded, ...draft, lifecycle: loaded.lifecycle, updatedAt: loaded.updatedAt });
      setHydrated(true);
    })();
  }, []);

  const columns = buildCompareColumnsFromLab(displayPayload, tuning);
  const restatement = buildThesisRestatement(tuning, expiry ?? `${record.horizonDays} days`);
  const checklist = hydrated
    ? buildConfirmChecklist(expiry, Boolean(displayPayload))
    : confirmationChecklist;

  async function persist(nextLifecycle: ThesisLifecycle) {
    const draft = buildThesisDraftFromLab(displayPayload, tuning, expiry);
    const next = withLifecycle(
      {
        ...record,
        ...draft,
        updatedAt: new Date().toISOString(),
      },
      nextLifecycle,
    );
    setRecord(next);
    setPersistError(null);
    const ok = await persistThesisRecord(next);
    if (!ok) {
      setPersistError("Could not save to server — stored locally only.");
    }
  }

  const isConfirmed = record.lifecycle === "confirmed";
  const activeLifecycle = lifecycleDisplayId(record.lifecycle);

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
            {restatement.prefix}{" "}
            <em>{restatement.emphasis}</em> {restatement.suffix}{" "}
            <em>{restatement.horizon}</em>.
          </p>

          {record.disagreementLine ? (
            <p className="panel-sub">{record.disagreementLine}</p>
          ) : null}

          <div className="compare-row" aria-label="Market vs thesis comparison">
            {columns.map((col) => (
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
                {record.instrument} · {expiry ?? `${record.horizonDays} days`}
              </p>
            </div>
          </div>
        </section>

        <aside className="confirm-right">
          <div className="panel">
            <div className="panel-head">
              <div>
                <h2>Before you continue</h2>
                <div className="panel-sub">Two quick checks — no hidden “AI says buy.”</div>
              </div>
            </div>
            {checklist.slice(0, 3).map((item) => (
              <div key={item.id} className="check-row">
                <span className="checkmark" aria-hidden="true">
                  ✓
                </span>
                <span>{item.label}</span>
              </div>
            ))}
          </div>

          <div className="proceed">
            <h3>Next step</h3>
            <p>Plan a paper trade after you confirm — no live orders on this demo.</p>
            <div className="confirm-actions">
              <button
                type="button"
                className="btn slim"
                disabled={!hydrated || isConfirmed}
                onClick={() => void persist("draft")}
              >
                Save draft
              </button>
              <button
                type="button"
                className="btn slim primary"
                disabled={!hydrated || isConfirmed}
                onClick={() => void persist("confirmed")}
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
            <p className="micro persistence-note">{THESIS_PERSISTENCE_LABEL}</p>
            <p className="micro" aria-label="Thesis lifecycle status">
              Status: {activeLifecycle}
            </p>
            {persistError ? (
              <p className="micro degraded-feed-note" role="alert">
                {persistError}
              </p>
            ) : null}
          </div>
        </aside>
      </div>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
