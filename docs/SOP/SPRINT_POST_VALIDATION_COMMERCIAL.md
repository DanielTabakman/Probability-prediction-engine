# Commercial Validation — draft sprint spec (post-Validation Chapter)

**Status:** DRAFT — awaiting steward approval before relay BUILD.  
**Live steering after approval:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION record:** [`POST_VALIDATION_CHAPTER_SELECTION.md`](POST_VALIDATION_CHAPTER_SELECTION.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Run **commercial Reality Checks** and ship a **minimal paid-beta / research-offer surface** (copy, CTA, operator playbook) without billing automation or scope creep into execution/multi-asset.

## Sprint-level acceptance

1. At least one **paid-interest** signal recorded (willingness to pay, waitlist, or paid pilot commitment) in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).
2. Offer surface live on demo or landing path (honest copy; no guaranteed alpha).
3. Optional: NVIDIA/LEAPS **manual brief** completed and logged (no code).
4. `python -m pytest -q` green on `main` before/after any PRODUCT slice.

## Not now

- Billing, entitlements, self-serve accounts
- Multi-asset options automation
- Execution / ticket / auto-trade language

---

## Slice map (draft)

### Commercial-Validation-Control-Slice001 — charter sync (CONTROL) — **SELECTED**

**Goal:** Promote draft spec + phase plan; update `MVP1_FRONTIER.md` active chapter row.

**Deliverables:** this file (accepted), phase plan, HANDOFF GATE.

---

### Commercial-Validation-Offer-Slice002 — offer surface v0 (PRODUCT) — **DEFERRED**

**Goal:** Single offer CTA block on demo path (private beta / weekly brief / call — pick one for v0).

**Acceptance:** copy review against `PPE_MASTER_MVP1.md` commercial boundary; pytest green.

---

### Commercial-Validation-Reality-Slice003 — paid interest log (CONTROL) — **DEFERRED**

**Goal:** Fill paid-interest row in reality-check log with dated notes from real conversation.

---

### Commercial-Validation-Nvidia-Brief-Slice004 — manual brief (CONTROL) — **DEFERRED**

**Goal:** One-page manual NVIDIA/LEAPS research brief; log result in reality checks.

---

## Phase plan

[`PHASE_PLANS/post_validation_commercial_validation.json`](PHASE_PLANS/post_validation_commercial_validation.json)
