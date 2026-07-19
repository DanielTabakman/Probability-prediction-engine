# Market Proposal + Hedge Capacity Preview v0 Closeout

**Issue:** #5391  
**Branch:** `codex/market-proposal-hedge-capacity-v0`  
**Base commit:** `829a68ff85519c277df31d494918bfbf8212ecf8`  
**Dependency:** #5388 independently accepted and PR #5393 merged at `d22ad66687c77013ec0eb46ca2f194810f8739b8`.

## Scope

Implemented a feature-flagged, preview-only operator surface for deterministic BTC terminal above/below market proposals and Deribit inverse-option vertical-spread hedge-capacity previews.

Feature flag:

```text
PPE_MARKET_PROPOSAL_PREVIEW_UI=1
```

Smoke-only default route:

```text
PPE_MARKET_PROPOSAL_PREVIEW_DEFAULT=1
```

## Exported Proposal

Tracked fixture export:

```text
docs/SOP/MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_V0_EXPORTED_PROPOSAL.md
```

Latest generated fixture witness export:

```text
artifacts/market_proposal_hedge_capacity/fixture_witness/20260719T010939Z/market_proposal_hedge_capacity_preview.md
```

Latest live public-data witness export:

```text
artifacts/market_proposal_hedge_capacity/live_witness/20260719T010939Z/market_proposal_hedge_capacity_preview.md
```

## Validation Evidence

```text
python -m pytest -q tests/test_market_proposal_hedge_capacity.py
20 passed in 0.52s

python scripts/run_market_proposal_hedge_capacity_smoke.py
ok: true
screenshot_path: artifacts/market_proposal_hedge_capacity_smoke/20260718_210940/market_proposal_preview.png

python scripts/run_market_proposal_hedge_capacity_witness.py --fixture
ok: true
readiness_state: SHAREABLE_DESIGN
YES policy capacity: 9000.0
NO policy capacity: 6000.0

python scripts/run_market_proposal_hedge_capacity_witness.py --live
ok: true
readiness_state: SHAREABLE_DESIGN
YES policy capacity: 1000.0
NO policy capacity: 9450.0
question: Will the official Deribit BTC delivery price for the option expiry at 08:00 UTC on 2026-07-19 be strictly above $64,500? YES pays $1 and NO pays $0.

python scripts/run_research_decision_dashboard_smoke.py
ok: true

python scripts/run_mvp1_dual_implied_lab_smoke.py
default MVP1_compact_verification pass: true
post-MVP1 A_width_target_payoff pass: false

python scripts/run_pushable_gate.py
All checks passed!
1529 passed in 104.78s
ppe_delegation_envelope: WARN - steward_packet; can_auto_ship=False warning only

python scripts/run_pushable_gate.py --pre-push
All checks passed!
1657 passed in 118.17s
4 passed, 1 skipped, 1657 deselected in 14.03s
ppe_delegation_envelope: WARN - steward_packet; can_auto_ship=False warning only
```

The post-MVP1 lab smoke failure is reported as residual shared-app evidence. The default compact surface and the accepted Research Review surface were green after the shared sidebar/app integration change.

## COORDINATION STATUS

```text
COORDINATION STATUS
Agreement: aligned
Compared: issue #5391, program, SELECTION, Codex packet, accepted #5388/#5393, current Deribit public documentation, focused tests, UI smoke, fixture witness, live public-data witness, shared-app smokes, pushable gate, pre-push gate
Disagreement: none
Evidence gap: fresh CI remains pending until the draft PR branch is pushed
Ownership overlap: no edits to overlapped docs/SOP/REPO_LAYER_PATH_PREFIXES.json; bounded edits to Streamlit app/sidebar, Deribit public adapter, fixture, smoke, witness, tests and export paths
Risk if unresolved: post-MVP1 optional lab smoke remains red outside the default compact path; live hedge capacity is snapshot-only and not a guaranteed fill
Recommended default: open draft PR for independent regular-Chat review and stop after acceptance for founder discussion
Founder decision required: no
```
