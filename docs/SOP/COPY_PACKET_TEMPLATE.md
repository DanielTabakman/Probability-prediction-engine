# Copy packet template (MSOS public surfaces)

Use for **copy agent** output. One packet per surface revision. BUILD agent implements from **approved** packets only.

**Canon:** [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) · [`MSOS_COPY_AGENT_V1.md`](MSOS_COPY_AGENT_V1.md)

---

## Front matter (required)

```yaml
---
surface: homepage          # id from SURFACE_INVENTORY.json
version: 1                 # bump on each revision
status: draft              # draft | review | approved | superseded
content_file: apps/msos-web/src/content/homepage.ts
author: copy-agent
as_of: 2026-06-22
north_star: >              # paste from ACTIVE_PRODUCT_DIRECTION.json when relevant
  See what BTC options imply, where you disagree, and what payoff fits — in under 15 seconds.
notes: ""                  # operator feedback, open questions
---
```

---

## Packet body

### Audience reminder

One line: who reads this surface and what they need in one pass.

### Strings

Group by UI region. Use stable **keys** that match the content file export.

```markdown
#### hero.eyebrow
For traders with a market view

#### hero.h1
Turn your market thesis into a trade you can reason about.

#### hero.body
Market Structure OS helps traders compare market-implied probabilities with their own view,
locate meaningful disagreement, and explore structures that fit the thesis — without hiding
the assumptions.
```

### CTAs

| key | label | href note |
|-----|-------|-----------|
| hero.primaryCta | Explore the platform | Strategy Lab route |
| hero.secondaryCta | Open Command Center | Command Center route |

### Metadata (when applicable)

```markdown
#### metadata.title
Market Structure OS

#### metadata.description
Compare your market thesis with what options imply — explore structures without hiding assumptions.
```

### Before → after (optional)

Only for revisions, not first draft.

| key | before | after | why |
|-----|--------|-------|-----|
| hero.h1 | … | … | shorter, trader verb |

---

## Copy agent checklist (before marking `review`)

1. [ ] Every string read aloud — new BTC options trader test
2. [ ] No banned terms (run `python scripts/validate_msos_public_copy.py`)
3. [ ] Non-advisory: no buy/sell, no “AI recommends”
4. [ ] Product hierarchy correct (MSOS → Strategy Lab → Probability Engine on homepage)
5. [ ] Live vs demo honest where relevant
6. [ ] Keys align with target `content/*.ts` export

## Operator checklist (before `approved`)

1. [ ] Tone matches brand — would you show this to a trader friend?
2. [ ] Nothing over-promises shipped features
3. [ ] Approve or leave inline `notes:` for next draft
