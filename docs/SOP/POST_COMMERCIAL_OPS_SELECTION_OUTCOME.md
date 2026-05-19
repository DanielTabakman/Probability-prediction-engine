# Post–commercial ops — SELECTION outcome (2026-05-19)

**Status:** **SELECTION COMPLETE** — next BUILD chapter chartered.

**Inputs:** Ops agent lane green (pytest **153**, dual smoke `20260519_131035` / `131251`); `docker-compose.yml` wires `PPE_RESEARCH_OFFER_*`; VPS auto-deploy on `main` push; paid-interest **N** (honest — live call still steward-scheduled).

---

## Selected next BUILD chapter

| Field | Value |
|-------|--------|
| **Chapter** | **MVP1 Reliability** |
| **Sprint spec** | [`SPRINT_MVP1_RELIABILITY.md`](SPRINT_MVP1_RELIABILITY.md) |
| **Phase plan** | [`PHASE_PLANS/mvp1_reliability_relay.json`](PHASE_PLANS/mvp1_reliability_relay.json) |
| **Baseline** | **`main`** after ops compose commit |
| **First slice** | `MVP1-Reliability-Control-Slice001` (CONTROL) |

---

## Rationale (steward SELECTION)

| Candidate | Decision |
|-----------|----------|
| **MVP1 reliability** | **Selected** — smoke runs were killed mid-scenario (`exit_code=4294967295`) before green witness; narrow hardening (harness timeouts, progress witness, deploy env docs) de-risks demos before a large Phase 2 reconcile. |
| **Phase 2 on `main`** | **Deferred** — prefer after reliability relay green + steward Phase 2 baseline reconcile from `recovery/frontier-steward-v2_1-baseline`. |
| **Sprint 003 evidence-plane** | **Deferred** — no fresh pilot evidence. |

**Paid interest N** does not block reliability BUILD; steward continues outreach in parallel per [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md).

---

## Steward parallel (non-BUILD)

1. VPS repo-root `.env` with `PPE_RESEARCH_OFFER_URL` + `PPE_RESEARCH_OFFER_LABEL` (compose keys on `main`).
2. Browser: **Research beta (v0)** on `marketstructureos.com`.
3. One live paid-interest conversation → **Y/N** in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

---

## Next execution step

Run **`MVP1-Reliability-Control-Slice001`** per relay runbook → accept sprint spec → PRODUCT slices in phase plan.
