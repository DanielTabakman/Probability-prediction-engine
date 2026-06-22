---
surface: command-center
version: 1
status: draft
content_file: apps/msos-web/src/content/commandCenter.ts
author: copy-agent
as_of: 2026-06-22
notes: >-
  Operator deferred lock-in — defaults chosen: Save a view (header CTA), Home crumb,
  Track how your views hold up (calibration), Have a view? (thesis prompt).
  Review pass welcome before promoting to approved.
---

# Command Center copy v1 (draft)

### One job

Authenticated home base — resume work, review saved views, shortcut into Strategy Lab and Monitor.

### Defaults locked (operator review pending)

| Region | String |
|--------|--------|
| Header CTA | Save a view |
| Crumb | Home |
| Calibration title | Track how your views hold up |
| Thesis prompt | Have a view? |

### Content module

All visitor strings in `apps/msos-web/src/content/commandCenter.ts`. Demo KPI/tile/headline fixtures re-export from content via `commandCenterFixtures.ts`.
