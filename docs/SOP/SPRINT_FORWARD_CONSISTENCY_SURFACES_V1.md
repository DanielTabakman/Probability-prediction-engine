# Forward Consistency surfaces v1

**Program:** [`FORWARD_CONSISTENCY_PROGRAM_V1.md`](FORWARD_CONSISTENCY_PROGRAM_V1.md)  
**SELECTION:** [`POST_FORWARD_CONSISTENCY_SURFACES_V1_SELECTION.md`](POST_FORWARD_CONSISTENCY_SURFACES_V1_SELECTION.md)  
**Blocked until:** `forward_consistency_bybit_v1` **COMPLETE**

---

## Sprint intent

Surface the same JSON contract on **secondary MSOS routes** without duplicating math: Options Horizon forward context strip + Command Center glance (counts / top WATCH).

---

## Acceptance

1. Horizon: expiry-aligned forward consistency summary (read-only fetch).
2. Command Center: optional strip — e.g. “0 POSSIBLE_ARB across enabled assets” (best-effort cache).
3. External JSON contract stable for future Agenomics consumer (document only).
4. MSOS witness + screenshot note in evidence.

---

## Not now

- Agenomics.xyz embed implementation
- Monitor push alerts
- Archive / history
