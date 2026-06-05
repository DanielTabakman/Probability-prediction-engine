# Dev changelog (rolling)

Human-readable release notes for work that landed on `main`. Updated on merge, daily (UTC), and chapter closeout.

## 2026-06-05

- `b32f955` — ci: fix docker_entrypoint Streamlit health check hang (#88)

## 2026-06-03

- `b6ad3a7` — control-plane: tiered pytest gates + testing efficiency (#84) (`docs/SOP/`)
- `f50b1a9` — Workflow-efficiency-tooling: control-plane scripts for BUILD starters and metrics (#86) (`scripts/`)
- `4169985` — MSOS P3: Command Center shell + fixture overview (Product-Slice002) (#85) (`apps/msos-web/`)
- `9c2fab7` — fix(tests): allow MSOS P3 manifest in charter witnesses (#83)
- `a3b50ed` — control: SELECTION MSOS P3 Command Center (#82) (`docs/SOP/`)
- `80eb7d5` — control-merge-to-push-gate (#81) (`docs/SOP/`)

## 2026-06-02

- `d89b321` — MSOS P2: public homepage + platform wiring + chapter closeout (#80) (`apps/msos-web/`)
- `34f6344` — control: SELECTION MSOS P2 homepage (manifest READY) (#79) (`docs/SOP/`)
- `a396f3a` — product-canon: install MSOS storyboard v0.6; open P2 gate (#78) (`docs/SOP/`)

## 2026-06-01

- `21034db` — control: integrate repo layer map into relay, orchestrator, and gates (#77) (`scripts/`)
- `e2e9936` — MSOS P1: stack routing ADR (Next.js shell + Streamlit PPE) (#76) (`docs/SOP/`)
- `fea4631` — Phase 6 trust metrics: chapter closeout SOP (Slice004). (#74) (`docs/SOP/`)
- `be79b27` — MVP1 Phase6: trust enum rollups in class summary (Product-Slice002). (#73) (`src/viz/`)

## 2026-05-29

- `80b998e` — Ops: enable PPE auto-operator (continuous, backlog propagate, steward charter). (#71) (`scripts/`)
- `33e51c7` — Steward: charter MVP1 Phase 6 trust metrics v1 for relay BUILD. (#70) (`docs/SOP/`)

## 2026-05-28

- `2978726` — MVP1 Phase5 review hardening + steering sync (full chapter closeout) (#69) (`docs/SOP/`)
- `aae5b26` — Ops: queue Phase 5 product chapter + continuous run improvements (#68) (`docs/SOP/`)
- `bfa9a88` — Ops: auto-builder v1 (deterministic relay + deploy witness closeout) (#67) (`docs/SOP/`)
- `d12b903` — Ops: auto-SELECTION roadmap v0 for run_ppe continuous (#66) (`docs/SOP/`)
- `d330aa8` — Ops: PPE worker modes v0 (deterministic continuous without ACP) (#65) (`scripts/`)
- `c78ab9f` — Post-Phase3 closeout: steering sync + closeout spec hardening (#63) (`docs/SOP/`)
- MVP1-PostPhase3-Smoke-Slice002: dual smoke witness (EVIDENCE-PLANE) (#62) (`docs/SOP/`)
- MVP1-PostPhase3-Control-Slice001: charter witness (EVIDENCE-PLANE) (#60) (`docs/SOP/`)
- `db7ca53` — Ops: PHASE_QUEUE auto-repair + post-Phase3 chapter (#59) (`docs/SOP/`)
- `051058f` — Ops: remove duplicate READY disagreement row from PHASE_QUEUE (#58) (`docs/SOP/`)
- `65f521e` — Ops: promotion recovery + Sprint003 closeout (#57) (`docs/SOP/`)
- `17acfcd` — Sprint003 closeout: chapter witness + docs (#56) (`docs/SOP/`)
- MVP1-Sprint003-Witness-Slice003: pytest witness (EVIDENCE-PLANE) (#54)
- `c6c9943` — ops: retry deploy healthcheck while stack starts (#52)
- `e38fb68` — ops: fix VPS recover script (if/elif for ssh-action) (#51)
- `6087aea` — ops: fix vps-recover ssh script (#50)
- `3f4a871` — Ops: VPS recovery workflow (#48)
- `878ae11` — Ops: healthcheck + uptime monitor (#47)
- `cfdb883` — Phase3 closeout: apply control closeout docs (#46) (`docs/SOP/`)
- `a0742b0` — Phase3-CommercialWrapper-Closeout-Slice004: chapter evidence witness (EVIDENCE-PLANE) (#45) (`docs/SOP/`)
- `1f5abb6` — Phase3: restore commercial wrapper phase plan (#44) (`docs/SOP/`)
- `daecb6c` — Phase3-Smoke-Slice003: commercial wrapper witness + main import fix (#43) (`src/viz/`)

## 2026-05-27

- `49e856e` — Phase3 commercial wrapper (integrated clean merge) (#42) (`src/viz/`)
- MVP1-Sprint003-Closeout-Slice004: chapter evidence witness (EVIDENCE-PLANE) (`docs/SOP/`)
- `6ac908b` — MVP1-Sprint003-Evidence-Slice002: tiered gate + queue auto-select (EVIDENCE-PLANE) (`scripts/`)
- MVP1-Sprint003-Control-Slice001: charter witness (EVIDENCE-PLANE) (`docs/SOP/`)
- MVP1-FeedbackBeta-Closeout-Slice004: chapter evidence witness (EVIDENCE-PLANE) (`docs/SOP/`)
- `5f28ddf` — Control-plane: deflake UI smoke and honor slice timeouts (#36) (`scripts/`)
- MVP1-FeedbackBeta-Smoke-Slice003: feedback panel witness in dual smoke harness (`scripts/`)
- MVP1-FeedbackBeta-Product-Slice002: friends-first feedback capture (`src/viz/`)
- `9a4a04c` — Control-plane: close disagreement chapter and SELECTION for feedback beta (#35) (`docs/SOP/`)
- `80729cd` — ControlPlane: enrich MSOS Live Mirror refresh report fields (#34) (`scripts/`)
- `f1070fe` — Control-plane: formalize GOOGLE_DOCS_REFRESH SOP (#33) (`scripts/`)
- `805a788` — Control-plane: Google Docs refresh protocol + MSOS mirror snapshot (#32) (`scripts/`)
- `3b898c9` — control-plane: selection queue QoL (#31) (`scripts/`)
- `1bca8d5` — control-plane: persist google-docs MCP config (#29)
- `dec7375` — control-plane: fix orchestrator root detection on Windows worktrees (#30) (`scripts/`)
- `d44193d` — control-plane: bounded auto-selection queue (#28) (`docs/SOP/`)
- `11f569c` — control-plane: add scripts/run_pushable_gate.py tiered gate (#27) (`scripts/`)
- `2cf8889` — control-plane: closeout evidence COMPLETE patch (#26) (`scripts/`)
- MVP1-DisagreementStrip-Closeout-Slice004: chapter evidence witness (EVIDENCE-PLANE) (#25) (`docs/SOP/`)

## 2026-05-26

- MVP1-DisagreementStrip-Smoke-Slice003: dual smoke witness (EVIDENCE-PLANE) (#24) (`docs/SOP/`)
- MVP1-DisagreementStrip-Product-Slice002: candidate strip hypothesis copy polish (#23) (`src/viz/`)
- `b4449c5` — control-plane: MVP1-aware primary smoke + auto-diagnose STOP_FOR_REVIEW (#22) (`scripts/`)
- `a5a1519` — control-plane: harden belief peak and sigma selectors for MVP1 UI smoke (#21) (`scripts/`)
- `40b6f7b` — control-plane: accept MVP1 belief peak label in UI smoke harness (#20) (`scripts/`)
- CLOSE MVP1-DisagreementStrip-Control-Slice001 (charter witness) (#19) (`docs/SOP/`)

## 2026-05-25

- `ef7a0f8` — control: unified run_ppe.cmd, active phase manifest, and Cursor context discipline (#17) (`docs/SOP/`)

## 2026-05-20

- CLOSE MVP1-OnboardingHowItWorks-Closeout-Slice004 (chapter complete) (#16) (`docs/SOP/`)
- `d4bcb19` — MVP1 onboarding: How it works expander + close Product and Smoke slices (#15) (`docs/SOP/`)
- CLOSE MVP1-OnboardingHowItWorks-Control-Slice001 (charter witness) (#14) (`docs/SOP/`)
- `2c0393e` — SELECTION: charter MVP1 onboarding How it works (#13) (`docs/SOP/`)
- `47816a6` — docs: align merge gate with full CI (pytest + docker_entrypoint) (#12) (`docs/SOP/`)
- `6050b55` — docs: post-PR10 deploy witness, SELECTION deferred, Cursor snippet steps (#11) (`docs/SOP/`)
- `aff44c5` — MVP1-BeliefInput: human belief controls + relay continuity bundle (#10) (`docs/SOP/`)
- `099dcd9` — ci: guard Streamlit/Docker entrypoint against src import regressions (`docs/SOP/`)
- `542cd4c` — MVP1-FriendsFirst: above-fold screen polish + vision import (product-plane) (#9) (`docs/SOP/`)
- `7fcb3d4` — docs: enable always-on auto-commit rule for PPE (#8) (`docs/SOP/`)
- `93945a1` — fix: ensure src package imports when Streamlit starts app (`src/viz/`)
- `f765592` — Merge pull request #7 from DanielTabakman/build/commercial-validation-v0
- `dab0765` — merge: integrate origin/main into build/commercial-validation-v0
- `6417811` — feat(mvp1): review enrichment and smoke regression chapters (`docs/SOP/`)

## 2026-05-19

- `85d5f7b` — docs(control): health-check cleanup and canonical commit test gates (#6) (`docs/SOP/`)
- `abaac6f` — chore(agent): auto-open PR to main after feature-branch push
- `b737344` — docs(control): health-check cleanup and canonical commit test gates (`docs/SOP/`)
- `bf262a4` — MVP1 operator hardening: trust-strip smoke gate and chapter close. (`docs/SOP/`)
- `7961c33` — Phase 2 Slice006: trust strip MVP1 disclosure; chapter closeout. (`docs/SOP/`)
- `0fde338` — docs(control): witness HEAD 707610c after Slice005 (`docs/SOP/`)
- `707610c` — feat(phase2): Slice005 decision surface panel parity + risk register (`docs/SOP/`)
- `6ba9ec1` — docs(control): witness HEAD 566f4f0 (`docs/SOP/`)
- `566f4f0` — docs(control): align witness to HEAD f828fb3 (`docs/SOP/`)
- `f828fb3` — docs(control): witness target SHA 0b09b97 (`docs/SOP/`)
- `0b09b97` — docs(control): integrated status + Phase2 Slice005 SELECTION (`docs/SOP/`)
- `01c89cf` — feat(phase2): reconcile Slice002 + MVP1 UI exclusions Product-Slice003 (`docs/SOP/`)
- `03a6835` — docs(control): integrated finish-line â€” Reliability complete, Phase 2 chartered (`docs/SOP/`)
- `559f908` — feat(reliability): per-scenario smoke timeouts and dual-smoke witness (`docs/SOP/`)
- `1367f9a` — docs(control): deploy witness SHA 34804ca after ops compose deploy (`docs/SOP/`)
- `34804ca` — ops: wire research offer in compose; close ops + SELECTION to MVP1 Reliability (`docs/SOP/`)
- `c6eca8a` — docs(control): deploy witness SHA 983e7f5 (`docs/SOP/`)
- `983e7f5` — docs(control): ops completion evidence, SELECTION prep, smoke witness 20260519_131035 (`docs/SOP/`)
- `268c907` — docs(control): ops completion focus and archived chapter cleanup (`docs/SOP/`)
- `132ac4f` — docs(control): deploy witness SHA after Commercial Validation (`docs/SOP/`)
- `f6490a7` — feat(product): demo research-offer CTA via PPE_RESEARCH_OFFER_URL (`src/viz/`)
- `a5b5d63` — docs(control): Commercial Validation chapter â€” charter, playbook, brief, closeout (`docs/SOP/`)
- `af02210` — fix(smoke): flush progress logs so UI smoke runs are observable (`docs/SOP/`)
- `7c6694e` — docs(control): deploy witness SHA after main merge (`docs/SOP/`)
- `f71566a` — merge: local main (orch-smoke) into notifications
- `dc03054` — feat(product): Validation Chapter smoke harness and MVP1 primary output banner (`src/viz/`)
- `1790177` — docs(control): close Validation Chapter; post-chapter Commercial Validation SELECTION (`docs/SOP/`)
- `9cc536b` — feat(mvp1): Validation Chapter â€” decision surface, demo UX, operator docs (`docs/SOP/`)

## 2026-05-18

- `92b6b8e` — Merge origin/main into notifications (sync Docker deploy stack)
- `004cc5b` — docs: re-import PPE master canon and align MVP1 steering (`docs/SOP/`)
- `4deb587` — docs: rename integration branch notifivations to notifications (`docs/SOP/`)

## 2026-05-15

- `b8c0f01` — Merge origin/main into notifivations
- `5add40e` — chore(deploy): add Docker stack files to main (#5)
- `aa691e4` — fix(caddy): add Caddyfile; split CF vs direct traffic for proto map (#4)
- `2a92f50` — Merge origin/main into notifivations
- `09f6835` — Add pytest.ini testpaths and guided VPS deploy bootstrap script. (#3) (`scripts/`)
- `d206126` — chore: merge main into notifivations (sync CI/deploy/docs)
- `95cb357` — docs: script to set VPS deploy secrets via gh CLI (#2) (`scripts/`)

## 2026-05-14

- `3cd2d5e` — ci: add CI, VPS deploy, and private-free merge automation workflows (#1) (`docs/SOP/`)

## 2026-05-13

- `999b508` — Demo CTA to private app; Caddy forwarded headers for Streamlit HTTPS; runbook + README (`src/viz/`)

## 2026-05-11

- `90f11b5` — Runbook: Cloudflare Flexible vs Full strict for HTTP-only origin
- `7ee92dc` — Caddy: auto_https off + single :80 host routing (fix 308 before DNS)
- `c01a14d` — Caddy: disable auto HTTPS redirects and serve demo on :80 for IP access

## 2026-05-08

- `4518358` — Add VPS Docker/Caddy deploy, snapshot toggle, restic backup scripts (`src/viz/`)
