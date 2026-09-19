import type { Metadata } from "next";
import Link from "next/link";

import { MsosLogo } from "@/components/MsosLogo";
import { OptionsMarketReadConsole } from "@/components/OptionsMarketReadConsole";
import styles from "./options-market-read.module.css";

export const metadata: Metadata = {
  title: "Options Market Read | Market Structure OS",
  description: "Ask what the BTC options market is pricing for a date, in ordinary language.",
};

export default function OptionsMarketReadPage() {
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
        <nav aria-label="Options Market Read">
          <span className={styles.environmentBadge}>Testing environment</span>
          <Link href="/options-market-read/help">Help</Link>
        </nav>
      </header>

      <main>
        <section className={styles.hero}>
          <div className={styles.heroCopy}>
            <span className={styles.kicker}>BTC · informational only</span>
            <h1>Ask what the options market is pricing.</h1>
            <p>
              Choose a date or ask in everyday language. You’ll get the likely center, the middle
              range of priced outcomes, and how uncertain this expiry looks beside nearby expiries.
            </p>
          </div>
          <div className={styles.heroBoundary}>
            <strong>This answers one question:</strong>
            <span>“What is the BTC options market pricing for this time?”</span>
            <small>It does not recommend a trade or predict the future.</small>
          </div>
        </section>

        <OptionsMarketReadConsole />
      </main>

      <footer className={styles.footer}>
        <span>Staging preview · BTC only · deterministic output</span>
        <Link href="/options-market-read/api-help">API help</Link>
      </footer>
    </div>
  );
}
