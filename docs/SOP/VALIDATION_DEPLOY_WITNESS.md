# Validation Chapter — deploy witness (steward fill)

Record post-deploy smoke after **`main`** merge per [DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md) §5.

| Field | Value |
|-------|--------|
| **Date (UTC)** | 2026-05-19 |
| **Git SHA on VPS** | `f6490a7` (Commercial Validation closeout; verify on VPS after `git pull`) |
| **Deploy path** | GitHub Actions on push to `main` / manual §4 |
| **marketstructureos.com** | PASS — Streamlit demo loads (HTTP 200; title **Streamlit** / Probability Engine surface) |
| **app.marketstructureos.com** | PASS — Cloudflare Access login gate present (**App full (snapshots)**); full app behind auth as designed |
| **HTTPS static assets** | PASS — no mixed-content failures observed on demo hostname fetch |
| **Demo operator script** | PASS — prep session; scripted walkthrough per [DEMO_OPERATOR_SCRIPT.md](DEMO_OPERATOR_SCRIPT.md) on public demo URL |

**Notes:** Full-app post-login smoke requires steward credentials; public demo validated without snapshot DB. Re-run §5 after merging Validation Chapter product commits to `main` and VPS `git pull`.

**Steward:** closeout **Validation-Chapter-Deploy-Slice003** — summary copied to [MVP1_FRONTIER.md](MVP1_FRONTIER.md).
