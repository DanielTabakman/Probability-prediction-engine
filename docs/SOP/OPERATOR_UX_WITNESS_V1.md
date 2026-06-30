# Operator UX witness (human vs machine)

**Plane:** CONTROL-PLANE · **Canon:** [`TESTING_TIERS_V1.md`](TESTING_TIERS_V1.md)

## Split of responsibility

| Who | When | What |
|-----|------|------|
| **CI / agents** | Every VPS deploy + before asking operator to look | HTTP witness (`msos_production_demo_witness.cmd`) + Playwright screenshots (`msos_production_playwright_witness.cmd`) |
| **Operator (human)** | After witnesses PASS **and** MSOS visitor surfaces changed | Solo subjective pass — see checklist below |
| **Visitors / testers** | Anytime | Public feedback at `/feedback` or Strategy Lab strip — no operator required |

Agents **do not** ask the operator to catch HTTP 500s, missing embeds, or broken routes — those are machine gates.

## When to ask the operator (solo)

Human UX witness is **not** every deploy. Run it when:

- `apps/msos-web/` visitor copy, layout, or workflow changed, **or**
- Agents cannot resolve a Playwright / copy witness warning, **or**
- You want a calm solo check before sharing the demo link

Skip when the pass was control-plane-only (`scripts/`, `docs/SOP/`, relay) with no MSOS shell diff.

## Commands (agents)

```bat
msos_production_demo_witness.cmd
msos_production_playwright_witness.cmd
```

Artifacts: `artifacts/health/msos_production_demo_witness.json` and `artifacts/health/msos_production_playwright/<run_id>/`.

## Solo UX checklist (~5 min, only when machine PASS)

1. Open https://marketstructureos.com/strategy-lab
2. Follow [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) steps 1–5 (skip live session logging unless something failed)
3. Check **three boxes** — all must pass for a green solo witness:
   - [ ] **Chart in 2 min** — I found the main implied chart without hunting
   - [ ] **No scary jargon** — first scan reads like a trader product, not internal notes
   - [ ] **Link-ready** — I'd send the URL without apologizing for the UI
4. Optional: submit your own notes via https://marketstructureos.com/feedback or `/learn?debrief=1`
5. Export visitor submissions anytime:

```bat
python scripts/ppe_export_web_feedback.py --markdown
```

Logging in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) is **optional** for solo UX witness — use it when a box fails or you want a paper trail.

## Public feedback (visitors — async validation)

| Surface | URL / path |
|---------|------------|
| Full form | https://marketstructureos.com/feedback |
| Compact strip | Strategy Lab footer → **Share quick feedback** |
| After tour | Platform tutorial completion → `/feedback` |
| Operator debrief | `/learn?debrief=1` — submit or copy validation row |

Submissions append to `ppe_web_feedback.jsonl` on the VPS (`PPE_WEB_FEEDBACK_DIR`). Operators review via export script — no live screen share required for early signal.

## Public copy (agents — `msos-shell`)

Before asking the operator to UX-walkthrough, grep new UI for banned jargon (`PPE`, `fixture`, `workflow store`, raw errors). Canon: [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) · helpers: `apps/msos-web/src/lib/publicCopy.ts`.

Fixture warnings in the HTTP witness (e.g. old storyboard copy) are **non-blocking** — but any visitor-visible string must follow public copy. Agents fix copy in the same pass; operators judge tone on walkthrough.
