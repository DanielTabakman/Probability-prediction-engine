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

Fixture warnings in the HTTP witness (e.g. old storyboard copy) are **non-blocking** until the live-metrics product slice ships.
