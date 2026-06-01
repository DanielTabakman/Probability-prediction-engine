# MSOS P1 — stack / routing ADR (stub sprint)

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) (P1)  
**SELECTION:** After P0 closeout — [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)  
**Output:** [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md) (created in Product slice)

---

## Sprint intent (P1)

Choose the smallest stable implementation path for the MSOS customer-facing surface **without rewriting PPE math**.

## Inventory (required in ADR)

- [`src/viz/`](../../src/viz/) — Streamlit implied lab (current product)
- [`docs/DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](../DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md) — demo vs full app hosts
- Auth: Cloudflare Access on `app.marketstructureos.com`
- Testing: pytest, dual smoke scripts (reference only)

## ADR must decide

1. Frontend root strategy (extend Streamlit vs new shell e.g. Next.js + adapter)
2. Auth model for MSOS shell vs existing Cloudflare Access
3. PPE integration boundary (embed, iframe, API — lowest risk)
4. Deploy path for new surfaces vs existing VPS Docker stack
5. P2 unblock criteria (explicit)

## Acceptance (chapter)

1. `MSOS_P1_STACK_ROUTING_ADR.md` committed with explicit decision.
2. MSOS frontier updated with P2 status (still blocked until storyboard).
3. Full pytest green before closeout.

## Not now

- Homepage UI (P2)
- Porting PPE calculations to TypeScript

---

## Slice map (stub)

- **Control-Slice001** — charter align
- **Product-Slice002** — write ADR (`local-agent`)
- **Witness-Slice003** — pytest + ADR checklist
- **Closeout-Slice004** — chapter close
