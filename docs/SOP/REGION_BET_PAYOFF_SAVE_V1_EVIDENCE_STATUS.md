# Region Bet payoff and save v1 — evidence status

## Status

COMPLETE. Product is on `main` via PR #5475 (`cc93fd6b`). Closeout recorded; do not re-BUILD product. Stale Autobuilder draft #5473 is closed as superseded.

## COORDINATION STATUS

| Slice | Status | Evidence |
| --- | --- | --- |
| `RegionBet-PayoffSave-Control-Slice001` | COMPLETE | Founder-approved charter, queue entry, phase plan, and selection record for Autobuilder catalog order 10. |
| `RegionBet-PayoffSave-Product-Slice002` | COMPLETE | Region Bet payoff/save shipped in #5475 (`cc93fd6b`). |
| `RegionBet-PayoffSave-Closeout-Slice003` | COMPLETE | Chapter closed after #5475; order 11 is also terminal (#5478). |

## Owns

Guided-flow payoff/scenario explanation, explicit confirmation, and owner-scoped persistence of a monitorable Region Bet with an immutable entry snapshot.

## Does not own

Expression-fit ranking math (#5454), risk-to-expression bridge (#5463), monitor teaching, manage/adjust, learning closeout, live execution, or Autobuilder runtime authority.

## Dependency

Requires terminal `region_bet_risk_expression_bridge_v1` on product main (PR #5463). Satisfied.

## Notes

Product paths stay bounded to `docs/SOP/PHASE_PLANS/region_bet_payoff_save_v1_relay.json`. Do not catalog or rebuild this chapter.
