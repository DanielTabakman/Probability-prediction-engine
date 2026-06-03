# MSOS website acceleration checklist

**Purpose:** Actionable changes agreed to compress calendar time toward storyboard v0.6 parity **without** widening PPE math, auth, or commercial honesty rules.

**Canon (unchanged):** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md) · [`docs/VISION/MSOS/storyboard-v0.6/MANIFEST.md`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md)

**As-of:** 2026-06-03 — P2 **COMPLETE**; P3 **READY** ([`MSOS_FRONTIER.md`](MSOS_FRONTIER.md))

---

## 1. Queue and orchestration (control plane)

| # | Change | Owner | Status |
|---|--------|-------|--------|
| 1.1 | Run **`run_ppe.cmd --continuous`** (or `run_ppe_auto_local.cmd`) after each MSOS chapter closeout so the next `queued` row propagates without idle days | Operator | **Do** |
| 1.2 | **Pre-charter P4–P8** before each prior chapter closes: add relay + sprint + SELECTION + evidence per chapter | Steward | **P4 done** 2026-06-03; **P5–P8 Todo** |
| 1.3 | For each pre-chartered chapter: add `SPRINT_MSOS_P4_*.md`, `POST_MSOS_P4_*_SELECTION.md`, `MSOS_P4_*_EVIDENCE_STATUS.md`, and set backlog `planPath` + `status: queued` when predecessor is **done** (per [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)) | Steward | **Todo** |
| 1.4 | Keep **`PHASE_CHAPTER_BACKLOG.json`** in sync when flipping `blocked` → `queued` → `done` (do not hand-edit manifest `phasePlanPath` after closeout — use `post_relay_continue`) | Agents | **Ongoing** |
| 1.5 | Optional steward **SELECTION record**: approve a **vertical demo** chapter (see §6) if investor walkthrough must land before P5 persistence | Steward | **Decision pending** |

---

## 2. P2 follow-ups (homepage — COMPLETE)

| # | Change | Owner | Status |
|---|--------|-------|--------|
| 2.1 | Operator **pixel screenshot witness** vs `prototype/screens/01_home.png` (deferred in P2 evidence) | Operator | **Todo** |
| 2.2 | **VPS deploy** of `msos_web` per [`docs/DEPLOY/MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md) after merge to `main` | Operator | **Todo** |
| 2.3 | Confirm P2 **design tokens** in `apps/msos-web/` are reusable for P3+ (CSS variables aligned to `prototype/html/style.css`); document token module path in P3 sprint carry-forward | Product slice | **Verify in P3** |

---

## 3. P3 — in flight (Command Center)

| # | Change | Owner | Status |
|---|--------|-------|--------|
| 3.1 | Execute relay plan [`msos_p3_command_center_relay.json`](PHASE_PLANS/msos_p3_command_center_relay.json) — shell + `02_command_center` with **fixture data** only | BUILD | **READY** |
| 3.2 | Reuse P2 tokens; **no** PPE proxy or thesis API in P3 (per sprint **Not now**) | BUILD | **Required** |
| 3.3 | Screenshot witness vs `prototype/screens/02_command_center.png` at closeout | BUILD | **Required** |
| 3.4 | **Optional (low debt):** add **Tailwind** mapped to existing storyboard CSS variables in Product slice **only if** it speeds layout without palette drift; do not adopt un-themed shadcn defaults | Steward + BUILD | **Optional** |

---

## 4. P4 — Strategy Lab / PPE entry (next integration risk)

| # | Change | Owner | Status |
|---|--------|-------|--------|
| 4.1 | Charter sprint: Strategy Lab route + storyboard `03_ppe_lab`; **Caddy reverse proxy** to Streamlit first ([`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)) | Steward | **Todo** |
| 4.2 | Document **iframe fallback** to `app.marketstructureos.com` in evidence if proxy blocked (ADR escape hatch — not first choice) | BUILD | **If needed** |
| 4.3 | **No** TypeScript port of PPE math, charts, or disagreement | BUILD | **Hard rule** |
| 4.4 | Honest **Live / Soon / Planned** on lenses per storyboard manifest | BUILD | **Required** |

---

## 5. P5–P7 — fixture-first, then persistence

| # | Change | Owner | Status |
|---|--------|-------|--------|
| 5.1 | **UI-first:** ship screens `04_confirmation`, `05_execution`, `06_monitor`, `07_history`, `08_updated_command` with **fixture/mock state** matching [`MSOS_Product_Semantics_State_Model_v0.1.md`](../VISION/MSOS/storyboard-v0.6/semantics/MSOS_Product_Semantics_State_Model_v0.1.md) | BUILD | **Todo** |
| 5.2 | **Persistence slice(s)** after UI witness: thesis save/reopen (P5), simulation-only expression plan (P6), monitoring/history states (P7) — separate relay slices or explicit sprint phases | Steward | **Todo** |
| 5.3 | P7 may span **three** PNG witnesses; consider **one chapter** with extra Product slices vs splitting P7a/P7b only if steward wants smaller PRs | Steward | **Decision** |
| 5.4 | No live execution, Hyperliquid beyond **Pending**, or undefined thesis-health metrics | BUILD | **Hard rule** |

---

## 6. P8 — tester release (not a commercial gate)

| # | Change | Owner | Status |
|---|--------|-------|--------|
| 6.1 | Charter P8: friends-first / validation report → next queue selection per [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) | Steward | **Todo** |
| 6.2 | Do **not** block paid research beta outreach on P8 ([`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md)) | Operator | **Policy** |

---

## 7. Optional steward compressions (calendar, controlled debt)

| # | Change | Tradeoff |
|---|--------|----------|
| 7.1 | **Vertical demo chapter:** merge **P3 shell + P4 iframe entry** into one SELECTION for investor demo | Faster journey; proxy polish deferred |
| 7.2 | **P5+P6 UI fixtures** in one chapter before any API | Looks like screens 04–05 earlier; persistence debt isolated |
| 7.3 | **iframe-first P4** (skip proxy attempt) | Fastest lab embed; CSP/cookie/URL debt later |

Require explicit SELECTION note + evidence doc if any of 7.x is chosen.

---

## 8. Parallel tracks (no queue violation)

| # | Change | Notes |
|---|--------|-------|
| 8.1 | **Commercial / customers:** run demo + research-beta script on **existing** `marketstructureos.com` / `app.marketstructureos.com` in parallel with MSOS BUILD | Does not require P2–P8 |
| 8.2 | **MVP1 engine:** optional separate MVP1 chapters on `src/viz/` while MSOS queue runs serially on `apps/msos-web/` | Non-widening rule applies |
| 8.3 | **Pre-write P4–P8 plans** while P3 BUILD runs | Reduces steward idle time; no code on `main` until SELECTION |

---

## 9. Implementation shortcuts (use these)

| # | Shortcut | Do not use |
|---|----------|------------|
| 9.1 | Port layout/tokens from `docs/VISION/MSOS/storyboard-v0.6/prototype/html/*.html` + `style.css` | Generic admin themes unrelated to v0.6 |
| 9.2 | Shared components: nav, shell, panel, KPI, pill, semantic-lock cards | Per-page one-off CSS |
| 9.3 | Streamlit remains PPE surface; MSOS wraps via proxy/iframe | Rebuild charts in React |

---

## 10. Explicit non-changes (avoid debt)

- Port PPE calculations or MVP1 trust semantics into `apps/msos-web/`
- Mark prediction markets / perps as **Live** without backend
- Custom auth server before program says otherwise
- Skip screenshot witnesses or closeout evidence for “speed”
- Force-push or skip CI gates on MSOS PRs

---

## 11. Suggested charter order (after P3)

```text
P3 Command Center (READY)
  → P4 Strategy Lab / PPE proxy (charter next)
  → P5 thesis confirm (fixture UI → persistence)
  → P6 expression sim (fixture → save/sim only)
  → P7 monitoring + history + updated CC (3 screens)
  → P8 tester release + validation report
```

**Target calendar (with §1–§9 applied):** ~6–12 weeks from P3 start to walkable storyboard journey; **~2–4 weeks** to public homepage + Command Center if P3 closes on schedule (P2 already shipped).

---

## Related

- Live queue: [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) · [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json)
- Operator run: [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
