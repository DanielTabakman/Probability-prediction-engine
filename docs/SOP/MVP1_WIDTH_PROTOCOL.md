# MVP1 paper protocol — ATM width disagreement (v0)

**Protocol, not proven edge.** For operator discipline and evidence-clock cases.

## When to log a case

All must hold on a **usable** run (`data_quality=usable` in verification):

- Classification suggests **market too wide** or **market too narrow** vs reference
- `primary_output_state` is **candidate** or **watch_only**
- Breeden–Litzenberger path computed (or belief overlay on with valid params)

## Protocol (short-vol family bias example)

**Trigger:** Market ATM width materially **above** benchmark at selected expiry; usable data; M_ratio above floor.

**Expression family (illustrative):** short-vol family — not an exact ticket.

**Action:** Freeze evaluation before outcome. Optionally paper-track mentally; no live trade required.

**Review horizon:** Selected expiry date.

**Falsification:** Width gap compresses toward benchmark by horizon, or data quality degrades below usable.

**Review question:** Did width move in the direction implied by the thesis (too wide → compress) by review time?

## Inverse (long-vol family bias)

**Trigger:** Market ATM width materially **below** benchmark; same gates.

**Review question:** Did width expand or reprice in the direction implied by “too narrow”?

## What this is not

- Not a claim of positive expected value
- Not autonomous execution
- Not multi-asset or NVIDIA automation

Use [MVP1_OPERATOR_RITUAL.md](MVP1_OPERATOR_RITUAL.md) for the freeze/review mechanics.
