# MVP1 guided demo path v1 — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B–15F · [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) § Founder-operator  
**Semantic contract:** [`docs/SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md) (copy only)  
**Operator crib sheet:** [`FOUNDER_OPERATOR_CRIB_SHEET_V1.md`](FOUNDER_OPERATOR_CRIB_SHEET_V1.md)  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md)  
**SELECTION:** [`POST_MVP1_GUIDED_DEMO_PATH_V1_SELECTION.md`](POST_MVP1_GUIDED_DEMO_PATH_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Reduce **founder-operator demo friction** on the public Streamlit lab: fewer sidebar rituals, less scroll, less noise on screen share — **without** new math, disagreement rules, or MSOS shell work.

Target: steward can run [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) in **~3 minutes** after one page load, with implied lab visible without hunting.

**Priority:** **MEDIUM** · **P2 lab legibility** — charter after B–L smoothing unless steward marks `urgent: true` when `sessions_logged < 3` and solo rehearsal still fails.

---

## Scope (PRODUCT — `src/viz/`)

1. **Guided demo / screen-share mode** — env flag (e.g. `PPE_GUIDED_DEMO=1` or extend existing demo env) that:
   - Collapses or hides **reference-only** blocks by default (Polymarket expanders, market context chart, debug performance).
   - Keeps **Bitcoin implied lab** as the primary surface (above-fold or anchor jump).
2. **Operator talk track** — compact **founder crib** panel or expanded **How this lab works** above the chart (copy from [`FOUNDER_OPERATOR_CRIB_SHEET_V1.md`](FOUNDER_OPERATOR_CRIB_SHEET_V1.md) — five concepts, no equations).
3. **Optional one-click Deribit refresh** on first demo load when guided mode is on (best-effort; degrade clearly if network fails).
4. **Document** env vars in `.env.example` and [`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md) demo setup.

---

## Scope (CONTROL)

- Charter witness + evidence status stub.
- Update [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) if the guided path changes steps.

---

## Acceptance

1. With guided mode env on, operator rehearsal: implied lab + chart visible without manual scroll past tutorial-only content (witness note or smoke marker).
2. **`python -m pytest -q`** green; tests for guided-mode gating (no regression on full app default).
3. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** (default env unchanged).
4. No new “recommended trade” or alpha language; semantic contracts unchanged.

---

## Touch set (expected)

- `src/viz/` — guided demo module + wiring in `app.py` / sidebar as needed
- `src/viz/tutorial.py` or `commercial_wrapper.py` — copy alignment only
- `tests/` — guided demo mode tests
- `.env.example`
- `docs/SOP/DEMO_OPERATOR_SCRIPT.md`, `docs/SOP/COMMERCIAL_VALIDATION_OPERATOR.md`

---

## Not now

- MSOS Next.js routes or embed changes
- New distribution math, B–L pipeline, or disagreement classification
- Billing, paywall, auto-trading
- Equation tooltips or Verification expansion by default
- Market registry / multi-asset

---

## Sprint status

**CHARTERED** — `queueAfterPlanPath`: B–L smoothing; steward **SELECTION** when prior chapter closeout propagates queue (or `urgent` bump per selection doc).
