# MVP1 mobile research demo v1 — SELECTION (pending)

**Chapter:** `mvp1_mobile_research_demo_v1`  
**Priority:** **MEDIUM** · **Playbook tier:** **P3** (distribution)  
**Sprint:** `SPRINT_MVP1_MOBILE_RESEARCH_DEMO_V1.md` (charter when dependency closes)  
**Relay plan:** `PHASE_PLANS/mvp1_mobile_research_demo_v1_relay.json` (not created yet)

## Status

**NOT SELECTED** — **blocked** until **`msos_public_demo_launch_v1` COMPLETE**.

After public demo launch closeout, charter the relay plan and run:

```bash
python scripts/ppe_queue_insert_after.py \
  --chapter-id mvp1_mobile_research_demo_v1 \
  --after-plan docs/SOP/PHASE_PLANS/msos_public_demo_launch_v1_relay.json \
  --apply
```

## Intent

Phone-friendly **research demo** path for the public Streamlit implied lab: single-column story (distribution summary → chart → MVP1 output → disagreement), inline controls, 3-minute operator script. Display-only — no PPE math port.

## First slice (at charter)

`MVP1-MobileDemo-Control-Slice001`

## Operator

If this chapter stays blocked (missing relay plan, dependency, or focus gate), the loop **skips to the next selectable chapter** and sends an **ntfy** ping — see [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md) § Queue skip and continue.
