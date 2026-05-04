# MVP1 Phase 1–3 — Build sprint (contracted)

Purpose: provide a stable slice spec file for MVP1 Phase 1–3 implementation and relay-gated execution.

Controlling canon: `docs/VISION/PPE_MASTER_MVP1.md` (MVP1 phases + governance + exclusions).
Live steering: `docs/SOP/MVP1_FRONTIER.md`.

## Slices

### MVP1-Phase1-Slice001 — Market + benchmark substrate completion (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** complete MVP1 Phase 1 contract:
- explicit benchmark identity + version
- market width and benchmark width visible on the same horizon
- visible trust state + honest degraded-state handling

**Non-goals / exclusions (MVP1):**
- no exact strikes workflows
- no trade ticket / executable ticket generation
- no snapshot persistence (Phase 4)
- no review engine (Phase 5)
- no class summaries (Phase 6)

**Acceptance evidence:**
- `python -m pytest -q` PASS
- `python scripts/run_implied_lab_ui_smoke.py` PASS (or explicitly classified if live-data degraded)

---

### MVP1-Phase2-Slice001 — Width-gap engine v1 (benchmarked) (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** implement MVP1 Phase 2 engine contract (benchmark vs market width):
- ATM width gap calculation: **absolute + relative**
- explicit **materiality logic** (v0 proxies allowed, must be labeled as such)
- explicit **trust gating** using `usable/degraded/invalid` (must affect outputs)
- required label set:
  - `market_too_wide`
  - `market_too_narrow`
  - `mixed_unclear`
  - `insufficient_trust`
  - `insufficient_materiality`

**Non-goals / exclusions (MVP1):**
- no confidence tiers (Phase 3)
- no output-state decision surface (Phase 3)
- no exact strikes workflows
- no trade ticket / executable ticket generation
- no snapshot persistence (Phase 4)

**Acceptance evidence:**
- `python -m pytest -q` PASS
- update verification payload with explicit fields for `W_m`, `W_b`, `G_abs`, `G_rel`, trust state, and materiality evaluation

---

### MVP1-Phase3-Slice001 — Decision surface (candidate/watch/no-trade) (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** implement MVP1 Phase 3 contract:
- exactly one primary output state: `candidate` / `watch_only` / `no_trade`
- explanation (plain language)
- confidence tier
- expression-family mapping (family-level only; no exact strikes)
- falsification condition
- review horizon assignment
- first-class no-trade reasoning

**Decision precedence (must match master canon):**
1) invalid path → no-trade  
2) low-trust → no-trade  
3) mixed/unclear → watch_only or no-trade  
4) insufficient materiality → no-trade  
5) marginal disagreement → watch_only  
6) clear+material+high-trust → candidate

**Non-goals / exclusions (MVP1):**
- no snapshot persistence (Phase 4)
- no review engine (Phase 5)
- no class summaries (Phase 6)
- no exact strikes workflows
- no trade ticket / executable ticket generation

**Acceptance evidence:**
- `python -m pytest -q` PASS
- `python scripts/run_implied_lab_ui_smoke.py` PASS (or explicitly classified if live-data degraded)
- verification payload contains `primary_output_state` and the required explanation/confidence/horizon fields

---

### MVP1-UIExclusions-Slice001 — Hide out-of-scope MVP1 UI surfaces (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** enforce MVP1 out-of-scope boundaries in the UI so it cannot be mistaken for later-phase functionality.

**Required exclusions (hide/disable):**
- exact strikes / target payoff surfaces (anything that implies strike selection or payoff targeting)
- trade ticket / executable ticket surfaces and any “execution-ready” implications

**Acceptance evidence:**
- `python -m pytest -q` PASS
- `python scripts/run_implied_lab_ui_smoke.py` PASS (or explicitly classified if live-data degraded)
- MVP1 panel does not present any strike-level or ticket-level workflow; any legacy panels are hidden or gated behind a non-MVP1 flag

