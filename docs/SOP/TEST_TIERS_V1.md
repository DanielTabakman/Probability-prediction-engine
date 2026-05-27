## Test tiers V1 (SOP)

Purpose: reduce time spent on redundant / flaky tests without weakening the canonical safety gate.

### Core rules (unchanged)

- **Canonical pushable gate (code):**
  - `python -m ruff check src tests scripts`
  - `python -m pytest -q`
- UI smoke is **high value** but more environment-sensitive; treat it as **tiered evidence**, not a constant tax.

### Tiers

#### Tier 0 — Fast local (default while iterating)

- **Run:**
  - `python -m ruff check src tests scripts`
  - `python -m pytest -q`
- **When:** most code iterations; any time you want quick confidence without UI automation.

#### Tier 1 — UI sanity (single harness pass)

- **Run:** Tier 0 plus:
  - `python scripts/run_implied_lab_ui_smoke.py`
- **When:** changes touching `src/viz/**` or smoke harness logic where you want a single end-to-end pass.

#### Tier 2 — Dual smoke witness (slice-grade UI evidence)

- **Run:** Tier 0 plus:
  - `python scripts/run_mvp1_dual_implied_lab_smoke.py`
- **When:** before closing a smoke/witness slice; before merging UI-heavy PRs; when you need MVP1 + full-lab confirmation.

#### Tier 3 — Full packaging sanity (rare)

- **Run:** Tier 2 plus Docker entry smoke (CI equivalent).
- **When:** pre-release / when diagnosing docker_entrypoint failures.

### Guidance to reduce smoke load safely

- Prefer **Tier 1** for most UI iterations; save **Tier 2** for witness/closeout moments.
- If a smoke is flaky, **deflake the harness** (visibility checks, robust waits) rather than rerunning indefinitely.
- Track smoke attempts and wall-clock time using `artifacts/logbook/ppe_events.jsonl` + dev notes.

