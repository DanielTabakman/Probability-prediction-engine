# MVP1 operator ritual — freeze → review → class summary

Repeatable validation path for the closed-loop v0 on **full app** (`PPE_ENABLE_SNAPSHOTS=1`).

## Prerequisites

- Streamlit: `streamlit run src/viz/app.py`
- Snapshots enabled (default locally unless `PPE_ENABLE_SNAPSHOTS=0`)
- Optional: `PPE_SNAPSHOT_DB_PATH` (default `data/ppe_frozen_evaluations.sqlite3`)

## Ritual (one horizon)

1. **Open** Bitcoin implied lab; select one **Expiry** in the sidebar.
2. **Refresh** priced inputs (Deribit) if you want live quotes.
3. **Read** MVP1 output line (candidate / watch only / no trade) and **Belief vs market — at a glance** when belief is on.
4. **Freeze:** expand **Freeze & history** → note → **Freeze this evaluation**.
5. **Reopen:** pick the frozen row from the list → confirm read-only verification + MVP1 fields.
6. **Review:** on reopen path, set review status (not `pending`) + short note → save.
7. **Class summary:** expand **Class summary — reviewed snapshots** → confirm counts update.

## Automated checks (before merge)

```bash
python -m pytest -q
python scripts/run_mvp1_dual_implied_lab_smoke.py
```

UI smoke depends on Playwright + live Deribit/Yahoo; classify failures per [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md) §6 when `page_loaded` is false.

## Evidence target (Validation Chapter)

- ≥10 frozen evaluations (mix of output states)
- ≥5 completed (non-pending) reviews
- Class summary non-zero for at least one bucket

Log counts in `artifacts/logbook/ppe_events.jsonl` or steward notes.
