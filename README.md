# Probability Prediction Engine

The Streamlit dashboard uses the shorter in-app and browser-tab title **Probability Engine**.

Cross-reference **market data** (stocks, crypto, futures) and **prediction markets** to find arbitrage, near-arbitrage, and high-probability opportunities. Later: derived (non-obvious) questions and AI-assisted trading, with visualization throughout.

## Stack

- **Python 3.11+**, **SQLite**, **Streamlit**
- **Data**: Yahoo Finance (gold, silver, Bitcoin), Polymarket (prediction markets)
- **Canonical events (v1)**: Gold, Silver, Bitcoin (e.g. “above $X by date Y”)

See [docs/PLAN.md](docs/PLAN.md) for full stack, data sources, and event definitions.

### Documentation and control plane (MVP1)

| Doc | Purpose |
|-----|---------|
| [docs/README.md](docs/README.md) | Documentation index |
| [docs/SOP/PPE_INTEGRATED_STATUS.md](docs/SOP/PPE_INTEGRATED_STATUS.md) | One-pager: chapter status, gates, deferred BUILD list |
| [docs/SOP/MVP1_FRONTIER.md](docs/SOP/MVP1_FRONTIER.md) | Live steering / slice queue |
| [docs/SOP/HANDOFF.md](docs/SOP/HANDOFF.md) | Session handoff gate |

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

### Commit and merge test gates

Canonical policy: [docs/SOP/COMMIT_POLICY_V1.md](docs/SOP/COMMIT_POLICY_V1.md). Operator setup: [docs/SOP/AGENT_GIT_SETUP.md](docs/SOP/AGENT_GIT_SETUP.md).

| When | Command |
|------|---------|
| **Every pushable commit (local)** | `python scripts/run_pushable_gate.py` (tier 0 docs-only / tier 1 targeted pytest / tier 2 full pytest) |
| **PR touching implied lab** (`src/viz/**`, smoke scripts) | also `python scripts/run_mvp1_dual_implied_lab_smoke.py` before merge (not every commit) |
| **Merge to `main`** | GitHub **CI** workflow green: **`CI / pytest`** (ruff + full pytest) **and** **`CI / docker_entrypoint`** (Docker image + Streamlit entry smoke). [Merge on green](.github/workflows/merge-on-green.yml) merges only when the **whole** `ci.yml` run succeeds, so both jobs must pass. |

### Testing policy (imports)

Unit tests should import **pure modules** under `src/` (for example `src.viz.app_panels`, `src.viz.frozen_evaluation_record`) and avoid importing `src.viz.app` unless the test is an explicit Streamlit integration test (that module runs `st.set_page_config` at import time and is slow). Periodically search `tests/` for `from src.viz.app import` / `import src.viz.app` to prevent regressions.

### Operator / steward backlog (rituals)

- **Day-to-day BUILD (full phase):** set [`docs/SOP/ACTIVE_PHASE_MANIFEST.json`](docs/SOP/ACTIVE_PHASE_MANIFEST.json) at SELECTION, then **`run_ppe.cmd`** from repo root ([`docs/SOP/ACTIVE_PHASE_MANIFEST.md`](docs/SOP/ACTIVE_PHASE_MANIFEST.md), [`docs/SOP/RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](docs/SOP/RELAY_ORCHESTRATOR_RUNBOOK_V1.md)).
- **After `run_ppe.cmd`:** read `artifacts/orchestrator/LAST_RUN_REPORT.md`; open a **new** Cursor thread with [`docs/SOP/AGENT_CONTINUITY_BRIEF.md`](docs/SOP/AGENT_CONTINUITY_BRIEF.md) only ([`docs/CONTEXT_RULES.md`](docs/CONTEXT_RULES.md)).
- **Dual smoke** before merging implied-lab PRs (see table above); Playwright required.
- **Relay / logbook** closeout when your SOP requires it (`run_slice.cmd`, `run_phase.cmd`, `scripts/log_event.py`, `artifacts/logbook/`).
- **Auto-merge to `main`:** [docs/SOP/GITHUB_ZERO_TOUCH_MERGE.md](docs/SOP/GITHUB_ZERO_TOUCH_MERGE.md).

### Agent commit / push behavior (automation)

- **Always-on rule:** [`.cursor/rules/auto-commit.mdc`](.cursor/rules/auto-commit.mdc). **One-time:** [docs/SOP/AGENT_GIT_SETUP.md](docs/SOP/AGENT_GIT_SETUP.md) + paste [`.cursor/USER_RULES_GIT_SNIPPET.md`](.cursor/USER_RULES_GIT_SNIPPET.md) if global rules still say “commit only when asked.”
- Auto-commit when todos are complete and `python scripts/run_pushable_gate.py` passes; show `git status` / `git diff` / `git log -1` first.
- Auto-push after the same gate on feature branches (no force-push).
- On **`main`**, prefer PR + full **CI** workflow green (pytest + docker_entrypoint) rather than direct push when branch protection applies.
- Never auto-commit secrets or artifacts (`.env`, `artifacts/`, caches, local DB files).

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
- `src/viz/` — Streamlit dashboards (`app.py` shell, `app_bitcoin_implied_lab.py` page, panels/domain modules — see [`docs/SOP/VIZ_LAYER_DISCIPLINE_V1.md`](docs/SOP/VIZ_LAYER_DISCIPLINE_V1.md))
- `docs/` — plan and design notes

### VPS / public demo (operators)

**Default release protocol:** **[docs/SOP/PRODUCTION_DEPLOY_PROTOCOL.md](docs/SOP/PRODUCTION_DEPLOY_PROTOCOL.md)** (branch `main`, bootstrap, Actions vs manual).

**Every UI release (local → git → VPS):** follow **[docs/SOP/DEMO_UI_RELEASE_CHECKLIST.md](docs/SOP/DEMO_UI_RELEASE_CHECKLIST.md)**.

**Auto-deploy on `main`:** after you configure secrets, **[docs/DEPLOY/GITHUB_ACTIONS_VPS_DEPLOY.md](docs/DEPLOY/GITHUB_ACTIONS_VPS_DEPLOY.md)** describes the GitHub Action that SSHs to the VPS and runs `git pull` + `docker compose up -d --build`.

Production layout (demo apex + private app, Caddy, Cloudflare Access, R2 backups) is documented in **[docs/DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md](docs/DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md)**. The runbook includes **Streamlit + `X-Forwarded-Proto`** (so lazy-loaded `/static/js/` chunks stay on **HTTPS** behind Cloudflare Flexible) and post-deploy smoke checks.

## Roadmap

1. **Phase 1**: Ingest markets + prediction markets → canonical events → probability layer
2. **Phase 2**: Arbitrage / near-arb / high-prob detection; simple derived events
3. **Phase 3**: Dashboards to visualize events and opportunities
4. **Phase 4**: AI and trading (later)
