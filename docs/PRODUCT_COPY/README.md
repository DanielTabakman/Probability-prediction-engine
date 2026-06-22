# MSOS product copy (packets + content files)

**Process:** [`docs/SOP/MSOS_COPY_AGENT_V1.md`](../SOP/MSOS_COPY_AGENT_V1.md) · **Voice canon:** [`docs/SOP/MSOS_PUBLIC_COPY_V1.md`](../SOP/MSOS_PUBLIC_COPY_V1.md)

Copy agent drafts live in **`packets/`**. Approved strings ship in **`apps/msos-web/src/content/`**. BUILD agent wires components to content files.

---

## Start a copy session

Say **"let's work on copy"** in Cursor — agent loads:

| Layer | Doc |
|-------|-----|
| 0 — Vision | [`LAYER_0_VISION_AND_PRINCIPLES.md`](LAYER_0_VISION_AND_PRINCIPLES.md) |
| 0b — Conversion | [`LAYER_0_CONVERSION_FRAMEWORK.md`](LAYER_0_CONVERSION_FRAMEWORK.md) |
| 1 — Pages | [`LAYER_1_PAGE_CATALOG.md`](LAYER_1_PAGE_CATALOG.md) |
| Handoff | [`HANDOFF_2026-06-22.md`](HANDOFF_2026-06-22.md) |

Full index: [`COPY_CONTEXT_INDEX.json`](COPY_CONTEXT_INDEX.json)

---

## Surface status

| Surface | Packet | Content file | Status | Notes |
|---------|--------|--------------|--------|-------|
| homepage | [`packets/homepage.v2.md`](packets/homepage.v2.md) (approved; supersedes v1) | [`../apps/msos-web/src/content/homepage.ts`](../apps/msos-web/src/content/homepage.ts) | approved | h1 v1 + CTA Try the lab |
| public-nav | [`packets/public-nav.v1.md`](packets/public-nav.v1.md) | [`../apps/msos-web/src/content/publicNav.ts`](../apps/msos-web/src/content/publicNav.ts) | approved | Monitor · Open Command Center |
| command-center | — | inline components | draft needed | Charter copy packet next |
| strategy-lab | — | fixtures + components | draft needed | |
| monitor | — | `monitoringFixtures.ts` | draft needed | |
| history | — | components | draft needed | |
| learn | — | `ConclusionContent.tsx` | draft needed | Vision / conclusion route |
| shared | — | [`publicCopy.ts`](../apps/msos-web/src/lib/publicCopy.ts) | approved | Footers, degraded paths |

Update this table when a packet moves to `approved` or a new surface is chartered.

**Continuing from BUILD/UX thread (2026-06-22):** read [`HANDOFF_2026-06-22.md`](HANDOFF_2026-06-22.md) — homepage done; next: `public-nav` → `strategy-lab` → `command-center`.

---

## Operator commands (copy thread)

- **“Draft homepage v2”** — new packet version, keep v1 until approved
- **“Audit banned terms”** — run validator, list fixes by surface
- **“Promote homepage to content”** — write `content/*.ts`, mark packet approved
- **“Implement on site”** — hand off to BUILD thread (components import content)

---

## Packets directory

- [`packets/_TEMPLATE.md`](packets/_TEMPLATE.md) — blank starter
- [`packets/homepage.v1.md`](packets/homepage.v1.md) — current homepage canon
