import type { Metadata } from "next";
import styles from "./connect.module.css";

const LINKEDIN_URL = "https://ca.linkedin.com/in/daniel-tabakman-5361b6196";
const PRODUCT_URL = "https://marketstructureos.com/";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Connect with Daniel Tabakman",
  description: "Connect with Daniel Tabakman on LinkedIn, WhatsApp, or through Market Structure OS.",
  alternates: { canonical: "https://marketstructureos.com/connect" },
  openGraph: {
    title: "Daniel Tabakman — Let's connect",
    description: "Products, systems, markets, and execution. Find the right way to connect.",
    url: "https://marketstructureos.com/connect",
    type: "profile",
  },
  robots: { index: false, follow: true },
};

function Arrow() {
  return (
    <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Download() {
  return (
    <svg aria-hidden="true" width="19" height="19" viewBox="0 0 24 24" fill="none">
      <path d="M12 3v12m-4-4 4 4 4-4M5 17v3h14v-3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function ConnectPage() {
  // Keep the phone number out of the public repository. Configure it on the
  // production VPS as MSOS_CONNECT_WHATSAPP_NUMBER after owner approval.
  const phone = (process.env.MSOS_CONNECT_WHATSAPP_NUMBER ?? "").replace(/\D/g, "");
  const whatsappUrl = /^\d{10,15}$/.test(phone) ? `https://wa.me/${phone}` : null;

  return (
    <main className={styles.shell}>
      <div className={styles.layout}>
        <header className={styles.top}>
          <div className={styles.identity}>
            <span className={styles.mark} aria-hidden="true">DT<span className={styles.markDot}>.</span></span>
            <span className={styles.topLabel}>PERSONAL CONTACT CARD</span>
          </div>
          <span className={styles.location}><span className={styles.locationDot} /> TORONTO, CANADA</span>
        </header>

        <div className={styles.content}>
          <section className={styles.hero} aria-labelledby="connect-name">
            <div className={styles.eyebrow}><span className={styles.line} /> IDEAS INTO EXECUTION</div>
            <div className={styles.monogram} aria-hidden="true">DT</div>
            <h1 id="connect-name">Daniel <span>Tabakman</span></h1>
            <p className={styles.role}>Product <span>·</span> Strategy <span>·</span> Systems</p>
            <p className={styles.intro}>
              I work at the intersection of technology, markets, and operations —
              turning complex ideas into products and systems people can use.
            </p>
          </section>

          <section className={styles.linksSection} aria-labelledby="ways-to-connect">
            <div className={styles.sectionHeading}>
              <h2 id="ways-to-connect">Let&apos;s connect</h2>
              <span>CHOOSE YOUR PATH</span>
            </div>

            <nav className={styles.linkList} aria-label="Connect with Daniel">
              <a className={styles.linkCard} href={LINKEDIN_URL} target="_blank" rel="noopener noreferrer">
                <span className={`${styles.linkIcon} ${styles.linkedin}`} aria-hidden="true">in</span>
                <span className={styles.linkCopy}>
                  <strong>LinkedIn</strong>
                  <small>Connect professionally</small>
                </span>
                <span className={styles.arrow}><Arrow /></span>
              </a>

              {whatsappUrl ? (
                <a className={styles.linkCard} href={whatsappUrl} target="_blank" rel="noopener noreferrer">
                  <span className={`${styles.linkIcon} ${styles.whatsapp}`} aria-hidden="true">↗</span>
                  <span className={styles.linkCopy}>
                    <strong>WhatsApp</strong>
                    <small>Start a conversation</small>
                  </span>
                  <span className={styles.arrow}><Arrow /></span>
                </a>
              ) : (
                <div className={`${styles.linkCard} ${styles.unavailable}`} aria-label="WhatsApp link pending configuration">
                  <span className={`${styles.linkIcon} ${styles.whatsapp}`} aria-hidden="true">↗</span>
                  <span className={styles.linkCopy}>
                    <strong>WhatsApp</strong>
                    <small>Available after contact confirmation</small>
                  </span>
                  <span className={styles.pending}>PENDING</span>
                </div>
              )}

              <a className={styles.linkCard} href={PRODUCT_URL} target="_blank" rel="noopener noreferrer">
                <span className={`${styles.linkIcon} ${styles.msos}`} aria-hidden="true">M</span>
                <span className={styles.linkCopy}>
                  <strong>Market Structure OS</strong>
                  <small>See what I&apos;m building</small>
                </span>
                <span className={styles.arrow}><Arrow /></span>
              </a>
            </nav>

            <a className={styles.saveButton} href="/connect/contact.vcf" download="Daniel-Tabakman.vcf">
              <Download /> <span>Save my contact</span> <Arrow />
            </a>
            <p className={styles.saveHint}>Add me to your phone contacts in one tap.</p>
          </section>
        </div>

        <footer className={styles.footer}>
          <span>A SIMPLE WAY TO STAY CONNECTED</span>
          <a href={PRODUCT_URL} target="_blank" rel="noopener noreferrer">MARKETSTRUCTUREOS.COM <span aria-hidden="true">↗</span></a>
        </footer>
      </div>
    </main>
  );
}
