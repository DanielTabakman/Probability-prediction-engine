# Options Horizon chart display contract v1

**Product:** Options Horizon  
**As-of:** 2026-06-27  
**Status:** Contract — implement in `horizon_chart_polish_v1`  
**Payload:** `GET /ppe-display-api/horizon/chart.json` (existing)

---

## Purpose

Define the **MSOS chart UX** that closes the gap between the v1 functional spike and the milestone north star. All distribution math stays in Python; MSOS renders pre-computed arrays only.

---

## Layout (target)

```
┌─────────────────────────────────────────────────────────────┐
│ Header: asset, as-of, expiry selector, simulation-only badge │
├──────────────────────────────┬──────────────────────────────┤
│ Time × price chart           │ Implied at expiry (panel)    │
│ • spot line + volume bars    │ LabeledDistributionChart     │
│ • forward curve (futures)    │ (prices_usd + pdf_pct)       │
│ • implied contour at expiry  │ spot marker, axis + legend   │
│ • thesis region box          │                              │
│ • grid + axis ticks + legend │                              │
└──────────────────────────────┴──────────────────────────────┘
│ Region preview: implied mass % · suggested next step (sim)  │
│ Open in Strategy Lab (deep-link)                            │
└─────────────────────────────────────────────────────────────┘
```

On narrow viewports the implied panel stacks below the time×price chart.

---

## Time × price pane

| Layer | Source field | Render |
|-------|--------------|--------|
| Historical spot | `historical.series[].close_usd` | Line + optional volume bars |
| Forward curve | `forward.curve[]` | Dashed line + expiry markers |
| Implied at expiry | `implied.prices_usd` + `implied.pdf_pct` | Contour or fan anchored at `implied.expiry_date` on time axis (display-only mapping; no TS density math) |
| Now | client clock | Vertical dashed line |
| Region | RegionIntent box | Semi-transparent fill + border |

**Axis parity:** reuse `chartAxisDisplay.ts` helpers (`buildPriceAxisTicks`, `CHART_AXIS_STYLE`, `formatAxisPrice`) — same visual language as Strategy Lab expression charts.

**Legend:** spot · volume · forward · implied at expiry · thesis region.

---

## Expiry selector

- Client calls chart API with `?expiry_ts=` when user picks a different Deribit expiry.
- Default: nearest expiry from initial payload (unchanged server behavior).
- Expiries list: from existing chart payload or a lightweight follow-on field if added server-side; v1 may derive from `forward.curve` expiry dates plus `implied.expiry_ts`.

---

## Implied panel

- Reuse `LabeledDistributionChart` with `payload.implied.prices_usd` and `payload.implied.pdf_pct`.
- Title: `Options-implied at {expiry_date}`.
- `spotUsd` from `payload.spot_usd`.

---

## Region + bridge (unchanged behavior, better chrome)

- Drag box on time×price pane → region preview API → implied mass %.
- Copy: "Thesis region," "implied mass in region," "suggested expression (simulation)" — per [`REGION_INTENT_SCHEMA_V1.md`](REGION_INTENT_SCHEMA_V1.md).
- Strategy Lab deep-link: `?asset=&expiry=` (existing).

Optional v1 polish slice: one-line **suggested expression family** label (read-only) when display API or Strategy Lab suggestion payload is already available — never order language.

---

## Explicit non-goals (this contract)

- Replay scrubber (`horizon_replay_scrubber_v1`)
- Liquidation overlay
- Multi-asset picker (BTC wedge until tradeable-universe tier promotes Horizon)
- TypeScript distribution / implied-mass math
- Execution or broker copy

---

## Witness (chapter close)

- [ ] `/options-horizon` shows grid + labeled axes + legend
- [ ] Implied PDF visible (panel and/or expiry contour on main chart)
- [ ] Expiry selector refreshes chart without full page reload
- [ ] Region draw → implied mass → Strategy Lab link still works
- [ ] No execution language in UI
