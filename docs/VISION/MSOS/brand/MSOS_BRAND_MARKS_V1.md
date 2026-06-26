# MSOS brand marks v1

**Status:** active · **As-of:** 2026-06-26

## Shipped (product default)

| Asset | Path | Use |
|-------|------|-----|
| Color emblem | `apps/msos-web/public/brand/msos-mark-color.svg` | Nav, sidebar, favicon, OG default |
| Monochrome emblem | `apps/msos-web/public/brand/msos-mark-mono.svg` | Dark UI chrome, watermarks |
| App icon | `apps/msos-web/src/app/icon.svg` | Next.js tab icon |

**Palette:** teal `#43E7D3`, cyan `#55BBFF` on near-black UI (`#05090F`). Aligns with Storyboard v0.6.

**Shape:** symmetrical market-structure emblem — central spire, stepped vertical bars, angular wing pairs, tapered base.

## Reserved — premium / special tier (not shipped)

**Mark:** pale gold / cream heraldic lockup (symmetrical emblem + **MSOS** + **MARKET STRUCTURE OS** tagline with horizontal rules).

**Intent:** hold for a future **premium product, paid tier, or special edition** — not the default MSOS shell. Do not use in public nav, favicon, or self-serve demo until explicitly chartered.

**When to activate:** steward SELECTION chapter that names tier (e.g. paid entitlement skin, private desk, partner edition) + visual witness in closeout.

**Asset slot:** drop canonical PNG/SVG under `docs/VISION/MSOS/brand/reserved/msos-mark-premium-gold/` when the operator exports the final file from design tooling.

## Rules

- Default customer-facing surfaces use the **teal/cyan** emblem only.
- Premium gold mark requires an explicit product decision — no ad-hoc swaps in `msos-web` without a BUILD slice.
- MSOS must not reimplement PPE math in TypeScript; brand work stays in `apps/msos-web/` and `docs/VISION/MSOS/brand/`.
