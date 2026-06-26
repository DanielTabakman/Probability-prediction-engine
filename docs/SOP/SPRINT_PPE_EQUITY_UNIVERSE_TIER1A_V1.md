# PPE equity universe tier-1a v1 — relay sprint spec

**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Adapter:** [`PPE_EQUITY_OPTIONS_ADAPTER_ADR.md`](PPE_EQUITY_OPTIONS_ADAPTER_ADR.md)  
**Manifest:** [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml)  
**SELECTION:** [`POST_PPE_EQUITY_UNIVERSE_TIER1A_V1_SELECTION.md`](POST_PPE_EQUITY_UNIVERSE_TIER1A_V1_SELECTION.md)

---

## Sprint intent

Enable **SPY, QQQ, IWM** via existing equity adapter — registry + witness only.

---

## Slice acceptance

| Slice | Deliverable |
|-------|-------------|
| PPE-EqT1a-Control-Slice001 | Charter |
| PPE-EqT1a-Core-Slice002 | Registry merge + per-ticker enable |
| PPE-EqT1a-Witness-Slice003 | pytest + yfinance flake handling |
| PPE-EqT1a-Closeout-Slice004 | Evidence COMPLETE |
