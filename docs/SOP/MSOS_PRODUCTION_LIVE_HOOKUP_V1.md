# MSOS production live hookup v1

**Purpose:** Close the gap between **relay chapters marked DONE** and **testers can actually use the site** on `marketstructureos.com`. This is the steward charter for “show people what it is,” not a fixture walkthrough.

**As-of:** 2026-06-19 · **Controlling canon:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) · [`RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](../DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md)

**Operator tools:** `ppe_vps_ssh.cmd` · `msos_production_demo_witness.cmd` · [`CONTROL_PLANE_OPERATOR_V1.md`](CONTROL_PLANE_OPERATOR_V1.md)

---

## Problem statement

The MSOS relay queue drained phases 1–6 (and 7a) as **BUILD-complete**, but production still behaves like a **partial demo**:

| Symptom | Why testers feel it |
|---------|---------------------|
| Anonymous apex traffic | Monitor/CC APIs have no `CF-Access-Authenticated-User-Email` → empty or degraded feeds |
| Research beta CTA missing | VPS `.env` lacks `PPE_RESEARCH_OFFER_URL` → witness `research_beta_cta` FAIL |
| Strategy Lab side panels | `strategyLabFixtures.ts` still drives metrics copy when embed is live |
| Stale deploy | VPS image behind `main` → old fixture strings on monitor pages |
| Sign-in only on `app.*` | Full PPE snapshots live on `app.marketstructureos.com`; apex MSOS shell is public |

**Goal:** A **friends-first cohort** can sign in, save a thesis, freeze in PPE, and see **their** data on Command Center / Monitor / History — with honest labels where data is still preview-only.

---

## What “fully hooked up” means (acceptance)

1. **VPS stack current** — `main` deployed; `docker compose ps` healthy.
2. **Env wired** — research CTA, embed URL, snapshot volume mounted read-only on `msos_web`.
3. **Identity on product routes** — Cloudflare Access on apex paths that need user scope (phase 4b intent).
4. **Signed-in journey works** — witness script PASS on production URLs (including `research_beta_cta`).
5. **Honest UX** — no fixture copy presented as live when workflow + snapshots are available.

**Out of scope for this charter:** Stripe billing (human backlog `stripe_operator_prereq`).

---

## Gap map (code vs production)

| Area | Repo state | Production gap |
|------|------------|----------------|
| PPE embed | `/ppe-embed` in Caddy; `NEXT_PUBLIC_PPE_EMBED_URL` build arg | Confirm VPS build uses `/ppe-embed`; embed loads without “pending” |
| Workflow store | `msos_web_data` volume + `/api/theses/*` | Works when identity present |
| Command Center | `api/command-center/summary` + snapshot mount | Needs `ppe_snapshots` + signed-in user |
| Monitor / History | `loadMonitorFeed` from workflow + snapshots (not fixture file) | Needs identity + freezes |
| Strategy Lab UI | Embed live; side metrics from fixtures | Optional: `msos_strategy_lab_embed_shell_v1` |
| Research CTA | `researchOfferCta.ts` | VPS `.env` + `msos_web` rebuild |
| Access identity | `msos_access_identity_v1` chartered | **Cloudflare policies on apex routes** (operator) |

---

## Execution tracks

### Track A — VPS ops (no product code)

**Owner:** Operator or agent via `ppe_vps_ssh.cmd` (keys stay local; never paste in chat).

| Step | Command / action |
|------|------------------|
| 1. Local SSH config | Copy `ppe_operator_ssh.local.cmd.example` → `ppe_operator_ssh.local.cmd` (gitignored) |
| 2. Research CTA | `ppe_vps_ssh.cmd research-cta you@example.com` |
| 3. Deploy latest | `ppe_vps_ssh.cmd deploy` |
| 4. Verify | `msos_production_demo_witness.cmd` from desktop (HTTP checks) |
| 5. Sign-off | Update [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) operator row |

**VPS `.env` checklist** (repo root on server):

```bash
PPE_RESEARCH_OFFER_URL=mailto:you@example.com?subject=PPE%20research%20beta
PPE_RESEARCH_OFFER_LABEL=Request research beta access
NEXT_PUBLIC_PPE_EMBED_URL=/ppe-embed
NEXT_PUBLIC_MSOS_SIGN_IN_URL=https://app.marketstructureos.com
```

After any `.env` change affecting Next build args: `docker compose up -d --build msos_web`.

### Track B — Cloudflare Access on apex (platform)

Per [`SPRINT_MSOS_ACCESS_IDENTITY_V1.md`](SPRINT_MSOS_ACCESS_IDENTITY_V1.md):

1. Zero Trust → Application (or extend existing) for `marketstructureos.com` paths:
   - `/command-center`, `/command-center/*`
   - `/strategy-lab`, `/strategy-lab/*`
   - `/monitor`, `/monitor/*`
   - `/history`, `/history/*`
2. Policy: allow tester emails (same Google IdP as `app.*`).
3. Homepage `/` may stay **public** (no fake logged-in state).
4. Confirm `msos_web` receives `CF-Access-Authenticated-User-Email` (see `msosIdentity.ts`).

**Policy question (steward):** Friends-first demo — protect **product routes only** (recommended) vs protect entire apex?

### Track C — Tester journey (evidence)

Manual script for cohort feedback sessions:

1. Open `https://marketstructureos.com` → sign in when prompted on product route.
2. Strategy Lab → confirm PPE embed loads; freeze an evaluation on `app.*` if needed.
3. Save thesis / expression (server persistence).
4. Command Center → see snapshot KPIs scoped to your email.
5. Monitor / History → live workflow + snapshot metadata (not fixture hero copy).
6. Research CTA visible where chartered.

Record outcome in witness artifacts; file issues via `ppe_request.cmd` if product gaps remain.

### Track D — Product polish (optional relay)

Queue only if Track A+B+C still leave misleading UI:

- `msos_strategy_lab_embed_shell_v1` — replace fixture side panels when embed is live.
- Re-open witness slice if production regressions need automated guard.

Use control plane: `ppe_request.cmd --chapter-id … --reason …` (do not hand-edit queue).

---

## Agent SSH access (secure pattern)

**Do not** paste private keys or passwords into Cursor chat.

1. **GitHub Actions deploy** (already supported): `scripts/setup_vps_deploy_once.ps1` → secrets `VPS_HOST`, `VPS_USER`, `VPS_SSH_PRIVATE_KEY`.
2. **Desktop agent ops:** `ppe_operator_ssh.local.cmd` sets `PPE_VPS_HOST`, `PPE_VPS_USER`, `PPE_VPS_SSH_KEY`, `PPE_VPS_ROOT`.
3. Agents run `ppe_vps_ssh.cmd <subcommand>` which SSHes non-interactively.

Optional: dedicated **agent deploy key** on VPS (`authorized_keys`), separate from your personal key — revoke without losing your login.

---

## Promotion to relay queue

When steward approves this charter:

1. Mark human backlog item `msos_production_live_hookup` **done** (ops checklist complete).
2. If product slices remain, add **`msos_production_live_verify_v1`** (or re-queue `msos_e2e_product_witness_v1` platform slice) via `ppe_request.cmd --apply`.
3. Reconcile: `ppe_request.cmd reconcile` → read `CONTROL_PLANE_STATUS.json`.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-19 | v1 — charter for production live hookup vs relay-DONE drift |
