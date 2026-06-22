# MSOS copy agent v1

**Plane:** CONTROL-PLANE + PRODUCT-PLANE · **Layer:** `msos-shell` (visitor copy only)

**Canon:** [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) · **Skill:** [`.cursor/skills/msos-copy-editor/SKILL.md`](../../.cursor/skills/msos-copy-editor/SKILL.md) · **Launch prompt:** [`COPY_AGENT_LAUNCH_PROMPT.md`](../CONTROL_PLANE/PROMPTS/COPY_AGENT_LAUNCH_PROMPT.md)

---

## Purpose

A **dedicated copy agent** writes and revises MSOS visitor-facing text so the operator does not draft every string by hand. The copy agent **does not** implement React, routes, or PPE wiring — it ships **approved words** into content files and copy packets; the BUILD agent wires them.

**Auto-activation:** Say *"let's work on copy"* in any Cursor thread — skill `msos-copy-editor` and rule `.cursor/rules/msos-copy-agent.mdc` load **layered context** (vision → pages → strings). No paste required.

---

## Context layers (reliable anchor in the weeds)

| Layer | Artifact | When |
|-------|----------|------|
| **0 — Vision** | [`LAYER_0_VISION_AND_PRINCIPLES.md`](../PRODUCT_COPY/LAYER_0_VISION_AND_PRINCIPLES.md) | Every copy session — north star, JTBD, voice, hierarchy |
| **1 — Pages** | [`LAYER_1_PAGE_CATALOG.md`](../PRODUCT_COPY/LAYER_1_PAGE_CATALOG.md) | Page purpose, regions, what's on each route |
| **1b — Handoff** | [`HANDOFF_2026-06-22.md`](../PRODUCT_COPY/HANDOFF_2026-06-22.md) | Shipped PRs, priority queue, product-truth limits |
| **2 — Surface** | [`SURFACE_INVENTORY.json`](../PRODUCT_COPY/SURFACE_INVENTORY.json) + [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) | Surface selected — files + voice rules |
| **3 — Strings** | [`packets/`](../PRODUCT_COPY/packets/) + [`content/*.ts`](../apps/msos-web/src/content/) | Specific headline, CTA, or panel copy |

Index: [`COPY_CONTEXT_INDEX.json`](../PRODUCT_COPY/COPY_CONTEXT_INDEX.json)

**Conversation flow:** Discuss Layer 0–1 freely; drop to Layer 3 only when drafting or revising specific strings. Tie every weed back to region job (Layer 1) + principle (Layer 0).

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

**Easiest:** open any thread and say **"let's work on copy"** — agent bootstraps layers 0–1 and asks what page to focus on.

Or:

1. Open a **dedicated Cursor thread** (not the relay BUILD thread).
2. Paste [`COPY_AGENT_LAUNCH_PROMPT.md`](../CONTROL_PLANE/PROMPTS/COPY_AGENT_LAUNCH_PROMPT.md) or invoke skill **`msos-copy-editor`**.
3. Agent reads Layer 0 → Layer 1 → handoff automatically.
4. Discuss page purpose or name a surface (e.g. `strategy-lab`, `command-center`).
5. When happy with a draft, say **promote to content** — agent updates `content/*.ts` and marks packet `approved`.

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
