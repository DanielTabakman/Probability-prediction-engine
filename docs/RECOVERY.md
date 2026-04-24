# Recovery

This project is designed to be safe to “reset and rerun” locally. If something gets weird (dependency conflicts, Streamlit behaving oddly, DB/schema drift), use the steps below to get back to a clean state.

## Reset the virtual environment

From the repo root:

```bash
deactivate  # if currently in a venv (ok if this errors)
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you use `run.bat`, you can also just delete `.venv/` and re-run `run.bat` (it recreates the venv and reinstalls deps).

## Clear Streamlit cache

Prefer the UI first:

- Open the app
- Click the “hamburger” menu (top-right)
- Use Streamlit’s **Clear cache** action

If you need a manual reset, you can delete Streamlit’s local cache dirs (location varies by OS/version). Safe options:

- Delete the project-local `.streamlit/` folder (if present; it’s mostly config)
- Delete your user-level Streamlit cache directory (commonly under your user home/app-data)

Then restart Streamlit:

```bash
streamlit run src/viz/app.py
```

## Clear/delete the DB (and optional snapshot DB)

This repo may create local SQLite files under `data/`:

- **Main app DB** (default): `data/engine.db` (configurable via `DB_PATH`)
- **Optional snapshot DB** (only if enabled): `data/probability_engine.sqlite`
  - Snapshotting is controlled by `ENABLE_SNAPSHOTS` and `SNAPSHOT_DB_PATH` (see `src/probability_engine/infra/store.py`)

To wipe local state:

```bash
rmdir /s /q data
mkdir data
```

Or delete just the DB files you care about:

```bash
del data\engine.db
del data\probability_engine.sqlite
```

## Get back to a clean git state

If you just want to discard local edits to tracked files:

```bash
git restore .
```

If you also want to delete ALL untracked files/folders (including build artifacts, venvs, caches, local DBs), use this (destructive):

```bash
git clean -fdx
```

If you want to fully reset tracked files to the last commit as well (destructive):

```bash
git reset --hard
git clean -fdx
```

