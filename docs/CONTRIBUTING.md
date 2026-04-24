# Contributing (internal)

This repository is a **proprietary/paid product**. Do not assume public GitHub workflows, open-source licensing, or public issue trackers.

## Prereqs

- **Python**: 3.11+
- **OS**: Windows is a first-class dev environment for this repo.

## Setup (Windows PowerShell)

From the repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Setup (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app

Current Streamlit entrypoint (Option A for current sprint):

```bash
streamlit run src/viz/app.py
```

Planned migration entrypoint (do not treat as canonical yet):

```bash
streamlit run src/probability_engine/app/app.py
```

Windows convenience:
- Run `run.bat` from the repo root (double-click or from `cmd`). If the window closes immediately, run it from a terminal so you can see errors.

## Tests

```bash
pytest
```

## Formatting and lint

This repo uses **Ruff** locally for linting/formatting. CI currently gates on **pytest** only to avoid introducing formatting churn across the repo.

If Ruff isn’t installed yet:

```bash
pip install ruff
```

Run:

```bash
ruff format .
ruff check .
```

## What not to do

- **Do not** put data fetching or persistence directly in Streamlit code; UI must call **services only** (see `docs/ARCHITECTURE.md`).
- **Do not** introduce new vendor-shaped payloads across layers; normalize into `contracts` (see `docs/CONTRACTS.md`).
- **Do not** add “just for now” cross-imports that violate the dependency direction rules.

## Troubleshooting (Windows notes)

- **`pip install` access denied / file in use**: close other Python processes, Streamlit instances, or IDE terminals; then retry. If needed, delete and recreate `.venv`.
- **Long paths**: if you hit path-length issues, move the repo closer to drive root (e.g. `D:\proj\...`) or enable long paths in Windows policy.

