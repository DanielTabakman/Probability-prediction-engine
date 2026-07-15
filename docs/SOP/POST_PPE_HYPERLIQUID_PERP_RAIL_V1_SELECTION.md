# Hyperliquid perp rail v1 — SELECTION

**Chapter:** `ppe_hyperliquid_perp_rail_v1`  
**Program:** [`PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md`](PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md)  
**Parent:** [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md)  
**Relay plan:** [`PHASE_PLANS/ppe_hyperliquid_perp_rail_v1_relay.json`](PHASE_PLANS/ppe_hyperliquid_perp_rail_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_HYPERLIQUID_PERP_RAIL_V1.md`](SPRINT_PPE_HYPERLIQUID_PERP_RAIL_V1.md)  
**Validation hook:** [`briefs/HYPERLIQUID_PERP_VALIDATION_BRIEF.md`](briefs/HYPERLIQUID_PERP_VALIDATION_BRIEF.md)

---

## Status

**SELECTED** 2026-06-30 — operator-approved **P2 side channel**. Does not preempt asset batch wave 1 or spine closeout.

**First slice:** `PPE-HyperliquidPerp-Control-Slice001` remains the historical first slice; it is not currently dispatchable from the READY frontier.

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Customer signal | Operator recurring time with Hyperliquid **perp** traders (HYPE) |
| Product gap | Exposure menu shows `perp_long` as **Planned**; HL traders get no Live path |
| Architecture | Extend `exposure_menu` + new `hyperliquid` venue — **not** options registry batch |
| Perps vs options | **Not a blocker** for exposure path; **blocks** Strategy Lab / wave 1 only |
| Priority | **P2** — parallel to wave 1; charter now, BUILD when slot available |

**Historical prerequisite cleared:** exposure menu v0 is satisfied. **Current reactivation condition:** evidence reconciliation or founder/operator-approved explicit requeue after the issue #5374 audit.

---

## Scope (v1)

1. **`fetch_hyperliquid.py`** — public API: HYPE mark, funding rate, OI (read-only).
2. **Registry row** `HYPE` with `exposure_only: true`, `venue: hyperliquid`.
3. **`perp_long` Live** on `/exposure?asset=HYPE` with honest trust labels.
4. **`ok_perp_only`** status when exposure-only asset has live perp (no options requirement).
5. **Witness** — `probe_hyperliquid_perp.py` or extended probe; not options catalog witness.
6. MSOS picker shows HYPE via catalog (enabled registry row).

---

## Acceptance (chapter)

1. `python scripts/probe_hyperliquid_perp.py --asset HYPE --json` → `ok: true`, mark + funding present.
2. `python scripts/find_exposure_paths.py --asset HYPE --direction long --json` → `perp_long` **Live**, `status: ok_perp_only`.
3. `GET /ppe-display-api/exposure-menu.json?asset=HYPE&direction=long` matches CLI.
4. MSOS `/exposure` — HYPE in picker; perp card shows Live mark/funding; footer unchanged.
5. `witness_asset_catalog.py --asset HYPE` passes **exposure-only** path (no options fetch).
6. Discovery script **not required** before enable (`exposure_only` bypass documented).
7. Gate green; evidence COMPLETE.

---

## Non-goals

- Live execution, wallet connect, or order routing on Hyperliquid
- HYPE options (Derive / PowerTrade adapters)
- Strategy Lab / implied distribution for HYPE
- Asset batch wave 1 manifest row
- BTC/ETH perp on Hyperliquid (HYPE proof only in v1)
- Funding history archive (v2)

---

## Scheduling

| When | Action |
|------|--------|
| **Now (2026-06-30)** | Charter + queue READY — this SELECTION |
| **Parallel** | Wave 1 batches 2–4 continue unchanged |
| **BUILD start** | Blocked after issue #5374 until evidence reconciliation or founder/operator-approved explicit requeue |

---

## Next chapter (defer)

`ppe_hyperliquid_perp_rail_v2` — funding history, short perp, basis vs index; only after v1 witness green + validation brief update.
