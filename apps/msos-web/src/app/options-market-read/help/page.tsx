import type { Metadata } from "next";
import Link from "next/link";

import { MsosLogo } from "@/components/MsosLogo";
import styles from "../options-market-read.module.css";

export const metadata: Metadata = {
  title: "Options Market Read Help | Market Structure OS",
  description: "How to ask Options Market Read about a BTC date and understand the answer.",
};

const examples = [
  "What is BTC options market pricing for December 25, 2026?",
  "What is the market saying 90 days from now?",
  "BTC next Friday",
  "What does BTC options pricing look like at year-end?",
];

export default function OptionsMarketReadHelpPage() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <Link className={styles.brand} href="/">
          <MsosLogo size={36} />
          <span>
            Market Structure OS
            <small>Options Market Read</small>
          </span>
        </Link>
        <nav aria-label="Options Market Read help">
          <span className={styles.environmentBadge}>Testing environment</span>
          <Link href="/options-market-read">Back to the tool</Link>
        </nav>
      </header>

      <main className={styles.helpMain}>
        <div className={styles.helpIntro}>
          <span className={styles.kicker}>Help</span>
          <h1>How to use Options Market Read</h1>
          <p>
            This tool turns a date into a plain-English summary of what BTC options are pricing.
            It is built to inform—not to recommend a position.
          </p>
          <Link className={styles.primaryLink} href="/options-market-read">
            Open Options Market Read
          </Link>
        </div>

        <div className={styles.helpGrid}>
          <section>
            <span className={styles.stepNumber}>1</span>
            <h2>Ask about a date</h2>
            <p>
              Use the question box, a quick choice, an available-expiry selector, or the calendar
              date picker. Selecting an available expiry gives you an exact contract match.
            </p>
            <ul className={styles.exampleList}>
              {examples.map((example) => <li key={example}>“{example}”</li>)}
            </ul>
          </section>
          <section>
            <span className={styles.stepNumber}>2</span>
            <h2>Confirm the expiry</h2>
            <p>
              Options trade on listed expiry dates. If your date is not listed, the tool uses the
              nearest supported expiry within 14 days and tells you exactly what changed.
            </p>
          </section>
          <section>
            <span className={styles.stepNumber}>3</span>
            <h2>Read the market view</h2>
            <p>
              Start with the two-sentence answer. The cards underneath show spot, the distribution’s
              center, its middle 50%, and annualized at-the-money implied volatility.
            </p>
          </section>
        </div>

        <section className={styles.glossary}>
          <h2>What the terms mean</h2>
          <dl>
            <div>
              <dt>Market’s center</dt>
              <dd>The median of the options-implied terminal distribution—not a price prediction.</dd>
            </div>
            <div>
              <dt>Middle 50%</dt>
              <dd>The interval from the 25th to 75th percentile. Outcomes outside it remain possible.</dd>
            </div>
            <div>
              <dt>Implied volatility (IV)</dt>
              <dd>Annualized priced uncertainty. IV says how much uncertainty is priced, not direction.</dd>
            </div>
            <div>
              <dt>Nearby expiries</dt>
              <dd>The immediately earlier and later listed contracts used for relative uncertainty context.</dd>
            </div>
          </dl>
        </section>

        <section className={styles.boundaryCard}>
          <div>
            <h2>What it can do</h2>
            <ul>
              <li>Summarize BTC options pricing for a selected time.</li>
              <li>Resolve a requested date to a nearby listed expiry.</li>
              <li>Compare priced uncertainty with adjacent expiries.</li>
              <li>Return the same answer for the same market snapshot.</li>
            </ul>
          </div>
          <div>
            <h2>What it cannot do</h2>
            <ul>
              <li>Predict where BTC will finish.</li>
              <li>Call the market bullish or bearish from IV alone.</li>
              <li>Recommend, rank, price, or execute a trade.</li>
              <li>Answer for ETH or other assets in this version.</li>
            </ul>
          </div>
        </section>

        <section className={styles.integrationCard}>
          <div>
            <span className={styles.sectionEyebrow}>For API integrations</span>
            <h2>The human page is an adapter; the JSON contract stays stable.</h2>
            <p>
              Consumers should call <code>GET /v1/options-market-read</code> with optional
              <code> asset=BTC</code> and <code>target_date=YYYY-MM-DD</code>. The language parser
              only helps a person select that date; it does not change the market math.
            </p>
          </div>
          <Link href="/options-market-read/api-help">Open machine-readable API help</Link>
        </section>
      </main>

      <footer className={styles.footer}>
        <span>Research information only · not investment advice</span>
        <Link href="/options-market-read">Back to the tool</Link>
      </footer>
    </div>
  );
}
