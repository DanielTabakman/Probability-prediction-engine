# MVP1 snapshot owner v1 — PPE persistence identity

**Display name:** PPE snapshot owner field · **chapterId:** `mvp1_snapshot_owner_v1`  
**Controlling canon:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) (phase 4a) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**Prior chapter:** [`SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md`](SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md)  
**SELECTION:** [`POST_MVP1_SNAPSHOT_OWNER_V1_SELECTION.md`](POST_MVP1_SNAPSHOT_OWNER_V1_SELECTION.md)  
**Priority:** **HIGH**  
**Baseline:** **`main`**

---

## Sprint intent

Add **owner identity** to PPE frozen evaluations so multi-user MSOS and Streamlit lab can scope snapshots per Cloudflare Access email. Without this, phase 4 MSOS access cannot filter “your” freezes honestly.

**Operator goal:** Freezes saved on `app.*` are attributable to the signed-in user; MSOS Command Center bridge can filter by owner.

---

## Preconditions

1. `msos_workflow_persistence_v1` **COMPLETE** (MSOS workflow store exists).
2. Cloudflare Access passes identity to `app_full` (document header name in platform evidence).

---

## Acceptance

1. **Schema:** `frozen_evaluations` gains nullable `owner_email` (migration safe for existing rows).
2. **Write path:** Streamlit save/freeze captures Access identity when header present; null allowed for legacy/demo.
3. **Read path:** list APIs in `frozen_evaluation_store.py` support optional `owner_email` filter.
4. **Tests:** pytest for migration + filter; no change to PPE math contracts.
5. Evidence doc documents header contract for Caddy/Cloudflare.

## Not now

- MSOS route Access policies (phase 4b `msos_access_identity_v1`)
- Billing / entitlements
- Custom auth server

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MVP1-SnapshotOwner-Control-Slice001** | EVIDENCE | CONTROL | Charter + migration witness |
| **MVP1-SnapshotOwner-Product-Slice002** | PRODUCT | PPE_UI | Store + Streamlit save path |
| **MVP1-SnapshotOwner-Witness-Slice003** | EVIDENCE | CONTROL | pytest + evidence |
| **MVP1-SnapshotOwner-Closeout-Slice004** | EVIDENCE | CONTROL | Chapter close |
