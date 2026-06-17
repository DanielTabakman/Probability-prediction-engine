# Dev changelog (rolling)

Human-readable release notes for work that landed on `main`. Updated on merge, daily (UTC), and chapter closeout.

## 2026-06-17

- `742ad0b` — Control-plane: dev changelog
- `193de4a` — Control-plane: dev changelog
- `9e5c423` — Control-plane: dev changelog
- `b821236` — Control-plane: dev changelog
- `86ecf96` — Control-plane: dev changelog
- `442b04a` — Control-plane: dev changelog
- `27b21c3` — Control-plane: dev changelog
- `ce5fe19` — Control-plane: dev changelog
- `2140a94` — Control-plane: dev changelog
- `f4fd8fd` — Control-plane: dev changelog
- `0a8a94e` — Control-plane: dev changelog
- MSOS-UserStateV1-Product-Slice002 (PRODUCT): Command Center PPE snapshot bridge (#184) (`apps/msos-web/`)
- `0d85ae8` — ops(control-plane): VM bootstrap, loop-host guard fix, prod wiring closeout (#183) (`docs/SOP/`)
- `70bf9c9` — ops(platform): add VM check_vm_loop and setup_vm_loop_host helpers (#182)
- `d7a4bd4` — ops(platform): fix VM headless loop popup cmd windows (#181) (`scripts/`)
- `928bac2` — Control-plane: dev changelog

## 2026-06-16

- `9d869dc` — fix: VM_AUTO on VM only, disable desktop auto default (#196) (`scripts/`)
- `90740b0` — ops(platform): DESKTOP AUTO START pushes BUILD/CONTINUE automatically (#195) (`scripts/`)
- `062a864` — ops(platform): auto-install operator Desktop shortcuts when appropriate (#194) (`docs/SOP/`)
- `53c2388` — ops(platform): DESKTOP BUILD and CONTINUE one-click buttons (#193)
- `bf5c58b` — docs(SOP): VM+desktop operator session handoff and procedure updates (#192) (`docs/SOP/`)
- `d567b35` — ops(platform): fix VM_STATUS closing before PHASE line shows (#191)
- `f2887c2` — ops(platform): always set PPE_STACK_HEADLESS in check_vm_loop (#190)
- `eb00b15` — ops(platform): add VM_RESTART.cmd stop-wait-start shortcut (#189)
- `4aeb02b` — ops(platform): VM desktop shortcuts and FIND_PPE_FOLDER (#188) (`scripts/`)
- `d7bfabb` — ops(platform): add VM_UPDATE.cmd double-click git pull (#187)
- `f5a7485` — ops(platform): double-click VM operator (no copy-paste) (#186)
- `ffa90c7` — ops: fix_vm_stop_all.cmd stop popups and visible logon task (#180)
- `c2c5421` — Control-plane: dev changelog
- `e2aa753` — ops: fix_vm_headless.cmd stop popup windows on loop host (#179)
- `91d0e74` — Control-plane: dev changelog
- `ac78a1f` — ops: add fix_vm_operator.cmd for VM loop-host recovery (#178)
- `4f57d4d` — Control-plane: dev changelog
- `183b22e` — feat(msos-ui): MSOS workflow persistence product slice 002 (server store + API) (#177) (`apps/msos-web/`)

## 2026-06-15

- `bb037e1` — ops: loop publish control-plane/loop-merge-each-pass (#176) (`docs/SOP/`)
- `9a7be4b` — feat(control-plane): mergeEachPass nudges green loop PRs in auto loop (#175) (`docs/SOP/`)
- `1775ed6` — Control-plane: dev changelog
- `5943703` — fix(control-plane): operator loop auto-heal and selection unblock (#174) (`scripts/`)
- `7c13b7f` — feat(control-plane): VM loop-host guard, SSH ops, prod wiring selection (#173) (`scripts/`)
- `91897d2` — control-plane: Monday workflow radar v1 (friction scan + orphan cleanup) (#172) (`scripts/`)
- `425d831` — feat(platform): MSOS production wiring platform slice 003 (#171) (`apps/msos-web/`)
- `cff9fb5` — feat(msos-ui): MSOS production wiring product slice 002 (clean) (#170) (`apps/msos-web/`)
- `e86e816` — Control-plane: dev changelog
- `32c6713` — control-plane: layer map for watch_ide_build_local.cmd (#164) (`docs/SOP/`)

## 2026-06-14

- `dcbbc75` — Control-plane: dev changelog
- `b0070c6` — platform(MSOS-PublicLaunchV1): wire msos_web research-offer env for VPS deploy (#165) (`docs/SOP/`)
- `cc26158` — control-plane: local IDE BUILD trigger watcher (CONTROL-PLANE) (#163) (`scripts/`)

## 2026-06-13

- `2b378d3` — control-plane: dist quant v2 closeout + validation gate unblock (#161)
- `31f2d5b` — feat(msos-shell): session notebook post-session survey (#162) (`docs/SOP/`)
- `459e66c` — control-plane: operator hardening (evidence stubs, stack dedupe, queue sync) (#160) (`scripts/`)
- `7a9ea61` — fix(platform): match session.html health check to page title (#159)
- `547b674` — MVP1 cross-venue prob panel (slices 002-004 + closeout) (#157) (`docs/SOP/`)
- `513ae72` — Control-plane: dev changelog
- `e24caef` — control-plane: cut GitHub Actions usage (#158) (`docs/SOP/`)
- `8e79c82` — fix(platform): force-recreate caddy on VPS deploy (#155)
- `88ea305` — control-plane: PPE autobuilder v1 (#153) (`scripts/`)
- `f35db18` — feat(msos-shell): deploy operator session notebook on apex (#152) (`docs/SOP/`)
- `1d1b3be` — Control-plane: dev changelog
- `092d291` — control-plane: relay operator hardening for unattended loop (#150) (`scripts/`)
- `29458ff` — control-plane: ntfy quiet hours, morning report, phone status (#148) (`scripts/`)
- `3950670` — charter(control): public demo launch + operator check-in ntfy (#147) (`docs/SOP/`)
- `b2e9a2e` — charter(control): MSOS storyboard visual parity v1 at MEDIUM priority (#146) (`docs/SOP/`)

## 2026-06-12

- `abeea4e` — fix(scripts): use float return from fetch_deribit_btc_index in snapshot collector (#145) (`scripts/`)
- `dfdad29` — Control-plane: dev changelog
- MVP1-DistQuantV2-Product-Slice004: daily distribution stats snapshot collector (#143) (`docs/SOP/`)
- MVP1-DistQuantV2-Product-Slice003: extended CSV and summary panel quant columns (PRODUCT-PLANE) (#142) (`src/viz/`)
- `8874f4e` — control-plane: fix scheduled Google Docs and dev-changelog CI sync (#141)
- `467da50` — docs(control): laptop shutdown handoff checklist in desktop starter (#140) (`docs/SOP/`)
- `61a4118` — fix(control-plane): throttle ntfy volume and auto-select empty plan (#124)
- `d191d55` — control-plane: IDE BUILD health + product focus gate (#139) (`docs/SOP/`)
- `9ea81c8` — control-plane: IDE BUILD automation health diagnostics (#138) (`scripts/`)
- MVP1-DistQuantV2-Product-Slice002: tail quantiles and strike ladder (#137) (`src/engine/`)
- MSOS-P8-Product-Slice002: conclusion learn loop UI (#135) (`docs/SOP/`)
- MSOS-P7-Product-Slice002: monitor, history, and calibration Command Center (PRODUCT-PLANE) (#133) (`apps/msos-web/`)

## 2026-06-11

- ops: loop publish build/auto/MSOS-P8-Product-Slice002-msos_p8 (#136) (`docs/SOP/`)
- ops: loop publish build/auto/MSOS-P7-Product-Slice002-msos_p7 (#134) (`docs/SOP/`)
- `0d5f46c` — fix(control-plane): ntfy quota visibility and urgent loop-down (#132) (`docs/SOP/`)
- MSOS-P6-Product-Slice002: expression planning UI (PRODUCT-PLANE) (#130) (`apps/msos-web/`)
- `929385d` — ops: loop publish control-plane/ntfy-quota-visibility (#131) (`scripts/`)
- ops: loop publish build/auto/MSOS-P5-Product-Slice002-msos_p5 (#129) (`docs/SOP/`)
- `4672f8c` — ops: ops/chapter-closeout-sync (#128)
- `c95db81` — chore(control-plane): sync SOP after MVP1 and MSOS chapter closeouts (#127) (`docs/SOP/`)
- `6522487` — control-plane: ppe_go.cmd operator handoff + alert hints (#120) (`scripts/`)
- `6385151` — test(control-plane): allow MSOS dist demo plan in manifest witness (#126)
- `afba296` — test(control-plane): allow MSOS dist demo plan in manifest witness (#125)
- `0c3ac88` — fix(control-plane): auto-select when manifest READY with empty planPath (#123)
- `8ffcff6` — fix(control-plane): auto-select when manifest READY with empty planPath (#122) (`scripts/`)
- `a673f80` — control-plane: add CLI-to-IDE fallback for ntfy fix command (#117) (`scripts/`)
- MSOS-DistDemo-Product-Slice002: Strategy Lab distribution demo embed (#121) (`apps/msos-web/`)
- `3167da0` — control-plane: loop singleton guard + MSOS_UI test layer map (#119) (`scripts/`)
- `f441914` — control-plane: IDE BUILD automation JSON trigger (not .md) (#118) (`docs/SOP/`)
- `82f9113` — control-plane: add PPE director subagents for IDE_BUILD handoff (#116) (`docs/SOP/`)
- `edaf09a` — control-plane: IDE BUILD automation loop and post-build watcher (#115)
- `983169d` — control-plane: IDE BUILD automation loop and post-build watcher (#114) (`scripts/`)
- `477980a` — control-plane: near-zero API IDE handoff + backlog priority (rebased) (#109) (`docs/SOP/`)
- `9ed5abb` — control-plane: IDE marker accepts squash-merged product on main (#113) (`scripts/`)
- `0f998cf` — control-plane: gitignore near-zero API + ntfy build test fix (#112)
- `58b82aa` — product(ppe-ui): distribution summary panel Slice002 (#111) (`src/viz/`)
- `a9acdc0` — control-plane: fix ntfy build test for IDE handoff path (#110)
- `87d327b` — control-plane: evidence-complete skip gates + IDE handoff (rebased) (#108) (`scripts/`)
- `fd84928` — control-plane: skip evidence-COMPLETE chapters at propagation and SELECTION (#105) (`scripts/`)
- **Chapter closed:** MSOS Strategy Lab distribution demo (`MSOS-DistDemo-Closeout-Slice005`)
- **Chapter closed:** MVP1 distribution stats legibility (`MVP1-DistStatsLeg-Closeout-Slice005`)

## 2026-06-10

- `97b7744` — control-plane: wire operator hygiene into preflight and loop startup (#107) (`docs/SOP/`)
- `268c225` — control-plane: fix evidence COMPLETE detection and advance to dist-stats (#104) (`docs/SOP/`)
- `ad5cec1` — control-plane: auto-start agent CLI on IDE_BUILD (#103) (`scripts/`)
- `cb8a64a` — control-plane: fix-status phone ntfy for operator repairs (#102)
- `a29b992` — control-plane: phone ntfy operator commands (build, fix, status) (#101) (`scripts/`)
- `00662b9` — control-plane: weekly digest notify + research distribution queue charter (#100) (`docs/SOP/`)
- `accf94f` — control-plane: weekly digest phone ntfy + Monday scheduler (#99) (`scripts/`)
- `9d988b2` — ops: ops/slice-batching-legibility (#98) (`scripts/`)
- `998a756` — feat: ntfy on slice and chapter completion for phone progress (CONTROL-PLANE) (#96) (`scripts/`)
- `fd79dcf` — ops: desktop operator bootstrap + P4 closeout (#95) (`scripts/`)

## 2026-06-09

- `4402870` — control-plane: mobile operator ntfy watch for desktop loop (#94) (`scripts/`)

## 2026-06-06

- `23865d4` — MVP1: BTC distribution stats CSV export (Phase 1) (#93) (`docs/SOP/`)

## 2026-06-05

- `ec445fe` — MVP1 probability method legibility + operator local-loop fixes (#90) (`docs/SOP/`)
- MSOS-P4-Product-Slice002: Strategy Lab route + PPE embed boundary (PRODUCT-PLANE, msos-shell) (#92)
- MSOS-P4-Product-Slice002: Strategy Lab route + PPE embed boundary (PRODUCT-PLANE, msos-shell) (#91) (`apps/msos-web/`)
- `6b93d8f` — Control-plane: rolling dev changelog + CI docker_entrypoint fix (#89) (`docs/SOP/`)
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
