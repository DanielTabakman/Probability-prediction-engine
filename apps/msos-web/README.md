# MSOS web shell

**Layer:** `msos-shell` ([`docs/SOP/REPO_LAYER_MAP_V1.md`](../../docs/SOP/REPO_LAYER_MAP_V1.md))

Next.js 15 App Router + TypeScript public homepage (MSOS P2). No PPE math in this tree — display only.

## Commands

```bash
npm install
npm run dev
npm run build
npm run lint
```

## Web feedback (research beta)

Public form: `/feedback` and compact panel on `/strategy-lab`.

| Env | Purpose |
|-----|---------|
| `PPE_WEB_FEEDBACK_DIR` | Directory for `ppe_web_feedback.jsonl` (Docker: `/data` volume) |
| `MSOS_OPERATOR_EMAIL` | Cloudflare Access email allowed to view `/operator/feedback` |

Export submissions:

```bash
python scripts/ppe_export_web_feedback.py --markdown
```

## Operator phone cue (founder only)

**Session notebook:** [`docs/SOP/OPERATOR_SESSION_NOTEBOOK_V1.md`](../../docs/SOP/OPERATOR_SESSION_NOTEBOOK_V1.md) — `/session.html` + `/session.json` (step-by-step, advances on phone). Edit [`docs/SOP/assets/operator_session_notebook.json`](../../docs/SOP/assets/operator_session_notebook.json) to update walkthrough.

Legacy `/cue.html` redirects to session notebook. Not linked from site nav; `noindex`. Bookmark on your phone; do not share with testers.

**Stack ADR:** [`docs/SOP/MSOS_P1_STACK_ROUTING_ADR.md`](../../docs/SOP/MSOS_P1_STACK_ROUTING_ADR.md)

**Visual reference:** [`docs/VISION/MSOS/storyboard-v0.6/`](../../docs/VISION/MSOS/storyboard-v0.6/MANIFEST.md) screen `01_home`.
