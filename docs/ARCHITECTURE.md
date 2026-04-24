# Architecture (App-first, enforce boundaries)

This repository is an **app-first** codebase (fast iteration) with a **planned upgrade** path to “library + app”.
We enforce boundaries now so that the upgrade is mechanical later.

## Goals

- **Keep Streamlit thin**: UI should be layout + state wiring only.
- **Make core logic testable**: business logic is pure, deterministic, and unit-tested.
- **Make I/O reliable**: external calls (Deribit/Yahoo/Polymarket) share the same retry/timeout/diagnostics policy.
- **Enable reproducibility later**: optional snapshot storage (SQLite) via a pluggable store.

## Layering (dependency direction)

Allowed direction:

`app/` → `services/` → (`domain/`, `infra/`, `contracts/`)

Rules:

- **`domain/`** must not import Streamlit, `requests`, or write files.
- **`infra/`** is the only layer that performs network I/O (HTTP).
- **Migration note (legacy I/O exception)**: while `src/data/*` fetchers still exist, treat `src/data/` as *the* I/O layer (equivalent to `infra/`). It must be invoked **only** via `probability_engine.services` adapters/shims and **never** imported/called from `src/viz/` (or `probability_engine.app`). End-state remains: all HTTP clients live in `probability_engine.infra`.
- **`app/`** must not call fetchers directly; it calls `services/`.
- **`app/` is layout only**: presentation/layout + state wiring; no data normalization, no business rules, no market-shape assembly.
- **`contracts/`** contains the shared shapes used between layers (TypedDict/dataclasses).

## Implied-lab service boundary (input preparation)

Implied-lab **input preparation** (assembling normalized `market_data` used by the lab) occurs in `probability_engine.services` (e.g. `services/implied_lab_inputs.py`).

- UI provides selections + cached fetch wrappers.
- Services assemble/normalize the `market_data` payload.
- Domain/derive functions consume `state` + `market_data` deterministically.

## Code layout (target)

Primary package namespace is **`probability_engine`**:

```
src/probability_engine/
  app/          # Streamlit entrypoints + UI composition (thin)
  services/     # app use-cases (fetch/normalize/compute/render payloads)
  domain/       # pure logic (math, payoff, parsing rules) - test heavy
  infra/        # I/O: HTTP, fetchers, caching, storage backends
  contracts/    # shared data shapes crossing boundaries
```

Legacy modules currently live under:

```
src/viz/     # Streamlit dashboard (legacy)
src/data/    # fetchers (legacy)
src/engine/  # pure-ish math/strategy modules (legacy)
```

Migration is incremental: new `probability_engine.app` entrypoint can import legacy UI while we move modules behind `services/`.

## Hybrid storage scaffold

We use a **pluggable Store**:

- `NullStore`: default, no persistence (fast iteration)
- `SQLiteStore`: optional, append-only snapshot tables

The UI does not write to SQLite directly. Persistence is called from `services/` after normalization:

`services/*` → `store.write_*()` (optional)

## Proprietary product note

This repository is intended to be a **paid/proprietary product**. Do not assume open-source distribution conventions.

- **Owns**: canonical data representations used between layers: rows, state, outputs, enums, IDs, timestamps.
- **Must not depend on**: `app/`, `services/`, `domain/`, `infra/` (keep it low/no-dependency).

Authoritative definitions live in `docs/CONTRACTS.md` and should be mirrored by code types/schemas.

## Dependency direction rules (enforced)

Allowed imports (✅) and forbidden imports (❌):

- `app` → ✅ `services`, `contracts` | ❌ `infra`, deep `domain`
- `services` → ✅ `domain`, `contracts`, `infra` (through adapters) | ❌ `app`
- `domain` → ✅ `contracts` | ❌ `services`, `infra`, `app`
- `infra` → ✅ `contracts` | ❌ `app`, (ideally ❌ `services` except narrow adapter interfaces)
- `contracts` → ❌ all project modules except stdlib (keep minimal)

## Where code lives (planned end-state)

```
src/probability_engine/
  app/                 # Streamlit UI + entrypoints only
  services/            # orchestration/use-cases
  domain/              # pure computation + rules
  infra/               # external I/O + storage
  contracts/           # normalized data shapes
```

## What not to do (common boundary breaks)

- **Do not** call `requests`, `yfinance`, DB code, or filesystem writes from Streamlit callbacks.
- **Do not** pass raw vendor payloads (Polymarket JSON, yfinance frames) across layers; normalize into `contracts`.
- **Do not** let `domain` read env vars, open files, or fetch network data.
- **Do not** “just import a helper” from `app/` into `services/` or `domain/` (inverts dependency).
- **Do not** resurrect `orchestrator/` (pre-v1 prototype; intentionally gitignored). Use `scripts/relay_runtime_v0.py` as the supported runtime.

## Upgrade path (from current repo to app-first)

Current layout includes `src/viz/` (Streamlit), `src/engine/` (logic), `src/data/` (fetchers), `src/models/` (schema).

Planned migration steps:

- Move `src/viz/*` → `src/probability_engine/app/*` (UI only; call services).
- Move `src/engine/*` → `src/probability_engine/domain/*` (pure logic) and `services/*` (orchestration).
- Move `src/data/*` → `src/probability_engine/infra/*` (clients/adapters).
- Move `src/models/schema.py` → `src/probability_engine/contracts/*` (types) + `infra/storage/*` (DDL/migrations).

During migration, prefer **compatibility shims** in `services/` so `app/` stays stable while internals move.

