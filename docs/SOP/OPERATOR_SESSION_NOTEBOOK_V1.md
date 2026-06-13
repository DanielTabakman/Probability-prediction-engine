# Operator session notebook v1

**Purpose:** Mobile **step-by-step** guide for live trader demos — context, goals, script, questions — advances as you tap **Done → next**. Content updates via JSON in the repo (no code change required for copy edits).

**Not for testers** — operator-only; `noindex` on deployed pages.

---

## Use on your phone

| Method | URL / path |
|--------|------------|
| **Live (after deploy)** | `https://marketstructureos.com/session.html` |
| **Offline pair** | [`assets/operator_session_notebook.html`](assets/operator_session_notebook.html) + [`assets/session.json`](assets/session.json) in the same folder |

**Add to Home Screen** (iPhone Share / Android Add to Home screen) for one-tap access in the room.

**Legacy cue card:** [`assets/operator_cue_card.html`](assets/operator_cue_card.html) — static panic sheet; session notebook supersedes for full walkthrough.

---

## How it works

1. One **step** on screen: what it is · what you're trying to do · do / say / ask.
2. **Your notes** per step saved in phone `localStorage`.
3. **Done → next** advances progress (stored on phone).
4. **Panic** overlay anytime.
5. **End:** copy-paste row for [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) § MSOS P8.

Progress does **not** sync to the server in v1 — only your phone. Export via copy at end of session.

---

## Update the walkthrough (steward)

Edit **canonical JSON** only:

[`assets/operator_session_notebook.json`](assets/operator_session_notebook.json)

Then copy to deploy surface:

```bash
copy docs\SOP\assets\operator_session_notebook.json apps\msos-web\public\session.json
```

Commit both paths. Deploy MSOS web — phones load fresh JSON on next open (cache-busted fetch).

### Step fields

| Field | Meaning |
|-------|---------|
| `context` | What this step **is** (for you) |
| `goal` | What you're **trying to learn or achieve** |
| `do` | Mechanical actions on laptop |
| `say` | Words to read aloud |
| `ask` | Question to tester (flips pressure) |
| `skip` | Optional deferral |

Bump `version` or `updated` in JSON when you change steps materially.

---

## Related

- [`FOUNDER_OPERATOR_CRIB_SHEET_V1.md`](FOUNDER_OPERATOR_CRIB_SHEET_V1.md)
- [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md)
- [`STEWARD_VALIDATION_GUIDE_V1.md`](STEWARD_VALIDATION_GUIDE_V1.md)
