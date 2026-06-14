# MSOS production wiring v1

**Controlling canon:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) (P3 distribution) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**Prior chapter:** [`SPRINT_MSOS_PUBLIC_DEMO_LAUNCH_V1.md`](SPRINT_MSOS_PUBLIC_DEMO_LAUNCH_V1.md)  
**SELECTION:** [`POST_MSOS_PRODUCTION_WIRING_V1_SELECTION.md`](POST_MSOS_PRODUCTION_WIRING_V1_SELECTION.md)  
**Priority:** **HIGH**  
**Baseline:** **`main`**

---

## Sprint intent

Close the gap between **pretty MSOS shell** (apex Next.js) and **working product walkthrough**: sign-in path, live PPE embed, env-driven CTAs, and navigation/buttons wired to real routes or documented external targets. **Streamlit PPE stays authoritative on `app.*`** — no math port, no custom auth server.

Operator goal: a visitor on `marketstructureos.com` can sign in to the real lab, open Strategy Lab with live PPE when env/proxy is set, and use CTAs that actually go somewhere honest.

---

## Preconditions

1. `msos_public_demo_launch_v1` **COMPLETE** (apex deploy path exists).
2. P4 embed boundary in `apps/msos-web/` (`PpeEmbedBoundary`) on `main`.
3. Cloudflare Access on `app.marketstructureos.com` unchanged ([`RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](../DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md)).

---

## Acceptance

1. **Sign in** on public nav links to private app URL (`PPE_PRIVATE_APP_URL` / `NEXT_PUBLIC_MSOS_SIGN_IN_URL` — default `https://app.marketstructureos.com`).
2. **Research beta CTA** on homepage reads `PPE_RESEARCH_OFFER_*` (same pattern as Streamlit demo).
3. **Strategy Lab** embed loads live Streamlit when `NEXT_PUBLIC_PPE_EMBED_URL` is set at `msos_web` build; degraded state when unset.
4. **Platform:** `docker-compose.yml` passes embed + offer env to `msos_web`; Caddy documents embed/proxy path per ADR; [`docs/DEPLOY/MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md) operator steps updated.
5. **Shell navigation:** public nav + app sidebar dead spans replaced with real `Link`/`href` to chartered routes (Command Center, Strategy Lab, Monitor, History, Learn); disabled items stay honest.
6. **Honest boundaries:** Command Center KPIs/theses remain fixture until [`msos_user_state_v1`](PHASE_CHAPTER_BACKLOG.json) — labels unchanged.
7. Pytest witness for sign-in href, CTA when env set, embed boundary; evidence doc operator checklist.

## Not now

- Command Center / history fed from snapshot DB (follow-on `msos_user_state_v1`)
- Custom auth server or in-app Google login
- Port PPE math to TypeScript
- Live execution, billing automation
- Cloudflare Access policy edits on VPS (document extension steps; operator applies in Cloudflare dashboard)

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-ProdWireV1-Control-Slice001** | EVIDENCE | CONTROL | Charter + queue align |
| **MSOS-ProdWireV1-Product-Slice002** | PRODUCT | MSOS_UI | Sign-in, CTA, nav/button wiring |
| **MSOS-ProdWireV1-Platform-Slice003** | EVIDENCE | PLATFORM | Compose/Caddy/env + deploy docs |
| **MSOS-ProdWireV1-Witness-Slice004** | EVIDENCE | CONTROL | pytest + evidence checklist |
| **MSOS-ProdWireV1-Closeout-Slice005** | EVIDENCE | CONTROL | Chapter close + operator check-in |
