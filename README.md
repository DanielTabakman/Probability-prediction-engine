# Probability Prediction Engine

Cross-reference **market data** (stocks, crypto, futures) and **prediction markets** to find arbitrage, near-arbitrage, and high-probability opportunities. Later: derived (non-obvious) questions and AI-assisted trading, with visualization throughout.

## Stack

- **Python 3.11+**, **SQLite**, **Streamlit**
- **Data**: Yahoo Finance (gold, silver, Bitcoin), Polymarket (prediction markets)
- **Canonical events (v1)**: Gold, Silver, Bitcoin (e.g. “above $X by date Y”)

See [docs/PLAN.md](docs/PLAN.md) for full stack, data sources, and event definitions.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run src/viz/app.py
```

Optional: copy `.env.example` to `.env` and set any API keys (none required for initial sources).

### Implied lab (MVP1) — operator switches

| Variable | When to set | Effect |
|----------|-------------|--------|
| `PPE_POST_MVP1_LAB_UI` | Omit or `0` / empty | **Default MVP1** implied lab: strike ladder, payoff → strikes solver, green payoff on chart, trade ticket, and related panels stay **hidden** (compact belief + chart + digest). |
| `PPE_POST_MVP1_LAB_UI` | `1`, `true`, `yes`, or `on` (case-insensitive) | Restores the **full post-MVP** workbench (same controls as before MVP1 UI exclusions). |
| `PPE_SNAPSHOT_DB_PATH` | Optional | Override path for **frozen evaluation** SQLite DB. If unset, defaults to `data/ppe_frozen_evaluations.sqlite3` under the repo root (see `src/viz/frozen_evaluation_store.py`). |

**Freeze & history:** In the Streamlit app, open Bitcoin implied lab → expand **Freeze & history (this device, SQLite)** under the chart column to save or reopen read-only snapshots.

**Dual UI smoke (MVP1 default + full lab):** from the repo root, with Playwright installed for the harness:

```bash
python scripts/run_mvp1_dual_implied_lab_smoke.py
```

This runs `MVP1_compact_verification` without `PPE_POST_MVP1_LAB_UI`, then `A_width_target_payoff` with `PPE_POST_MVP1_LAB_UI=1`. Manifests are written under `artifacts/ui_smoke/<run_id>/`.

Running `implied_lab_ui_smoke_harness.py` **without** `--scenario` exercises every entry in its `SCENARIOS` list in one Streamlit session; with default MVP1 UI, scenarios that open **Mode & solver** will fail—prefer `--scenario` or the dual runner above.

### Testing policy (imports)

Unit tests should import **pure modules** under `src/` (for example `src.viz.app_panels`, `src.viz.frozen_evaluation_record`) and avoid importing `src.viz.app` unless the test is an explicit Streamlit integration test (that module runs `st.set_page_config` at import time and is slow). Periodically search `tests/` for `from src.viz.app import` / `import src.viz.app` to prevent regressions.

### Operator / steward backlog (rituals)

- Re-run **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** after major implied-lab or harness changes (Playwright required).
- Run **`python -m pytest -q`** (full suite) before merge when you touched shared modules.
- Use **relay / logbook** closeout when your SOP requires it for a slice (`run_slice.cmd`, `scripts/log_event.py`, `artifacts/logbook/`).

### Agent commit / push behavior (automation)

- Auto-commit when the active plan's todos are complete and **targeted tests** for the touched code pass (always showing `git status` / `git diff` / `git log -1` first).
- Auto-push on **feature branches** to their tracked remote after targeted tests pass (no force-push, no history rewrite).
- Auto-push on **`main`** / `master` only after **full pytest** (`python -m pytest -q`) passes.
- Never auto-commit secrets or obvious artifacts by default (`.env`, `artifacts/`, caches, local DB files); never force-push.

**If `pip install` says "file in use" or "access denied"**: another program (IDE, another terminal, Python process) is using the package files. Close other Python/terminal windows and try again, or use a new venv in a new folder.

**Windows double-click**: run `run.bat` from the project folder. It will show the project path and any errors; if the window flashes and closes, open Command Prompt, `cd` to the project folder, then run `run.bat` so you can see the output.

## Run from another device (GitHub)

1. **Put this repo on GitHub** (one-time, from this machine):
   - Create a new repository on [github.com](https://github.com/new) (e.g. `probability-prediction-engine`), no README/license needed.
   - In the project folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: probability engine Phase 1"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
   Use your GitHub username and repo name for `YOUR_USERNAME` / `YOUR_REPO_NAME`.

2. **On any other device**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```
   Then same quick start: venv, `pip install -r requirements.txt`, `streamlit run src/viz/app.py` (or on Windows, `run.bat` after copying it into the clone).

## Project layout

- `config/` — symbols, event definitions, source URLs
- `src/data/` — fetchers (Yahoo, Polymarket)
- `src/models/` — DB schema, canonical event types
- `src/engine/` — probability layer, opportunity detection
- `src/viz/` — Streamlit dashboards
- `docs/` — plan and design notes

### VPS / public demo (operators)

Production layout (demo apex + private app, Caddy, Cloudflare Access, R2 backups) is documented in **[docs/DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md](docs/DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md)**. The runbook includes **Streamlit + `X-Forwarded-Proto`** (so lazy-loaded `/static/js/` chunks stay on **HTTPS** behind Cloudflare Flexible) and post-deploy smoke checks.

## Roadmap

1. **Phase 1**: Ingest markets + prediction markets → canonical events → probability layer
2. **Phase 2**: Arbitrage / near-arb / high-prob detection; simple derived events
3. **Phase 3**: Dashboards to visualize events and opportunities
4. **Phase 4**: AI and trading (later)
