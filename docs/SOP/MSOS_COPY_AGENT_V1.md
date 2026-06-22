# MSOS copy agent v1

**Plane:** CONTROL-PLANE + PRODUCT-PLANE · **Layer:** `msos-shell` (visitor copy only)

**Canon:** [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) · **Skill:** [`.cursor/skills/msos-copy-editor/SKILL.md`](../../.cursor/skills/msos-copy-editor/SKILL.md) · **Launch prompt:** [`COPY_AGENT_LAUNCH_PROMPT.md`](../CONTROL_PLANE/PROMPTS/COPY_AGENT_LAUNCH_PROMPT.md)

---

## Purpose

A **dedicated copy agent** writes and revises MSOS visitor-facing text so the operator does not draft every string by hand. The copy agent **does not** implement React, routes, or PPE wiring — it ships **approved words** into content files and copy packets; the BUILD agent wires them.

---

## Roles

| Role | Owns | Does not |
|------|------|----------|
| **Copy agent** | Voice, headlines, CTAs, empty states, degraded messages, metadata one-liners | Components, tests, relay, math |
| **BUILD agent** | Import content files, layout, data binding, witnesses | Inventing new marketing copy mid-slice |
| **Operator (human)** | Final taste, “would I show this to a trader friend?” | Hand-editing scattered JSX strings |

---

## Workflow (copy-first → BUILD)

```text
1. Copy agent  →  draft/revise packet in docs/PRODUCT_COPY/packets/
2. Copy agent  →  update apps/msos-web/src/content/<surface>.ts (when approved)
3. Copy agent  →  run validate_msos_public_copy.py (must pass)
4. Operator    →  optional read-aloud / taste pass on packet
5. BUILD agent →  wire content imports if components still inline old strings
6. CI          →  validate_msos_public_copy.py in pushable gate (msos-shell changes)
```

**Rule:** No IDE BUILD slice should invent visitor copy from scratch. BUILD reads the **latest approved packet** or **content file** for that surface.

---

## Where artifacts live

| Path | Purpose |
|------|---------|
| [`docs/PRODUCT_COPY/README.md`](../PRODUCT_COPY/README.md) | Surface index + packet status |
| [`docs/PRODUCT_COPY/SURFACE_INVENTORY.json`](../PRODUCT_COPY/SURFACE_INVENTORY.json) | Machine-readable surface → file map |
| [`docs/PRODUCT_COPY/packets/*.md`](../PRODUCT_COPY/packets/) | Human-readable copy packets (draft → approved) |
| [`docs/SOP/COPY_PACKET_TEMPLATE.md`](COPY_PACKET_TEMPLATE.md) | Packet shape |
| [`apps/msos-web/src/content/*.ts`](../apps/msos-web/src/content/) | Shippable strings BUILD imports |
| [`apps/msos-web/src/lib/publicCopy.ts`](../apps/msos-web/src/lib/publicCopy.ts) | Shared footers, degraded paths, workspace labels |

---

## Starting a copy session (operator)

1. Open a **dedicated Cursor thread** (not the relay BUILD thread).
2. Paste [`COPY_AGENT_LAUNCH_PROMPT.md`](../CONTROL_PLANE/PROMPTS/COPY_AGENT_LAUNCH_PROMPT.md) or invoke skill **`msos-copy-editor`**.
3. Say which surface to work on (e.g. `homepage`, `strategy-lab`, `command-center`) or “audit all surfaces for banned terms.”
4. Review the packet; when happy, tell the copy agent to **promote to content file** and mark packet `status: approved`.

---

## Handoff to BUILD

When copy is approved, BUILD packet includes:

```text
COPY_PACKET: docs/PRODUCT_COPY/packets/<surface>.vN.md
CONTENT_FILE: apps/msos-web/src/content/<surface>.ts
COPY_STATUS: approved
```

BUILD agent verifies components import the content file (no duplicate inline strings).

---

## Validation

```bash
python scripts/validate_msos_public_copy.py
```

Checks visitor-visible paths for banned internal jargon per [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md). Warnings on stale packets do not block; **content/** and **components/** failures block.

---

## When to revise this doc

- New visitor surface chartered (add row to `SURFACE_INVENTORY.json`)
- Copy agent repeatedly misses a banned term → add to validator + `MSOS_PUBLIC_COPY_V1`
- Operator wants copy agent to also draft email/billing copy → extend inventory first

**History:** Copy agent process v1 — 2026-06-22.
