# MVP1 B–L density smoothing v1 — relay sprint spec

**Controlling canon:** [`docs/IMPLIED_DISTRIBUTION_AND_STRATEGIES_PLAN.md`](../IMPLIED_DISTRIBUTION_AND_STRATEGIES_PLAN.md) (Method A)  
**Semantic contract:** [`docs/SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md)  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md)  
**SELECTION:** [`POST_MVP1_BL_DENSITY_SMOOTHING_V1_SELECTION.md`](POST_MVP1_BL_DENSITY_SMOOTHING_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Improve the **orange options-chain curve** on the implied lab: same legend (**Options chain (B–L)**), smoother and more stable density from live Deribit marks. Reduces jagged finite-difference noise and **degenerate / skipped** B–L fits so screen-share demos and anomaly detection are more trustworthy.

**Priority:** **MEDIUM** (P2 demo confidence — not `high`; steward may SELECTION before MSOS slot-1 website rows when lab demo matters more).

---

## Scope (engine — `ppe-core`)

1. **Smoothed call inputs** before B–L (pick one primary path; optional second as fallback):
   - Per-strike `mark_iv` → Black–Scholes call prices on a dense strike grid, **or**
   - Convex / monotone spline fit on observed `C(K)` from marks, then differentiate.
2. **Optional robustness:** OTM call–put blended marks where both exist (document choice).
3. Keep **`market_implied_density_breeden_litzenberger`** as the public entry point or thin wrapper — UI labels unchanged.
4. **Normalize** and clamp as today; fewer `bl_status=skipped` degenerate cases.
5. Unit tests: synthetic smile + known forward → smooth PDF, ∫f ≈ 1, no negative mass after clamp.

---

## Scope (UI — display only unless stats drift)

- No third chart method; no legend rename.
- Distribution summary / CSV **market_implied_bl** rows should benefit automatically when engine improves.
- Optional witness note in evidence if mean/q50 shift materially on a fixed fixture.

---

## Acceptance

1. Orange curve visually smoother on a typical Deribit expiry (witness screenshot or smoke note).
2. `python -m pytest -q` green; new tests in `tests/test_implied_distribution.py` or dedicated smoothing tests.
3. `is_anomalous` / L2 still use lognormal vs market-implied — behavior documented if thresholds need retuning.
4. Legibility copy unchanged (`TRACE_OPTIONS_CHAIN`, `DIST_METHOD_BL`).

---

## Touch set (expected)

- `src/engine/implied_distribution.py` — smoothing + B–L pipeline
- `src/data/fetch_deribit.py` — only if per-strike IV fetch helper needed (no viz imports)
- `tests/test_implied_distribution.py` (or `tests/test_bl_density_smoothing_v1.py`)
- `docs/SOP/EVIDENCE/` — closeout witness (on closeout slice)

---

## Not now

- Third distribution method on chart (Dupire, SVI surface product line, mixtures)
- MSOS Next.js changes unless embed consumes same engine path unchanged
- Cross-venue CSV column schema changes (downstream may improve automatically)
- Relay plan / SELECTION until steward charters chapter

---

## Sprint status

**CHARTERED** — `queueAfterPlanPath`: dist quant v2; **next READY** after current chapter closeout (`ppe_queue_insert_after.py`).
