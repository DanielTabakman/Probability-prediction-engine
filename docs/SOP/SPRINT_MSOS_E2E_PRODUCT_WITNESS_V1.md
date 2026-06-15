# MSOS end-to-end product witness v1

**chapterId:** `msos_e2e_product_witness_v1`  
**Controlling canon:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) (phase 6)  
**Prior chapter:** [`SPRINT_MSOS_MONITOR_HISTORY_LIVE_V1.md`](SPRINT_MSOS_MONITOR_HISTORY_LIVE_V1.md)  
**SELECTION:** [`POST_MSOS_E2E_PRODUCT_WITNESS_V1_SELECTION.md`](POST_MSOS_E2E_PRODUCT_WITNESS_V1_SELECTION.md)  
**Priority:** **MEDIUM**  
**Baseline:** **`main`**

---

## Sprint intent

Prove the **full storyboard journey** works on production (or staging) as one coherent product — not slice-by-slice green in isolation.

**Journey:** `/` → sign in → Strategy Lab (live embed) → confirm thesis → expression plan → Command Center (real data) → monitor → history → learn.

---

## Preconditions

1. Phases 1–5 **COMPLETE** on deployed apex + `app.*`.

---

## Acceptance

1. Evidence doc with **checked operator path** (URLs + screenshots or honest blocked reason).
2. Automated pytest smoke where feasible (route reachability + API contracts); browser E2E optional if env allows.
3. One row in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).
4. Deviations from storyboard documented per screen.

## Not now

- New product features
- Stripe checkout in witness path (unless phase 7 shipped)

---

## Slice map

| Slice | Plane | Deliverable |
|-------|--------|-------------|
| **MSOS-E2EWitV1-Control-Slice001** | EVIDENCE | Charter + checklist |
| **MSOS-E2EWitV1-Witness-Slice002** | EVIDENCE | pytest + operator witness doc |
| **MSOS-E2EWitV1-Closeout-Slice003** | EVIDENCE | Close |
