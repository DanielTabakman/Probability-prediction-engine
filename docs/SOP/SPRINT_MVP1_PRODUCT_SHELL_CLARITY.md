# MVP1 product shell clarity — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 1 (product shell).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_DECISION_REVIEW_SELECTION_OUTCOME.md`](POST_MVP1_DECISION_REVIEW_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Clarify the **MVP1 product shell** on the BTC implied lab path: readable **name hierarchy** (Probability Engine → BTC Implied Lab), **compact sidebar** when MVP1 compact UI is active, and an obvious **feedback path** — copy and layout only; no auth, billing, or landing-page rewrite.

---

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** with run IDs in [`MVP1_PRODUCT_SHELL_CLARITY_EVIDENCE_STATUS.md`](MVP1_PRODUCT_SHELL_CLARITY_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on chapter closeout.

---

## Not now

- Full public marketing site, SSO, or paywall.
- Phase 3 commercial wrapper (new charter).
- Multi-asset workspaces beyond current BTC lab.
- Recovery merge of blind `app.py` / `mvp1_benchmark_substrate.py`.

---

## Slice map

### MVP1-ProductShell-Control-Slice001 — charter (EVIDENCE-PLANE)

Charter witness: sprint spec, phase plan, evidence stub, frontier/queue alignment; baseline `main`.

### MVP1-ProductShell-Product-Slice002 — shell polish (PRODUCT)

**Touch:** `src/viz/mvp1_product_shell.py`, `src/viz/app_panels.py`, `src/viz/app_sidebar.py`, `tests/`.  
**Forbidden:** `src/viz/app.py`, `src/viz/app_bitcoin_implied_lab.py` unless steward packet widens TOUCH_SET.

### MVP1-ProductShell-Smoke-Slice003 — dual smoke (EVIDENCE-PLANE)

Dual smoke witness; extend MVP1_compact markers for product-shell context strip if needed.

### MVP1-ProductShell-Closeout-Slice004 — chapter close (EVIDENCE-PLANE)

Evidence witness + steward CONTROL-CLOSEOUT.

---

## Sprint status

**IN PROGRESS** — see [`MVP1_PRODUCT_SHELL_CLARITY_EVIDENCE_STATUS.md`](MVP1_PRODUCT_SHELL_CLARITY_EVIDENCE_STATUS.md).
