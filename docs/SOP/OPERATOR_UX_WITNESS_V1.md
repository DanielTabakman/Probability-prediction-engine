# Operator UX witness (human vs machine)

**Plane:** CONTROL-PLANE · **Canon:** [`TESTING_TIERS_V1.md`](TESTING_TIERS_V1.md)

## Split of responsibility

| Who | When | What |
|-----|------|------|
| **CI / agents** | Every VPS deploy + before asking operator to look | HTTP witness (`msos_production_demo_witness.cmd`) + Playwright screenshots (`msos_production_playwright_witness.cmd`) |
| **Operator (human)** | After witnesses PASS | Subjective walkthrough: pleasant? understandable in 5 min? would you show a friend? |

Agents **do not** ask the operator to catch HTTP 500s, missing embeds, or broken routes — those are machine gates.

## Commands (agents)

```bat
msos_production_demo_witness.cmd
msos_production_playwright_witness.cmd
```

Artifacts: `artifacts/health/msos_production_demo_witness.json` and `artifacts/health/msos_production_playwright/<run_id>/`.

## Human walkthrough (only when machine PASS)

1. Open https://marketstructureos.com/strategy-lab
2. Follow [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md)
3. Log notes in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) — optional

Fixture warnings in the HTTP witness (e.g. old storyboard copy) are **non-blocking** — but any visitor-visible string must follow [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md). Agents fix copy in the same pass; operators judge tone on walkthrough.

## Public copy (agents — `msos-shell`)

Before asking the operator to UX-walkthrough, grep new UI for banned jargon (`PPE`, `fixture`, `workflow store`, raw errors). Canon: [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) · helpers: `apps/msos-web/src/lib/publicCopy.ts`.
