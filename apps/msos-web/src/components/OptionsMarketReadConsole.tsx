"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  parseOptionsMarketQuestion,
  targetDateFromPreset,
  type MarketReadQueryResult,
} from "@/lib/optionsMarketReadQuery";
import styles from "@/app/options-market-read/options-market-read.module.css";

type MarketReadPayload = {
  answer: string;
  as_of: string;
  as_of_display: string;
  asset: string;
  data_status: string;
  disclosures: Record<string, string>;
  effective_target_date: string;
  expiry_offset_days: number;
  expiry_resolution: "exact" | "nearest_before" | "nearest_after";
  interpretation: {
    days_to_expiry: number;
    range_vs_spot_percent: {
      low_percent: number;
      high_percent: number;
      width_percent: number;
    };
    uncertainty_context: {
      rating: string;
      description: string;
    };
  };
  max_expiry_gap_days: number;
  metrics: {
    atm_iv_percent: number;
    implied_forward_price: number;
    median_terminal_price: number;
    median_vs_spot_percent: number;
    middle_50_range: {
      high_price: number;
      low_price: number;
      width: number;
    };
    spot_price: number;
  };
  requested_target_date: string | null;
  resolved_expiry: string;
  ruleset_version: string;
  schema_version: string;
  snapshot_id: string;
};

type ApiError = {
  error?: {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
  };
};

type DisplayPayload = {
  series_by_expiry?: Array<{
    expiry_date?: string;
  }>;
};

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const compactCurrency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 1,
});

const calendarDate = new Intl.DateTimeFormat("en-US", {
  timeZone: "UTC",
  year: "numeric",
  month: "short",
  day: "numeric",
});

function formatDate(value: string): string {
  return calendarDate.format(new Date(`${value}T00:00:00Z`));
}

function formatSignedPercent(value: number, digits = 1): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(digits)}%`;
}

function friendlyApiError(status: number, body: ApiError): string {
  const code = body.error?.code;
  const details = body.error?.details ?? {};
  if (code === "expiry_not_close_enough") {
    const before = typeof details.nearest_before === "string" ? formatDate(details.nearest_before) : null;
    const after = typeof details.nearest_after === "string" ? formatDate(details.nearest_after) : null;
    const alternatives = [before, after].filter(Boolean).join(" or ");
    return `There is no supported BTC options expiry close enough to that date.${alternatives ? ` Try ${alternatives}.` : " Try another future date."}`;
  }
  if (code === "past_target_date") {
    return "That date is before the market snapshot. Choose today or a future date.";
  }
  if (code === "unsupported_asset") {
    return "This testing version supports BTC only.";
  }
  if (status >= 500) {
    return "Fresh market data is temporarily unavailable. Please try again in a moment.";
  }
  return body.error?.message || "The market read could not be loaded for that date.";
}

function rawApiHref(targetDate: string | null): string {
  const params = new URLSearchParams({ asset: "BTC" });
  if (targetDate) params.set("target_date", targetDate);
  return `/v1/options-market-read?${params.toString()}`;
}

export function OptionsMarketReadConsole() {
  const [payload, setPayload] = useState<MarketReadPayload | null>(null);
  const [question, setQuestion] = useState("");
  const [pickedDate, setPickedDate] = useState("");
  const [queryNote, setQueryNote] = useState("Using the API's standard 30-day target.");
  const [inputError, setInputError] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTargetDate, setActiveTargetDate] = useState<string | null>(null);
  const [listedExpiries, setListedExpiries] = useState<string[]>([]);

  async function loadRead(targetDate: string | null, note?: string) {
    setLoading(true);
    setRequestError(null);
    setInputError(null);
    try {
      const response = await fetch(rawApiHref(targetDate), {
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      const body = (await response.json()) as MarketReadPayload | ApiError;
      if (!response.ok || !("answer" in body)) {
        setRequestError(friendlyApiError(response.status, body as ApiError));
        return;
      }
      setPayload(body);
      setActiveTargetDate(targetDate);
      if (note) setQueryNote(note);
      if (targetDate) setPickedDate(targetDate);
    } catch {
      setRequestError("The testing API could not be reached. Please try again shortly.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadRead(null);
    void fetch("/ppe-display-api/display.json?asset=BTC&depth=full", {
      cache: "no-store",
      headers: { Accept: "application/json" },
    })
      .then(async (response) => {
        if (!response.ok) return;
        const display = (await response.json()) as DisplayPayload;
        const expiries = (display.series_by_expiry ?? [])
          .map((row) => row.expiry_date)
          .filter((value): value is string => Boolean(value && /^\d{4}-\d{2}-\d{2}$/.test(value)))
          .sort();
        setListedExpiries([...new Set(expiries)]);
      })
      .catch(() => {
        // The free date picker still works if the optional expiry list is unavailable.
      });
  }, []);

  function useParsedResult(result: MarketReadQueryResult) {
    if (!result.ok) {
      setInputError(result.message);
      return;
    }
    void loadRead(result.targetDate, result.explanation);
  }

  function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!payload) return;
    useParsedResult(parseOptionsMarketQuestion(question, payload.as_of));
  }

  function submitDate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!pickedDate) {
      setInputError("Choose a date first.");
      return;
    }
    if (!payload) return;
    useParsedResult(parseOptionsMarketQuestion(pickedDate, payload.as_of));
  }

  function applyPreset(preset: "default" | "7d" | "90d" | "year-end") {
    if (!payload) return;
    useParsedResult(targetDateFromPreset(preset, payload.as_of));
  }

  const targetSummary = useMemo(() => {
    if (!payload) return null;
    const target = formatDate(payload.effective_target_date);
    const expiry = formatDate(payload.resolved_expiry);
    if (payload.expiry_resolution === "exact") {
      return `Exact listed expiry: ${expiry}`;
    }
    const direction = payload.expiry_offset_days < 0 ? "before" : "after";
    const gap = Math.abs(payload.expiry_offset_days);
    return `You asked about ${target}. The nearest supported expiry is ${expiry}, ${gap} day${gap === 1 ? "" : "s"} ${direction}.`;
  }, [payload]);

  const lowVsSpot = payload?.interpretation.range_vs_spot_percent.low_percent ?? 0;
  const highVsSpot = payload?.interpretation.range_vs_spot_percent.high_percent ?? 0;

  return (
    <div className={styles.console}>
      <section className={styles.askCard} aria-labelledby="ask-heading">
        <div className={styles.sectionEyebrow}>Ask in ordinary language</div>
        <h2 id="ask-heading">What date do you want to understand?</h2>
        <p className={styles.sectionIntro}>
          Ask a simple BTC question. We convert the date into the exact API input and show you what
          was used before displaying the result.
        </p>

        <form className={styles.questionForm} onSubmit={submitQuestion}>
          <label htmlFor="market-question">Your question</label>
          <div className={styles.inputRow}>
            <input
              id="market-question"
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="What is BTC options market pricing for December 25, 2026?"
              autoComplete="off"
              disabled={!payload || loading}
            />
            <button type="submit" disabled={!payload || loading}>
              {loading ? "Loading…" : "Ask"}
            </button>
          </div>
        </form>

        <div className={styles.shortcuts} aria-label="Date shortcuts">
          <span>Quick choices</span>
          <button type="button" onClick={() => applyPreset("default")} disabled={!payload || loading}>
            30-day default
          </button>
          <button type="button" onClick={() => applyPreset("7d")} disabled={!payload || loading}>
            7 days
          </button>
          <button type="button" onClick={() => applyPreset("90d")} disabled={!payload || loading}>
            90 days
          </button>
          <button type="button" onClick={() => applyPreset("year-end")} disabled={!payload || loading}>
            Year-end
          </button>
        </div>

        {listedExpiries.length ? (
          <div className={styles.listedExpiryPicker}>
            <label htmlFor="listed-expiry">Choose an available options expiry</label>
            <select
              id="listed-expiry"
              value=""
              onChange={(event) => {
                const value = event.target.value;
                if (!value || !payload) return;
                setPickedDate(value);
                useParsedResult(parseOptionsMarketQuestion(value, payload.as_of));
              }}
              disabled={!payload || loading}
            >
              <option value="">Select a listed expiry…</option>
              {listedExpiries.map((expiry) => (
                <option key={expiry} value={expiry}>{formatDate(expiry)}</option>
              ))}
            </select>
            <small>These dates map exactly to live contracts in the current snapshot.</small>
          </div>
        ) : null}

        <form className={styles.dateForm} onSubmit={submitDate}>
          <div>
            <label htmlFor="target-date">Or choose any calendar date</label>
            <input
              id="target-date"
              type="date"
              min={payload?.as_of.slice(0, 10)}
              value={pickedDate}
              onChange={(event) => setPickedDate(event.target.value)}
              disabled={!payload || loading}
            />
          </div>
          <button type="submit" disabled={!payload || loading || !pickedDate}>
            Use this date
          </button>
        </form>

        <div className={styles.parseNote} aria-live="polite">
          <span>How we understood it</span>
          <strong>{inputError ?? queryNote}</strong>
        </div>
        <p className={styles.parserBoundary}>
          Supported language includes exact dates, “in 90 days,” “next Friday,” “Christmas,” and
          “year-end.” If a phrase is unclear, we ask for a date instead of guessing.
        </p>
      </section>

      <section className={styles.resultArea} aria-live="polite" aria-busy={loading}>
        {loading && !payload ? (
          <div className={styles.loadingCard}>
            <span className={styles.spinner} aria-hidden="true" />
            Reading the latest BTC options snapshot…
          </div>
        ) : null}

        {requestError ? (
          <div className={styles.errorCard} role="alert">
            <strong>We couldn’t produce that read.</strong>
            <p>{requestError}</p>
          </div>
        ) : null}

        {payload && !requestError ? (
          <div className={loading ? styles.resultLoading : undefined}>
            <div className={styles.resultHeader}>
              <div>
                <div className={styles.sectionEyebrow}>What the options market is saying</div>
                <h2>BTC for {formatDate(payload.resolved_expiry)}</h2>
              </div>
              <span className={styles.freshBadge}>Snapshot: {payload.as_of_display}</span>
            </div>

            <div className={styles.answerCard}>
              <p>{payload.answer}</p>
              <div className={styles.expiryNote}>{targetSummary}</div>
            </div>

            <div className={styles.metricsGrid}>
              <article>
                <span>BTC spot now</span>
                <strong>{currency.format(payload.metrics.spot_price)}</strong>
                <small>At the snapshot time</small>
              </article>
              <article>
                <span>Market’s center</span>
                <strong>{currency.format(payload.metrics.median_terminal_price)}</strong>
                <small>{formatSignedPercent(payload.metrics.median_vs_spot_percent)} vs. spot</small>
              </article>
              <article className={styles.rangeMetric}>
                <span>Middle 50% of priced outcomes</span>
                <strong>
                  {compactCurrency.format(payload.metrics.middle_50_range.low_price)} – {compactCurrency.format(payload.metrics.middle_50_range.high_price)}
                </strong>
                <small>{formatSignedPercent(lowVsSpot)} to {formatSignedPercent(highVsSpot)} vs. spot</small>
              </article>
              <article>
                <span>Priced uncertainty</span>
                <strong>{payload.metrics.atm_iv_percent.toFixed(1)}% IV</strong>
                <small>{payload.interpretation.uncertainty_context.description}</small>
              </article>
            </div>

            <div className={styles.detailGrid}>
              <details>
                <summary>How to read these numbers</summary>
                <div className={styles.detailBody}>
                  <p>
                    <strong>Market’s center</strong> is the median of the options-implied distribution,
                    not a prediction that BTC will finish at exactly that price.
                  </p>
                  <p>
                    <strong>Middle 50%</strong> runs from the 25th to the 75th percentile. Prices outside
                    that interval are still possible.
                  </p>
                  <p>
                    <strong>Implied volatility</strong> describes priced uncertainty, not whether the
                    market is bullish or bearish.
                  </p>
                </div>
              </details>
              <details>
                <summary>Method, freshness, and small print</summary>
                <div className={styles.detailBody}>
                  {Object.values(payload.disclosures).map((disclosure) => (
                    <p key={disclosure}>{disclosure}</p>
                  ))}
                </div>
              </details>
              <details>
                <summary>Technical details</summary>
                <div className={styles.technicalList}>
                  <span>Target date</span><strong>{formatDate(payload.effective_target_date)}</strong>
                  <span>Resolved expiry</span><strong>{formatDate(payload.resolved_expiry)}</strong>
                  <span>Days to expiry</span><strong>{payload.interpretation.days_to_expiry}</strong>
                  <span>Schema</span><strong>{payload.schema_version}</strong>
                  <span>Ruleset</span><strong>{payload.ruleset_version}</strong>
                </div>
              </details>
            </div>

            <div className={styles.resultFooter}>
              <Link href="/options-market-read/help">How this tool works</Link>
              <a href={rawApiHref(activeTargetDate)} target="_blank" rel="noreferrer">
                View the raw API JSON
              </a>
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}
