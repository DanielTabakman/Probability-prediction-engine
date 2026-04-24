# Decisions (ADR-lite)

## 2026-04-23 — App-first with planned upgrade

- **Decision**: App-first architecture now, with enforced boundaries so “library + app” is a mechanical upgrade later.
- **Why**: fast iteration while the vision is evolving; keep core logic clean for eventual productization.

## 2026-04-23 — Package namespace

- **Decision**: Primary import namespace is **`probability_engine`**.
- **Why**: stable, product-friendly name.

## 2026-04-23 — Automation runtime

- **Decision**: Retire `orchestrator/` path and keep `scripts/relay_runtime_v0.py` as the single supported relay runtime.
- **Why**: stdlib-only, spec-tested, minimal vendor tie-in.

## 2026-04-23 — Storage approach

- **Decision**: Hybrid storage scaffold: `NullStore` by default, optional `SQLiteStore` snapshots later.
- **Why**: keeps iteration fast while enabling reproducibility/backtesting when ready.

## 2026-04-23 — Canonical app entrypoint

- **Decision**: **Option A (current sprint)** — official Streamlit entrypoint remains `src/viz/app.py`.
- **Migration target**: `src/probability_engine/app/app.py`.
- **Why**: keep the current UI stable while we migrate toward the packaged `probability_engine` app path.

# Decisions (lightweight ADR log)

This repository is a **proprietary/paid product**. Decisions are recorded for internal alignment and upgrade safety.

Format:
- **Status**: Accepted | Planned | Deprecated
- Keep entries short; add links to follow-on docs when useful.

---

## ADR-0001: App-first architecture with enforced boundaries

- **Status**: Accepted
- **Decision**: The product is organized around an `app` layer that calls `services` only. Core logic is isolated in `domain`, I/O is isolated in `infra`, and normalized data shapes live in `contracts`.
- **Why**: Prevent UI-driven spaghetti, keep logic testable, and make later storage/integration changes low-risk.
- **Consequences**:
  - Streamlit code must stay thin and must not perform I/O or complex computation directly.
  - Cross-layer imports must follow the direction rules in `docs/ARCHITECTURE.md`.

## ADR-0002: Canonical package name `probability_engine`

- **Status**: Accepted
- **Decision**: New code migrates into `src/probability_engine/...` as the stable import root.
- **Why**: Consistent namespace for app/services/domain/infra/contracts and future packaging.
- **Consequences**:
  - Transitional shims may exist, but the end-state import root is `probability_engine`.

## ADR-0003: Retire “orchestrator” path in favor of services

- **Status**: Planned
- **Decision**: Any orchestrator-style coordination logic is replaced by explicit `services/*` use-cases.
- **Why**: Services provide a clearer boundary, test surface, and dependency direction.
- **Consequences**:
  - Orchestration is not embedded in UI, scripts, or ad-hoc runner modules.

## ADR-0004: Hybrid storage scaffold (now: SQLite/local; later: upgrade path)

- **Status**: Accepted
- **Decision**: Provide storage via an infra abstraction that supports:
  - local/dev persistence (e.g. SQLite / file-backed)
  - optional cache layer
  - a clear upgrade path to a server database if/when needed
- **Why**: Keep dev friction low while preserving a path to scale and reliability.
- **Consequences**:
  - `domain` stays storage-agnostic.
  - `services` own transactional boundaries and persistence decisions.

## ADR-0005: Single app entrypoint

- **Status**: Accepted
- **Decision**: The UI is launched through one canonical entrypoint.
  - **Current**: `streamlit run src/viz/app.py`
  - **Planned**: `streamlit run src/probability_engine/app/app.py` (or equivalent) once migration completes
- **Why**: Avoid multiple subtly different entrypoints and configuration drift.
- **Consequences**:
  - Helper scripts should call the same entrypoint or share a single runner function in `app/`.

