# MSOS access identity v1

**Display name:** Access on MSOS routes + user-scoped API · **chapterId:** `msos_access_identity_v1`  
**Controlling canon:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) (phase 4b) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**Prior chapter:** [`SPRINT_MVP1_SNAPSHOT_OWNER_V1.md`](SPRINT_MVP1_SNAPSHOT_OWNER_V1.md)  
**SELECTION:** [`POST_MSOS_ACCESS_IDENTITY_V1_SELECTION.md`](POST_MSOS_ACCESS_IDENTITY_V1_SELECTION.md)  
**Priority:** **HIGH**  
**Baseline:** **`main`**

---

## Sprint intent

Extend **Cloudflare Access** to authenticated MSOS routes on apex; MSOS APIs read `CF-Access-Authenticated-User-Email` (or documented equivalent) and **scope reads/writes** to that identity. Completes multi-user-safe product path with PPE snapshot owner field.

---

## Preconditions

1. `mvp1_snapshot_owner_v1` **COMPLETE**.
2. `msos_workflow_persistence_v1` **COMPLETE**.
3. [`RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](../DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md) operator can add MSOS path policies.

---

## Acceptance

1. **Platform evidence:** Cloudflare Access policy covers `/command-center`, `/strategy-lab/*`, `/monitor`, `/history` (document operator steps).
2. **MSOS APIs:** workflow + command-center summary filter by authenticated email; 401 when protected route lacks identity.
3. **Caddy:** forwards Access JWT / identity headers to `msos_web` per runbook.
4. **Honest public routes:** `/` homepage remains public without fake “logged in.”
5. Pytest with mocked identity header; operator witness checklist.

## Not now

- Stripe / paid tier enforcement (phase 7 entitlements)
- Custom auth server

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-AccessIdV1-Control-Slice001** | EVIDENCE | CONTROL | Charter |
| **MSOS-AccessIdV1-Product-Slice002** | PRODUCT | MSOS_UI | Identity middleware + scoped APIs |
| **MSOS-AccessIdV1-Platform-Slice003** | EVIDENCE | PLATFORM | Caddy + Cloudflare runbook |
| **MSOS-AccessIdV1-Witness-Slice004** | EVIDENCE | CONTROL | pytest + evidence |
| **MSOS-AccessIdV1-Closeout-Slice005** | EVIDENCE | CONTROL | Close |
