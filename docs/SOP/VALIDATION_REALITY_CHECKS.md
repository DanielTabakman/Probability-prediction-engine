# Validation Chapter — Reality Checks log

Lightweight external validation. Copy a row per session.

**Strategic focus:** Log sessions against targets in [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) (return rate, paid interest, PMF survey). Use the playbook **session script** for guided tester runs.

| Date | Check | Pass? | Notes |
|------|--------|-------|-------|
| 2026-06-21 | **MCD operator sign-off (production witness)** | Y | All 9 MCD criteria witness-verified — [`MSOS_MCD_OPERATOR_WITNESS_V1_EVIDENCE_STATUS.md`](MSOS_MCD_OPERATOR_WITNESS_V1_EVIDENCE_STATUS.md). Production journey PASS; research beta CTA OK; embed shell markers on `/strategy-lab`. External 15-min comprehension → first TRADER_WORKFLOW cohort row. |
| 2026-06-21 | **MSOS production live hookup (Track A+C)** | Y | HTTP witness PASS on `marketstructureos.com`; VPS deploy not run from desktop (no `ppe_operator_ssh.local.cmd`). Track B apex Access deferred. |
| 2026-06-19 | **MSOS E2E journey (production HTTP witness)** | Y (journey) | `python scripts/msos_production_demo_witness.py` — all storyboard routes HTTP 200 on `marketstructureos.com`; Cloudflare Access on `app.marketstructureos.com`; fixture labels honest on monitor/history/CC. **Research beta CTA:** N until VPS `PPE_RESEARCH_OFFER_URL` set + `msos_web` rebuild. |
| 2026-05-19 | **Paid interest** — willingness to pay for beta/brief/call | N | Phase2 Product-Slice003 shipped; VPS CTA still pending `.env`; **steward live call required** — [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md) §Outreach (**do not mark Y** without real conversation) |
| 2026-05-19 | **Reviewable cases** — showed freeze + reopen + review on full app | Y | Ritual + evidence clock seeded to targets (see VALIDATION_EVIDENCE_STATUS) |
| 2026-05-19 | **NVIDIA / LEAPS** — manual brief only (no code) | Y | [`briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md`](briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md) drafted; live interviews optional follow-up |

## Demo clarity

Use [DEMO_OPERATOR_SCRIPT.md](DEMO_OPERATOR_SCRIPT.md). Pass if the viewer can describe chart + disagreement readout without jargon.

## Paid interest

Single offer surface (pick one): private demo + paid beta, weekly BTC brief, bespoke call. Record objection themes.

## Reviewable cases

On full app: run [MVP1_OPERATOR_RITUAL.md](MVP1_OPERATOR_RITUAL.md) once live in front of viewer if possible.

## NVIDIA / LEAPS

Manual research brief only — do not expand MVP1 BTC scope. Note whether customer values thesis-to-options translation.

## §15F demo spot-check (optional)

After usable-demo UX on production: 5–10 min with 1–2 testers. Copy a row when done.

| Date | Tester profile | Understood “what this run is saying” without Verification? | Trust strip noticed? | Would open again? | Notes |
|------|----------------|--------------------------------------------------------------|----------------------|---------------------|-------|
| _fill_ | _e.g. quant-curious friend_ | Y/N | Y/N | Y/N | |

Use [DEMO_OPERATOR_SCRIPT.md](DEMO_OPERATOR_SCRIPT.md) timing; rubric detail in [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15F.

## MSOS P8 tester metrics (template)

Log after guided MSOS web sessions (`/learn` learn loop). Do **not** auto-widen scope from fixture UI alone.

| Date | Tester profile | Comprehension (~5 min) | Thesis confirm honest | Return to monitor/history | Paid interest (steward call) | Notes |
|------|----------------|------------------------|----------------------|---------------------------|------------------------------|-------|
| _fill_ | _e.g. research contact_ | Y/N | Y/N | Y/N | Y/N | Link session notes |

**Next queue recommendation (P8 closeout):** optional validation logging before paywall or live execution SELECTION.

**Validation rollup:** [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) — interim **COMPLETE** 2026-06-13 (0 guided sessions; PMF targets pending).

## Evidence targets (engineering companion)

- ≥10 freezes, ≥5 completed reviews ([MVP1_WIDTH_PROTOCOL.md](MVP1_WIDTH_PROTOCOL.md)) — live counts in [VALIDATION_EVIDENCE_STATUS.md](VALIDATION_EVIDENCE_STATUS.md)
- `python -m pytest -q` and dual smoke green on `main` — see engineering gates in [VALIDATION_EVIDENCE_STATUS.md](VALIDATION_EVIDENCE_STATUS.md)
