import type { Metadata } from "next";
import Link from "next/link";
import styles from "./daniel.module.css";

export const metadata: Metadata = {
  title: "Daniel Tabakman — Labs | Market Structure OS",
  description:
    "A running shelf of experiments in markets, games, AI, and decision systems by Daniel Tabakman.",
};

export default function DanielLabsPage() {
  return (
    <main className={styles.page}>
      <div className={styles.shell}>
        <nav className={styles.nav} aria-label="Daniel labs navigation">
          <Link className={styles.brand} href="/">
            Market Structure OS
          </Link>
          <a
            className={styles.navLink}
            href="https://github.com/DanielTabakman"
            target="_blank"
            rel="noreferrer"
          >
            GitHub ↗
          </a>
        </nav>

        <header className={styles.hero}>
          <p className={styles.kicker}>Daniel Tabakman · Labs</p>
          <h1>Markets, games, AI, and weird systems.</h1>
          <p className={styles.lede}>
            A running shelf of things I build to understand how people make
            decisions, how markets move, and what happens when software reacts
            to the real world.
          </p>
        </header>

        <section className={styles.section} aria-labelledby="projects-heading">
          <div className={styles.sectionHeading}>
            <h2 id="projects-heading">Selected experiments</h2>
            <span>Playable things first.</span>
          </div>

          <div className={styles.grid}>
            <article className={`${styles.card} ${styles.featured}`}>
              <p className={styles.eyebrow}>Newest experiment · game</p>
              <h3>PitchPacks — Live Sports Autobattler</h3>
              <p>
                Five little fighters automatically beat the hell out of each
                other while events from a real sporting match buff the
                corresponding athlete. Big plays create a small rest-of-match
                upgrade and a much larger burst for the next battle.
              </p>
              <div className={styles.tags}>
                <span>5v5 autobattle</span>
                <span>live-event buffs</span>
                <span>bench swaps</span>
                <span>sports collectibles</span>
              </div>
              <div className={styles.actions}>
                <Link className={styles.primaryButton} href="/daniel/pitchpacks">
                  Play prototype →
                </Link>
                <a
                  className={styles.secondaryButton}
                  href="https://github.com/DanielTabakman/pitch-packs"
                  target="_blank"
                  rel="noreferrer"
                >
                  Project notes ↗
                </a>
              </div>
            </article>

            <article className={styles.card}>
              <p className={styles.eyebrow}>Markets · product</p>
              <h3>Market Structure OS</h3>
              <p>
                Tools for turning market beliefs into explicit, inspectable
                reasoning — with market structure, payoff design, and research
                experiments living in one system.
              </p>
              <div className={styles.tags}>
                <span>market structure</span>
                <span>options</span>
                <span>decision support</span>
              </div>
              <div className={styles.actions}>
                <Link className={styles.primaryButton} href="/">
                  Open product →
                </Link>
              </div>
            </article>

            <article className={styles.card}>
              <p className={styles.eyebrow}>Hackathon · prediction markets</p>
              <h3>Match Horizon</h3>
              <p>
                A World Cup demo that compares market probabilities with a
                user&apos;s belief, turns the disagreement into a simulated
                execution route, and resolves it against a deterministic replay.
              </p>
              <div className={styles.tags}>
                <span>prediction markets</span>
                <span>Kelly sizing</span>
                <span>replay</span>
              </div>
              <div className={styles.actions}>
                <a
                  className={styles.primaryButton}
                  href="https://match-horizon.vercel.app"
                  target="_blank"
                  rel="noreferrer"
                >
                  Open demo ↗
                </a>
                <a
                  className={styles.secondaryButton}
                  href="https://github.com/DanielTabakman/match-horizon"
                  target="_blank"
                  rel="noreferrer"
                >
                  Code ↗
                </a>
              </div>
            </article>

            <article className={styles.card}>
              <p className={styles.eyebrow}>Build log</p>
              <h3>GitHub</h3>
              <p>
                The less curated shelf: research tooling, hackathon work,
                agents, dashboards, and experiments that may or may not survive
                contact with reality.
              </p>
              <div className={styles.actions}>
                <a
                  className={styles.primaryButton}
                  href="https://github.com/DanielTabakman"
                  target="_blank"
                  rel="noreferrer"
                >
                  Browse GitHub ↗
                </a>
              </div>
            </article>
          </div>
        </section>

        <footer className={styles.footer}>
          <span>This is a public shelf, not a finished portfolio.</span>
          <Link href="/">← Back to Market Structure OS</Link>
        </footer>
      </div>
    </main>
  );
}
