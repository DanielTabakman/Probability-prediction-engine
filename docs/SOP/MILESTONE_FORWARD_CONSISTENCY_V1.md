# Milestone: Forward Consistency v1

**Milestone ID:** `forward_consistency_v1`  
**Program:** [`FORWARD_CONSISTENCY_PROGRAM_V1.md`](FORWARD_CONSISTENCY_PROGRAM_V1.md)  
**Related milestone:** [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md) — internal consistency lane  
**As-of:** 2026-06-28

---

## What this milestone is

**Goal:** Reuse the asset catalog and Strategy Lab surfaces to show whether **option-implied synthetic forwards** and **tradable futures/perp forwards** are internally consistent after executable bid/ask and estimated costs — honestly, visually, research-only.

**Not** a one-off SOL widget. **Not** live execution or order routing.

**North star question:**

> For this asset and expiry, are the option-implied synthetic forward and the tradable future/perp forward internally consistent after executable bid/ask and estimated costs?

---

## Foundation (in flight)

| Piece | Status |
|-------|--------|
| Engine + JSON contract | **PR #447** (`build/forward-consistency-v1`) |
| Strategy Lab panel | Same PR |
| Deribit BTC/ETH | Same PR |
| Bybit SOL | Follow-on chapter |
| Cross-surface + archive | Later chapters |

---

## Milestone complete when

1. **Spine live on main:** Engine, `forward-consistency.json`, Strategy Lab panel green on production for Deribit BTC/ETH.
2. **Bybit path:** SOL (and tier-1 Bybit assets) return comparable checks or honest `NOT_COMPARABLE`.
3. **Surfaces:** At least one secondary surface (Horizon strip or Command Center glance) reads the same JSON contract.
4. **Honesty:** No execution language; status enum documented; copy separates spot vs chart median vs arb frame.
5. **Witness:** Evidence docs green; operator can open Strategy Lab and interpret `NO_ARB` / `WATCH` without confusion.

---

## Explicitly not this milestone

- Live execution, monitor alerts, Agenomics embed implementation
- Expression planning auto-fill from `POSSIBLE_ARB` legs
- Equity American-option parity (honest deferral only)
- Historical arb archive / replay (deferred chapter)

---

## Canon docs

| Doc | Role |
|-----|------|
| [`FORWARD_CONSISTENCY_PROGRAM_V1.md`](FORWARD_CONSISTENCY_PROGRAM_V1.md) | Chapter sequence + operator artifacts |
| [`docs/VISION/FORWARD_CONSISTENCY/JSON_CONTRACT_V1.md`](../VISION/FORWARD_CONSISTENCY/JSON_CONTRACT_V1.md) | API + status enum |
| [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) | Frontier pointer after charter |
