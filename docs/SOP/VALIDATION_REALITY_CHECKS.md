# Validation Chapter — Reality Checks log

Lightweight external validation. Copy a row per session.

| Date | Check | Pass? | Notes |
|------|--------|-------|-------|
| 2026-05-19 | **Demo clarity** — viewer names main object in ~5 min | Y | Prep: public demo URL + operator script; MVP1 banner above fold on branch |
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

## Evidence targets (engineering companion)

- ≥10 freezes, ≥5 completed reviews ([MVP1_WIDTH_PROTOCOL.md](MVP1_WIDTH_PROTOCOL.md)) — live counts in [VALIDATION_EVIDENCE_STATUS.md](VALIDATION_EVIDENCE_STATUS.md)
- `python -m pytest -q` and dual smoke green on `main` — see engineering gates in [VALIDATION_EVIDENCE_STATUS.md](VALIDATION_EVIDENCE_STATUS.md)
