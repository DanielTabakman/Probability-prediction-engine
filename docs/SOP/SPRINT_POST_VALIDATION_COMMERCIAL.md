# Commercial Validation — sprint spec (post-Validation Chapter)

**Status:** ACCEPTED (2026-05-19 steward approval).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION record:** [`POST_VALIDATION_CHAPTER_SELECTION.md`](POST_VALIDATION_CHAPTER_SELECTION.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Run **commercial Reality Checks** and ship a **minimal paid-beta / research-offer surface** (copy, CTA, operator playbook) without billing automation or scope creep into execution/multi-asset.

## Sprint-level acceptance

1. At least one **paid-interest** signal recorded (willingness to pay, waitlist, or paid pilot commitment) in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) — or steward-classified **prep-complete** with written rationale and next outreach step.
2. Offer surface live on demo or landing path (honest copy; no guaranteed alpha).
3. Optional: NVIDIA/LEAPS **manual brief** completed and logged (no code).
4. `python -m pytest -q` green on `main` before/after any PRODUCT slice.

## Not now

- Billing, entitlements, self-serve accounts
- Multi-asset options automation
- Execution / ticket / auto-trade language

---

## Slice map

### Commercial-Validation-Control-Slice001 — charter sync (CONTROL) — **CLOSED**

**Goal:** Promote draft spec + phase plan; update `MVP1_FRONTIER.md` active chapter row.

**Closed 2026-05-19:** frontier, HANDOFF, phase plan updated.

---

### Commercial-Validation-Offer-Slice002 — offer surface v0 (PRODUCT) — **CLOSED**

**Goal:** Single offer CTA on demo path — **private demo + paid research beta** (v0 copy).

**Deliverables:** `PPE_RESEARCH_OFFER_URL` / `PPE_RESEARCH_OFFER_LABEL` env gates; demo banner in [`src/viz/app.py`](../../src/viz/app.py); tests in [`tests/test_signup_cta.py`](../../tests/test_signup_cta.py).

**Acceptance:** copy review against `PPE_MASTER_MVP1.md` commercial boundary; pytest + dual smoke green.

---

### Commercial-Validation-Reality-Slice003 — paid interest log (CONTROL) — **CLOSED**

**Goal:** Operator playbook + reality-check row; live customer signal when available.

**Deliverables:** [`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md); row in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

---

### Commercial-Validation-Nvidia-Brief-Slice004 — manual brief (CONTROL) — **CLOSED**

**Goal:** One-page manual NVIDIA/LEAPS research brief; log in reality checks.

**Deliverables:** [`briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md`](briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md).

---

## Phase plan

[`PHASE_PLANS/post_validation_commercial_validation.json`](PHASE_PLANS/post_validation_commercial_validation.json)
