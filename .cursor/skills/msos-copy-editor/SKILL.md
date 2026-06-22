---
name: msos-copy-editor
description: >-
  Writes and revises MSOS visitor-facing website copy (headlines, CTAs, empty states,
  metadata) per MSOS_PUBLIC_COPY_V1. Use when the user asks for website copy, copy agent,
  marketing text, homepage wording, trader-facing UI strings, or copy review for msos-shell.
---

# MSOS copy editor

## Quick start

1. Read [`docs/SOP/MSOS_PUBLIC_COPY_V1.md`](docs/SOP/MSOS_PUBLIC_COPY_V1.md)
2. Read [`docs/SOP/ACTIVE_PRODUCT_DIRECTION.json`](docs/SOP/ACTIVE_PRODUCT_DIRECTION.json) (`northStar`)
3. Read [`docs/PRODUCT_COPY/SURFACE_INVENTORY.json`](docs/PRODUCT_COPY/SURFACE_INVENTORY.json)
4. Draft in [`docs/PRODUCT_COPY/packets/`](docs/PRODUCT_COPY/packets/) using [`docs/SOP/COPY_PACKET_TEMPLATE.md`](docs/SOP/COPY_PACKET_TEMPLATE.md)
5. Run `python scripts/validate_msos_public_copy.py`

Full process: [`docs/SOP/MSOS_COPY_AGENT_V1.md`](docs/SOP/MSOS_COPY_AGENT_V1.md)

## Scope

| Do | Don't |
|----|-------|
| Packets + `apps/msos-web/src/content/*.ts` | `components/`, PPE math, relay |
| `publicCopy.ts` when footers/degraded in scope | Invent copy inside BUILD slices |
| Banned-term validation | Over-promise unshipped features |

## Surfaces (pick one per session)

See [`docs/PRODUCT_COPY/README.md`](docs/PRODUCT_COPY/README.md). Common ids: `homepage`, `public-nav`, `command-center`, `strategy-lab`, `monitor`, `history`, `shared`.

## Promotion rule

Update `content/*.ts` only when operator approves or task says **promote to content**. Set packet YAML `status: approved`.

## Report footer (every turn)

```text
COPY AGENT REPORT
- Surface: …
- Packet: … (status: …)
- Content file: … (updated: …)
- Validator: PASS|FAIL
- Operator action: …
```

## Additional resources

- Launch prompt: [`docs/CONTROL_PLANE/PROMPTS/COPY_AGENT_LAUNCH_PROMPT.md`](docs/CONTROL_PLANE/PROMPTS/COPY_AGENT_LAUNCH_PROMPT.md)
- BUILD handoff: cite `COPY_PACKET` + `CONTENT_FILE` in BUILD packet per [`docs/SOP/BUILD_PACKET_TEMPLATE.md`](docs/SOP/BUILD_PACKET_TEMPLATE.md)
