/**
 * Homepage visitor copy — canon: docs/PRODUCT_COPY/packets/homepage.v2.md
 * Copy agent edits this file; BUILD wires components to import from here.
 */

export const homepageMetadata = {
  title: "Market Structure OS",
  description:
    "Compare your market thesis with what options imply — explore structures without hiding assumptions.",
} as const;

export const homepageHero = {
  eyebrow: "For traders with a market view",
  h1: "Turn your market thesis into a trade you can reason about.",
  body: "Market Structure OS helps traders compare market-implied probabilities with their own view, locate meaningful disagreement, and explore structures that fit the thesis — without hiding the assumptions.",
  primaryCta: "Try the BTC Options Lab",
  secondaryCta: "Open Command Center",
  signInCta: "Sign in",
  pills: [
    "Your thesis stays yours",
    "Expression, not recommendation",
    "BTC options live preview",
  ],
} as const;

export const homepageProductCards = [
  {
    title: "Market Structure OS",
    body: "One workspace for thesis-driven market decisions.",
  },
  {
    title: "Strategy Lab",
    body: "Build, compare, and monitor strategies from a clear market view.",
  },
  {
    title: "Probability Engine",
    body: "See where options pricing agrees — or disagrees — with your thesis.",
  },
] as const;

export const homepageLensTags = {
  btcLive: "BTC options — Live",
  eventMarkets: "Event markets — Coming",
  perpPositioning: "Perp positioning — Coming",
} as const;

export const homepagePreview = {
  urlLabel: "marketstructureos.com / command-center",
  title: "Command Center",
  subtitle: "Compare the market's view with yours — then find the cleanest expression.",
  demoTag: "Live demo",
  comparisonSection: "Market comparison",
  marketImplies: {
    label: "Market implies",
    value: "Wider expected range",
    hint: "Options-implied distribution",
  },
  yourThesis: {
    label: "Your thesis",
    value: "Narrower expected range",
    hint: "Your stated market view",
  },
  vs: "vs",
  thesisGap: {
    label: "Thesis gap",
    value: "21%",
    tag: "Worth reviewing",
    detail: "Your range is 21% narrower than current options pricing implies.",
  },
} as const;

export const homepageFeatures = [
  {
    kicker: "01 — Read",
    title: "See what the market implies",
    body: "Start with options pricing, probabilities, positioning, and other market surfaces.",
  },
  {
    kicker: "02 — State",
    title: "Add your thesis",
    body: "Turn your view into something the system can compare against the market.",
  },
  {
    kicker: "03 — Fit",
    title: "Explore possible expressions",
    body: "Compare structures that fit your view, risk limits, and time horizon.",
  },
  {
    kicker: "04 — Learn",
    title: "Track what happened",
    body: "Review how the thesis, structure, and outcome evolved over time.",
  },
] as const;
