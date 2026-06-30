# Operator UX witness (human vs machine)

**Plane:** CONTROL-PLANE · **Canon:** [`TESTING_TIERS_V1.md`](TESTING_TIERS_V1.md)

## Split of responsibility

| Who | When | What |
|-----|------|------|
| **CI / agents** | Every VPS deploy + before asking operator to look | HTTP witness + Playwright + **public copy gate** |
| **Operator (human)** | After witnesses PASS **and** MSOS visitor surfaces changed | Solo 3-checkbox pass (~5 min) |
| **Visitors / testers** | Anytime | `/feedback` — async, no operator required |

Agents **do not** ask the operator to catch HTTP 500s, missing embeds, broken routes, or banned jargon — those are machine gates.

## Machine gates (agents)

```bat
msos_production_demo_witness.cmd
msos_production_playwright_witness.cmd
msos_public_copy_gate.cmd
```

| Gate | Catches |
|------|---------|
| HTTP witness | Routes, display API, embed health |
| Playwright | Screenshots, belief click, confirm navigation, **banned copy in rendered HTML** |
| Public copy gate | Banned jargon in visitor-facing source strings |

Artifacts: `artifacts/health/msos_production_demo_witness.json`, `artifacts/health/msos_production_playwright/<run_id>/`.

## When to ask the operator (solo)

Human UX witness is **not** every deploy. Run when MSOS shell copy/layout changed or Playwright/copy gate reports warnings you want a human tone check on.

Skip control-plane-only passes with no `apps/msos-web/` visitor diff.

## Solo UX checklist (~5 min)

1. Open https://marketstructureos.com/strategy-lab
2. Follow [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) steps 1–5
3. All three must pass:
   - [ ] **Chart in 2 min** — main implied chart without hunting
   - [ ] **No scary jargon** — reads like a trader product
   - [ ] **Link-ready** — you'd send the URL without apologizing
4. Optional: submit notes at `/feedback` or `/learn?debrief=1`
5. Review submissions: https://marketstructureos.com/operator/feedback (Cloudflare Access) or `python scripts/ppe_export_web_feedback.py --markdown`

Logging in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) is **optional** unless a box fails.

## Async validation (preferred while solo)

See [`OPERATOR_ASYNC_VALIDATION_V1.md`](OPERATOR_ASYNC_VALIDATION_V1.md) — outreach + feedback form counts toward wedge proof without live screen share.

## Public copy (agents — `msos-shell`)

Before human walkthrough: `msos_public_copy_gate.cmd` must pass. Canon: [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) · helpers: `apps/msos-web/src/lib/publicCopy.ts`.

Fixture warnings in HTTP witness are **non-blocking**; banned visitor jargon is **blocking** for ship.
