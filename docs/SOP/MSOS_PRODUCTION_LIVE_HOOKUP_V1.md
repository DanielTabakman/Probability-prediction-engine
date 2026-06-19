# MSOS production live hookup v1

**Purpose:** Close the gap between **relay chapters marked DONE** and **anyone can use the full site** on `marketstructureos.com`. Code matches the designed plan in [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md); production config and Cloudflare still lag.

**As-of:** 2026-06-19 · **Controlling canon:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) · [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md) · [`RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](../DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md)

**Operator tools:** merge to `main` → **Deploy VPS** GitHub Action · `msos_production_demo_witness.cmd` · [`CONTROL_PLANE_OPERATOR_V1.md`](CONTROL_PLANE_OPERATOR_V1.md)

---

## Deploy plane — GitHub is enough (desktop SSH optional)

You do **not** need laptop SSH for normal agent work.

| Path | Who uses it | What happens |
|------|-------------|--------------|
| **Primary — GitHub → VPS** | Agents + you | PR merges to `main` → [`.github/workflows/deploy-vps.yml`](../../.github/workflows/deploy-vps.yml) SSHs with **repo secrets** (`VPS_HOST`, `VPS_USER`, `VPS_SSH_PRIVATE_KEY`) and runs `git pull` + `docker compose up -d --build`. |
| **One-time bootstrap** | You (once, at home) | [`scripts/setup_vps_deploy_once.ps1`](../scripts/setup_vps_deploy_once.ps1) — deploy key on VPS + secrets in GitHub. After that, agents never touch your laptop. |
| **Optional — desktop SSH** | Emergency only | `ppe_vps_ssh.cmd` — same commands without waiting for a merge. Skip until Windows/password setup is comfortable. |

**Why SSH exists at all:** GitHub Actions *is* SSH — the workflow connects to the VPS on every `main` push. Desktop SSH duplicates that for one-off ops (broken deploy, `.env` tweak before we automate it). Agents ship **code and docs via PR**; the server pulls from GitHub.

**What still needs the VPS filesystem (not in git):** repo-root `.env` on the server (`PPE_RESEARCH_OFFER_URL`, etc.). Optimal fix: add those values as **GitHub Actions secrets** and extend the deploy workflow to write/sync `.env` before `docker compose` (Track 1 below). Until then, one manual `.env` edit on VPS or a `workflow_dispatch` input.

---

## Product stance — full public website (no friends-only cohort)

Steward decision **2026-06-19:** Do **not** run a separate friends/family allowlist. Same experience for everyone who signs in.

| Layer | Decision |
|-------|----------|
| **Audience** | General public — any user who passes Cloudflare Access (Google login). |
| **Entitlements** | **`free` tier by default** on first login ([`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md)). No artificial cripple for v1. |
| **Access policy** | Cloudflare **Allow** for authenticated users (Google IdP), **not** a named-email tester list. |
| **Marketing** | Homepage `/` may stay **public** (ADR) for acquisition; **all product routes** behind Access so APIs get identity headers. |
| **Stripe** | Out of scope until demo is proven (`stripe_operator_prereq` human backlog). |

This matches phases 1–7a already built in repo — we are **turning production on**, not re-designing.

---

## Problem statement

Relay queue shows MSOS phases **DONE**, but production still feels like a fixture walkthrough:

| Symptom | Root cause |
|---------|------------|
| Empty / degraded Command Center & Monitor | Apex traffic is anonymous — no `CF-Access-Authenticated-User-Email` on product APIs |
| Research beta CTA missing | VPS `.env` lacks `PPE_RESEARCH_OFFER_URL` → witness `research_beta_cta` FAIL |
| Stale UI copy | VPS image behind `main` or pre-live-hookup build |
| PPE full lab vs shell split | Snapshots on `app.*`; MSOS shell on apex — by design, but user must sign in on **both** surfaces where Access applies |

**Goal:** A new visitor can discover the site, sign in with Google, use Strategy Lab → save thesis → freeze → see **their** data on Command Center / Monitor / History — same path for everyone.

---

## Acceptance (“fully hooked up”)

1. **Deploy loop** — every `main` merge redeploys VPS; health step in workflow green.
2. **Production env** — research CTA, embed URL, snapshot volume on `msos_web` (see checklist below).
3. **Cloudflare Access** — all MSOS **product routes** on apex; **Allow all authenticated Google users** (not email allowlist).
4. **Identity → data** — workflow store + snapshot reads scoped to `owner_email`.
5. **Witness PASS** — `msos_production_demo_witness` including `research_beta_cta` and signed-in journey checklist.
6. **Honest labels** — no fixture copy where live workflow + snapshots exist.

---

## Optimal implementation order

Execute in this order — minimal rework, matches existing sprint evidence.

### Track 1 — Production env + deploy (platform, mostly GitHub)

**Owner:** Operator one-time + optional PR to automate.

| Step | Action |
|------|--------|
| 1 | Confirm GitHub deploy secrets set ([`GITHUB_ACTIONS_VPS_DEPLOY.md`](../DEPLOY/GITHUB_ACTIONS_VPS_DEPLOY.md)). |
| 2 | On VPS `/opt/marketstructureos/.env` (or future GHA secret sync): |

```bash
PPE_RESEARCH_OFFER_URL=mailto:you@example.com?subject=PPE%20research%20beta
PPE_RESEARCH_OFFER_LABEL=Request research beta access
NEXT_PUBLIC_PPE_EMBED_URL=/ppe-embed
NEXT_PUBLIC_MSOS_SIGN_IN_URL=https://app.marketstructureos.com
```

| 3 | Merge latest `main` (or **Actions → Deploy VPS → Run workflow**) → `docker compose up -d --build msos_web`. |
| 4 | **Follow-up PR (recommended):** extend `deploy-vps.yml` to write `.env` keys from GitHub secrets so agents never need VPS shell. |

### Track 2 — Cloudflare Access (platform, operator UI)

Per [`SPRINT_MSOS_ACCESS_IDENTITY_V1.md`](SPRINT_MSOS_ACCESS_IDENTITY_V1.md) — **production operator steps** that relay code cannot do from repo alone:

1. Zero Trust → Application for `marketstructureos.com` paths:
   - `/command-center`, `/command-center/*`
   - `/strategy-lab`, `/strategy-lab/*`
   - `/monitor`, `/monitor/*`
   - `/history`, `/history/*`
2. **Policy:** Allow — **Include: Everyone** (or Login methods: Google, no email restriction). Same IdP as `app.marketstructureos.com`.
3. Confirm `msos_web` receives `CF-Access-Authenticated-User-Email` (`msosIdentity.ts`).
4. Keep `/` public unless steward later chooses full-site Access.

Document screenshots / policy names in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

### Track 3 — Entitlements on first login (already in repo)

Phase 7a code should grant **`free`** on first authenticated API hit. Verify after Track 2 — no separate cohort setup.

### Track 4 — Production witness + sign-off (evidence)

1. Run `msos_production_demo_witness.cmd` (HTTP checks from any machine).
2. Manual signed-in journey: homepage → sign in → Strategy Lab → freeze on `app.*` → CC → Monitor → History.
3. Update operator row in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

### Track 5 — Product gaps only if witness fails

Queue via `ppe_request.cmd` — do not hand-edit queue. Likely small fixes only; backlog chapters are **DONE**.

---

## Gap map (code vs production)

| Area | Repo | Production gap |
|------|------|----------------|
| MSOS shell + APIs | DONE (phases 1–5) | Access + identity headers on apex |
| PPE embed | Caddy `/ppe-embed` | Confirm build arg + running `app_demo` |
| Workflow + snapshots | volumes + APIs | Needs signed-in user |
| Entitlements | phase 7a DONE | Verify first-login grant live |
| Research CTA | `researchOfferCta.ts` | VPS `.env` + rebuild |
| Strategy Lab shell | embed shell DONE | Deploy + embed env |
| Stripe | deferred | human backlog only |

---

## What agents do vs what you do

| Task | Agent (via GitHub) | You (operator) |
|------|-------------------|----------------|
| Code / docs / witness scripts | PR → merge | Review / merge |
| VPS deploy | Automatic on `main` | Ensure secrets once |
| `.env` on VPS | PR to automate from secrets | Until then: one edit on VPS or wait for Track 1 PR |
| Cloudflare Access policies | Document steps in evidence | Click in Zero Trust UI |
| Google OAuth client | — | Already done for `app.*` |

---

## Promotion / queue

This charter is **operator go-live** for chapters already DONE — not a new product phase.

1. Complete Tracks 1–4.
2. Mark human backlog `msos_production_live_hookup` **done**.
3. If witness finds code bugs: `ppe_request.cmd --chapter-id <fix-chapter> --reason "production witness FAIL: …" --apply`.
4. `ppe_request.cmd reconcile` → read `CONTROL_PLANE_STATUS.json`.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-19 | v1 — charter for production live hookup vs relay-DONE drift |
| 2026-06-19 | v2 — GitHub-first deploy; full public product (no friends-only); optimal track order |
