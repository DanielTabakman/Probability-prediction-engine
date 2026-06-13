# MSOS public demo launch v1

**Controlling canon:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) (P3 distribution) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**Prior chapter:** [`SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md`](SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md)  
**SELECTION:** [`POST_MSOS_PUBLIC_DEMO_LAUNCH_V1_SELECTION.md`](POST_MSOS_PUBLIC_DEMO_LAUNCH_V1_SELECTION.md)  
**Priority:** **MEDIUM**  
**Baseline:** **`main`**

---

## Sprint intent

After visual parity, make the **public demo real**: MSOS Next shell live on VPS apex, research-beta CTA wired, operator witness that URLs match expectations. **Streamlit PPE stays** on `app.*` — no stack switch.

---

## Preconditions

1. `msos_storyboard_visual_parity_v1` **COMPLETE**.
2. Visual parity evidence screenshots checked (or deviations documented).

---

## Acceptance

1. [`docs/DEPLOY/MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md) updated with operator steps run on VPS.
2. `msos_web` service deployed; apex serves Next.js MSOS routes.
3. Research beta CTA on homepage uses `PPE_RESEARCH_OFFER_*` env (same pattern as demo Streamlit).
4. Evidence doc operator check-in boxes completed or honestly blocked with reason.
5. Closeout triggers phone **check-in** ntfy (see `ppe_progress_notify.py`).

## Not now

- Port PPE to React/Next
- Custom auth server
- Paid billing automation

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-PublicLaunchV1-Control-Slice001** | EVIDENCE | CONTROL | Charter |
| **MSOS-PublicLaunchV1-Platform-Slice002** | EVIDENCE | PLATFORM | VPS deploy + Caddy |
| **MSOS-PublicLaunchV1-Product-Slice003** | PRODUCT | MSOS_UI | Research beta CTA |
| **MSOS-PublicLaunchV1-Witness-Slice004** | EVIDENCE | CONTROL | URL witness |
| **MSOS-PublicLaunchV1-Closeout-Slice005** | EVIDENCE | CONTROL | Closeout + check-in |
