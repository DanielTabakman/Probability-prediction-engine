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

## Roadmap

1. **Phase 1**: Ingest markets + prediction markets → canonical events → probability layer
2. **Phase 2**: Arbitrage / near-arb / high-prob detection; simple derived events
3. **Phase 3**: Dashboards to visualize events and opportunities
4. **Phase 4**: AI and trading (later)
