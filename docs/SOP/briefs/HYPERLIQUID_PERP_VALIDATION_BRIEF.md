# Hyperliquid / HYPE perp — validation brief (v0)

**Purpose:** Capture operator customer signal for Hyperliquid perp traders — parallel to NVIDIA LEAPS brief.  
**Program:** [`PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md`](../PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md)  
**Status:** Signal logged 2026-06-30 — interviews optional; product slice chartered.

## Customer signal (summary)

Operator spends recurring time with people who trade **HYPE on Hyperliquid via perps**, not listed options. They want help understanding **how to express a directional view** without manual venue/tab hopping — aligned with Exposure menu (“how do I get long HYPE?”), not Strategy Lab implied distributions.

## What we would test (lightweight)

1. **Show** `/exposure?asset=HYPE` with Live perp mark + funding (after v1 BUILD).
2. **Ask** 1–2 HL traders: “Is this enough to compare perp vs spot/options elsewhere, or do you need funding history / basis?”
3. **Price probe (optional):** bundled in research beta vs standalone HL legibility call.

## What v1 proves (after BUILD)

- Honest **Live** perp path on Exposure menu — no fake options, no execution.
- HYPE in catalog picker alongside BTC/ETH/SOL (registry enabled row).
- Copy: paths for comparison only; funding/liquidation risks surfaced.

## What v1 does not prove

- Execution on Hyperliquid
- HYPE options (Derive/PowerTrade)
- Strategy Lab distribution chart for HYPE

## Interpretation for roadmap

| Finding | Implication |
|---------|-------------|
| Strong pull for HL legibility | Prioritize v2 (funding history, short perp) |
| “Just need mark + funding on a card” | v1 sufficient; log in validation checks |
| Demand is execution | **Stop** — separate SELECTION post-validation; not v1 |

## Log result

Update [`VALIDATION_REALITY_CHECKS.md`](../VALIDATION_REALITY_CHECKS.md) **Hyperliquid / HYPE perp** row after first demo or steward review.

**Steward note (2026-06-30):** Brief + program SELECTION merged; BUILD queued as P2 side channel.
