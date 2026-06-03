# MSOS P3 — authenticated shell + Command Center

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) (P3)  
**Visual reference:** [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md) — screen `02_command_center`  
**Stack ADR:** [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**SELECTION:** [`POST_MSOS_P3_COMMAND_CENTER_SELECTION.md`](POST_MSOS_P3_COMMAND_CENTER_SELECTION.md) · [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)  
**Acceleration:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md) — reuse P2 tokens; fixture-only in P3

---

## Sprint intent (P3)

Ship the **authenticated MSOS workspace shell** and **Command Center** overview in `apps/msos-web/` (Next.js App Router), aligned to storyboard v0.6 `02_command_center`, using **fixture/preview data** where backend APIs are not real yet.

## Preconditions (met 2026-06-03)

1. P2 homepage **COMPLETE** on `main` (`apps/msos-web/` public route).
2. Storyboard v0.6 in-repo; [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) **OPEN**.
3. P1 ADR auth model: Cloudflare Access for authenticated routes (no custom auth server in P3).

## Shell acceptance

1. **App shell:** sidebar nav (Command Center, Strategy Lab, Theses, Expression & Execution, Monitor, History) + top bar; reuse P2 design tokens.
2. **Command Center route:** KPI row, Strategy Lab & lens tiles, current-work list, context/alerts panel — narrative matches storyboard **fixture** copy.
3. **Honest labels:** BTC options **Live** (preview); ETH / event markets / perps **Soon** or **Planned**; no live order transmission.
4. **Auth boundary:** document dev stub (e.g. `/app` or `/command-center`) and production Cloudflare Access extension in platform evidence; no fake “logged in” on public homepage.
5. `apps/msos-web/` lint passes; extend [`tests/test_msos_web_homepage.py`](../../tests/test_msos_web_homepage.py) or add command-center witness tests.

## Hard visual closeout

Evidence doc includes screenshot witness vs [`prototype/screens/02_command_center.png`](../VISION/MSOS/storyboard-v0.6/prototype/screens/02_command_center.png); material deviations noted in closeout.

## Not now

- PPE proxy / Strategy Lab embed (P4)
- Real thesis persistence API (P5)
- Live execution or Hyperliquid (deferred per program)

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-P3-Control-Slice001** | EVIDENCE | CONTROL | Charter + queue align |
| **MSOS-P3-Product-Slice002** | PRODUCT | MSOS_UI | Shell layout + Command Center page |
| **MSOS-P3-Platform-Slice003** | EVIDENCE | PLATFORM | Caddy/Access notes for authenticated MSOS routes |
| **MSOS-P3-Witness-Slice004** | EVIDENCE | CONTROL | pytest + command-center witness |
| **MSOS-P3-Closeout-Slice005** | EVIDENCE | CONTROL | Chapter close |
