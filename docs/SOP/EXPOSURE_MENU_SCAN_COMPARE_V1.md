# Exposure menu — scan, compare, and fit lenses v1

**Parent program:** [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md)  
**Module ID:** `exposure_menu`  
**As-of:** 2026-06-30  
**Status:** **LIVE** — scan/compare shipped in product (2026-06-30)

---

## Problem

v0 ships a **flat card grid**. Paths are sorted correctly in the engine, but traders cannot **scan** the ladder (spot → defined → aggressive → planned) or **compare** two paths side-by-side. Goal-fit language (“I want light capital” / “defined max loss”) is missing — without becoming a recommender.

---

## North star (unchanged)

**Compare paths, not picks.** Fit lenses **highlight** alignment with a user priority. They do **not** rank, auto-select, or imply edge.

Semantic rule: [`SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md) §10 — **fit, not recommendation**.

---

## Scope (v1 — keep it simple)

| In scope | Out of scope |
|----------|----------------|
| Visible **sections** matching catalog `sort_order` | Natural-language intake |
| **Summary cards** (metadata chips; pros/cons collapsed) | 3+ path compare matrix |
| **Six fit lens chips** (highlight + dim; all paths stay visible) | ML scoring or “best trade” banner |
| **Two-path compare** drawer (pin A vs B) | Re-sorting grid by fit lens |
| One-line **legs** on options paths when engine fills them | New quant paths or strike optimization |
| Boundary fields: `sort_group`, `fit_lenses[]`, optional `sections[]` | Workflow save (T4 — defer) |

**Default path:** sections + summary cards alone already fix scan. Fit chips and compare are **additive**, not required for first merge.

---

## Scan — section ladder

Mirror [`config/exposure_path_catalog.yaml`](../../config/exposure_path_catalog.yaml) `sort_order`. Section headings (user-facing):

| `sort_group` | Section title | One-line subcopy |
|--------------|---------------|------------------|
| `spot_equity` | **Spot — simplest** | No expiry; full delta on the underlying |
| `listed_options_defined_risk` | **Defined-risk options** | Premium or net debit caps worst case |
| `listed_options_leaps` | **Longer-dated options** | More time; usually higher premium |
| `listed_options_aggressive` | **Timing-sensitive** | More leverage; faster decay |
| `etf_proxy`, `perp` | **Planned — context only** | Not connected yet; shown for honesty |

Empty sections: omit the block (do not show “No paths”).

**Summary card (scan tier):** label, headline, illustrative cost, three chips (`leverage` · `time_bound` · `liquidity`), trust + rail badges, fit pills when present. Pros/cons and full capital shape behind **Details** expander. Options paths: one-line legs when `legs[]` non-empty.

---

## Fit lenses (six priorities)

Deterministic tags on each path in Python — **no new market math**. A path may carry **multiple** tags.

| Lens ID | Chip label | Fits when |
|---------|------------|-----------|
| `simplest` | Simplest | `leverage=none` and `time_bound=none` |
| `defined_risk` | Defined max loss | `leverage=defined` |
| `capital_light` | Light capital | Live path; `cost_hint_usd` in **lowest third** among live paths for this request |
| `upside_leverage` | Upside leverage | `leverage=high` or `sort_group=listed_options_aggressive` |
| `patient` | Patient horizon | `sort_group` contains `leaps` or template `min_horizon_days ≥ 270` |
| `liquid` | Most liquid | `trust_badge=Live` and `liquidity` is `high` or `medium` |

**Short direction only (optional seventh):** `income_style` → **Income-style** when `path_id=cash_secured_put`. Omit from chip row when direction ≠ short.

**Planned paths:** no live fit tags; section copy carries trust.

### Chip interaction

- **None selected:** neutral scan (sections only).
- **One selected:** matching cards normal; others **slightly dimmed** (still visible).
- **No reorder** within sections — preserves simplest-first ladder.
- **No auto-pin** to compare.

Intro copy: *“Highlights paths that align with a priority — fit is not a recommendation.”*

### Names we avoid

| Avoid | Use instead |
|-------|-------------|
| Safest / best | Defined max loss / Simplest |
| Highest reward | Upside leverage |
| Recommended | Fits: … |

---

## Compare — two paths only

1. User **pins** up to **two** paths (toggle on card).
2. Sticky **Compare** bar appears; tap opens drawer with fixed rows:

| Row | Source |
|-----|--------|
| Illustrative cost | `cost_hint_usd` |
| Capital at risk | `capital_shape` (short) |
| Leverage · Time · Liquidity | enum fields |
| Trust | `trust_badge` |
| Structure | `legs[]` one-liner or “—” |
| Fits | `fit_lenses` labels |

No winner column. Footer: same as module footer (comparison only).

**Why two, not three:** keeps mobile layout and cognitive load low; enough for “stock vs spread” or “LEAPS vs near-dated.”

---

## Display boundary additions

Extend `/ppe-display-api/exposure-menu.json` (and CLI report) — MSOS remains display-only.

**Per path (add):**

```json
{
  "sort_group": "listed_options_defined_risk",
  "fit_lenses": ["defined_risk", "capital_light", "patient"]
}
```

**Optional top-level (preferred for dumb UI):**

```json
{
  "sections": [
    {
      "sort_group": "spot_equity",
      "title": "Spot — simplest",
      "subcopy": "No expiry; full delta on the underlying",
      "path_ids": ["long_stock"]
    }
  ],
  "fit_lens_catalog": [
    { "id": "simplest", "label": "Simplest", "tradeoff": "Full spot downside; most capital per unit of delta" }
  ]
}
```

`fit_lens_catalog` can be static in MSOS for v1; engine only computes `fit_lenses[]` per path.

Also export `sort_group` in `ExposurePath.to_dict()`.

---

## BUILD chapter (proposed relay)

**Chapter ID:** `ppe_exposure_menu_scan_v1`  
**Target tier:** T2 (same module; UX depth only)  
**Plane mix:** PRODUCT (PPE_CORE boundary + MSOS_UI)

| Slice | Preset | Deliverable |
|-------|--------|-------------|
| **PPE-ExposureMenuScan-Core-Slice001** | PPE_CORE | `fit_lenses` rules, `sort_group` in `to_dict`, section builder, boundary + CLI tests |
| **PPE-ExposureMenuScan-UI-Slice002** | MSOS_UI | Sectioned layout, summary cards, fit chips (highlight/dim), legs line, Details expander |
| **PPE-ExposureMenuScan-Product-Slice003** | MSOS_UI | Two-path pin + compare drawer |
| **PPE-ExposureMenuScan-Closeout-Slice004** | CONTROL | Evidence, program link, registry note |

**Merge strategy:** Slice 001 alone is shippable (API + sections via client-side group if needed). Slice 002 is the main UX win. Slice 003 can slip one relay beat without blocking 001–002.

---

## Acceptance

1. NVDA long: ≥4 sections visible when paths exist; planned block last.
2. Each live path has ≥0 fit tags; tags stable under pytest fixtures.
3. Fit chip never hides paths; dimming only.
4. Compare drawer works for exactly two pinned paths; clears cleanly.
5. Copy passes semantic guard — no “recommended” / “best trade” in UI strings.
6. Gate green; boundary tests lock new fields.

---

## Small extras (optional — only if cheap)

- **Live path count** in page header: “5 live · 1 planned” (already in payload `live_path_count`).
- **Horizon hint** when `3m`/`12m` active: one status line (“Filtering options expiries to ~3m window”).
- **Empty direction:** honest empty state for neutral (no fake cards).

Do **not** add: comparison export, saved pins, NL intake, or fourth fit dimension UI.

---

## Known gaps — resolution plan

| Gap | Resolution |
|-----|------------|
| **Workflow handoff** (Lab → Expression planner) | Shipped: options cards link “inspect in Strategy Lab” and “structure fit” (`/strategy-lab/expression?asset=`). |
| **Short / neutral sparse** | Short: added `long_put_leaps` + income-style put on equities. Neutral: honest empty copy — hedged catalog deferred. |
| **Universe** | `equity_index` binding for SPY/QQQ/IWM; crypto binding covers BTC/ETH/SOL via registry picker. |
| **Branch / PR** | Ship on a product branch (`product/exposure-menu-scan-v1` or similar); avoid mixed control-plane commits. |
| **Relay closeout** | Optional evidence row when operator runs chapter closeout — not blocking UX. |

---

## Related docs

| Doc | Role |
|-----|------|
| [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md) | Module charter |
| [`MSOS_UX_DESIGN_PHILOSOPHY_V1.md`](MSOS_UX_DESIGN_PHILOSOPHY_V1.md) | One-screen first, progressive disclosure |
| [`PPE_EXPOSURE_MENU_V1_EVIDENCE_STATUS.md`](PPE_EXPOSURE_MENU_V1_EVIDENCE_STATUS.md) | v0 chapter evidence |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-30 | v1 charter — scan sections, six fit lenses, two-path compare |
| 2026-06-30 | Implemented in product — boundary sections/fit_lenses + MSOS UI |
