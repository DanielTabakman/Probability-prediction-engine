## Workflow Metrics V1 (SOP)

### 1. Purpose

- Track a minimal, decision-useful set of workflow metrics.
- Keep logging lightweight.
- Avoid dashboard bloat and precision theater.

### 2. Core principle

- Optimize for clean throughput.
- **North-star metric:** `weighted_slices_per_active_hour`
- Interpret alongside: `avg_cognitive_load`, `avg_roundtrips`

### 3. System layers

- **Ledger** = live workflow steering in chat.
- **Sheet** = durable metrics memory / charts.
- **SOP docs** = canonized protocol.
- Ledger feeds sheet; sheet does not replace ledger.

### 4. Session logging convention

- User interface is chat.
- Session events:
  - `start session`
  - `break start`
  - `break end`
  - `session stop`
- `active_minutes` is derived from: `session_start → session_stop` minus breaks.
- User provides at `session stop`:
  - `cognitive_load_1_5`
  - optional `session_notes`

### 5. Slice logging convention

- Slice rows are created/updated from workflow milestones.
- At selection, steward/assistant records:
  - `slice_id`, `phase`, `sprint`, `title`, `slice_kind`, `value_surface`, `planned_size`, `status`, `started_at`
- At closeout, steward/assistant records:
  - `actual_size`, `completed_at`, `roundtrips`, `raw_copy_pastes`, `rework_count`, `incident_flag`
  - `incident_started_at` (if any), `recovered_at` (if any), optional `notes`

### 6. Required sheet tabs

- Sessions
- Slices
- Events

### 7. Exact V1 field sets

**Sessions fields**

- `session_id`
- `session_started_at`
- `session_ended_at`
- `break_minutes`
- `active_minutes`
- `cognitive_load_1_5`
- `session_notes`
- `total_roundtrips`
- `total_raw_copy_pastes`
- `slices_completed_count`
- `weighted_slices_completed`

**Slices fields**

- `slice_id`
- `phase`
- `sprint`
- `title`
- `slice_kind`
- `value_surface`
- `status`
- `planned_size`
- `actual_size`
- `size_weight_actual`
- `started_at`
- `completed_at`
- `active_dev_minutes`
- `roundtrips`
- `raw_copy_pastes`
- `rework_count`
- `incident_flag`
- `incident_started_at`
- `recovered_at`
- `primary_session_id`
- `notes`

**Events fields**

- `event_id`
- `timestamp`
- `event_type`
- `session_id`
- `slice_id`
- `value_1`
- `value_2`
- `note`

### 8. Allowed enum values

**`slice_kind`**

- `product`
- `process`
- `bugfix`
- `refactor`

**`value_surface`**

- `user_facing`
- `workflow_enabling`
- `reliability`
- `internal_only`

**`status`**

- `selected`
- `build`
- `recovery`
- `closeout`
- `closed`

**size classes**

- `S = 1`
- `M = 2`
- `L = 3`
- `XL = 5`

### 9. Size rubric

- `S` = very small, one narrow bounded outcome.
- `M` = normal healthy slice, one coherent outcome.
- `L` = multiple coupled subparts, harder to validate cleanly.
- `XL` = should probably have been split earlier.

### 10. Logging burden rule

- If logging takes more than about 2 minutes at session end, simplify the system.
- Prefer consistency over precision.

### 11. V1 interpretation

- A healthy week improves weighted throughput without increasing overload or friction.
- Read throughput with cognitive load and roundtrips, not in isolation.

### 12. Current status note

- V1 is a trial instrumentation layer and may be adjusted after several real sessions.
