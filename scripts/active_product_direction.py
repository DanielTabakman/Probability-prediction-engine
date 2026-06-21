"""Single source of truth for product direction and propagation to steering docs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DIRECTION_REL = "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json"
PIVOT_RUNBOOK_REL = "docs/SOP/PRODUCT_DIRECTION_PIVOT_V1.md"
MARKER_START = "<!-- ACTIVE_PRODUCT_DIRECTION:START -->"
MARKER_END = "<!-- ACTIVE_PRODUCT_DIRECTION:END -->"


@dataclass(frozen=True)
class Direction:
    raw: dict[str, Any]

    @property
    def pivot_id(self) -> str:
        return str(self.raw.get("pivotId") or "unknown")

    @property
    def as_of(self) -> str:
        return str(self.raw.get("asOf") or "")

    @property
    def primary_focus(self) -> str:
        return str(self.raw.get("primaryFocus") or "")

    @property
    def north_star(self) -> str:
        return str(self.raw.get("northStar") or "")

    @property
    def active_chapter_id(self) -> str:
        return str(self.raw.get("activeBuildChapterId") or "")

    @property
    def active_plan_path(self) -> str:
        return str(self.raw.get("activeBuildPlanPath") or "")

    @property
    def active_sprint(self) -> str:
        return str(self.raw.get("activeBuildSprint") or "")

    @property
    def next_steward_action(self) -> str:
        return str(self.raw.get("nextStewardAction") or "")

    @property
    def storyboard_ref(self) -> str:
        return str(self.raw.get("storyboardRef") or "")

    @property
    def current_stage(self) -> str:
        return str(self.raw.get("currentStage") or "")


def load_direction(repo: Path) -> Direction:
    path = repo / DIRECTION_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{DIRECTION_REL}: root must be object")
    return Direction(raw=data)


def _deprecated_lines(direction: Direction) -> str:
    items = direction.raw.get("deprecatedApproaches") or []
    if not isinstance(items, list) or not items:
        return "- _(none)_"
    return "\n".join(f"- ~~{item}~~ — **retired** by pivot `{direction.pivot_id}`" for item in items)


def _side_channel_lines(direction: Direction) -> str:
    channels = direction.raw.get("sideChannels") or []
    if not isinstance(channels, list) or not channels:
        return "- _(none)_"
    lines: list[str] = []
    for ch in channels:
        if not isinstance(ch, dict):
            continue
        doc = str(ch.get("doc") or "")
        role = str(ch.get("role") or "")
        name = Path(doc).stem if doc else str(ch.get("id") or "channel")
        lines.append(f"- **{name}** ([`{Path(doc).name}`]({doc})) — {role}")
    return "\n".join(lines) if lines else "- _(none)_"


def _build_track_block(direction: Direction) -> str:
    track = direction.raw.get("buildTrack") or {}
    if not isinstance(track, dict):
        return ""
    label = str(track.get("label") or "BUILD track")
    outcome = str(track.get("outcome") or "")
    chapters = track.get("chapters") or []
    chapter_lines = ""
    if isinstance(chapters, list) and chapters:
        chapter_lines = "\n".join(f"  - `{c}`" for c in chapters)
    return f"""**{label}:** {outcome}

{chapter_lines}"""


def render_frontier_block(direction: Direction) -> str:
    return f"""{MARKER_START}
**Direction pivot:** `{direction.pivot_id}` · **as-of:** {direction.as_of}

- **North star:** {direction.north_star}
- **Primary focus:** {direction.primary_focus}
- **Stage:** {direction.current_stage} — storyboard design **complete** ([`storyboard-v0.6`]({direction.storyboard_ref})); **BUILD** integration is active
- **Active BUILD chapter:** `{direction.active_chapter_id}` · plan [`{Path(direction.active_plan_path).name}`]({direction.active_plan_path})
- **Next steward action:** {direction.next_steward_action}

**Retired (do not steer BUILD by these):**
{_deprecated_lines(direction)}

**Side channels (optional, not gates):**
{_side_channel_lines(direction)}
{MARKER_END}"""


def render_integrated_status_block(direction: Direction) -> str:
    return f"""{MARKER_START}
| Field | Value |
|-------|--------|
| **Direction pivot** | `{direction.pivot_id}` ({direction.as_of}) |
| **Primary focus** | {direction.primary_focus} |
| **Design** | Storyboard v0.6 **complete** — [`storyboard-v0.6`]({direction.storyboard_ref}) |
| **Active BUILD** | `{direction.active_chapter_id}` — [`{Path(direction.active_sprint).name}`]({direction.active_sprint}) |
| **Relay plan** | [`{Path(direction.active_plan_path).name}`]({direction.active_plan_path}) |
| **Next** | {direction.next_steward_action} |

{_build_track_block(direction)}
{MARKER_END}"""


def render_playbook_stage_block(direction: Direction) -> str:
    return f"""{MARKER_START}
| Signal | Status |
|--------|--------|
| Storyboard v0.6 (design) | **COMPLETE** — implementation BUILD in flight |
| MSOS shell routes | **Partial** — storyboard screens chartered; integration hardening active |
| PPE inside MSOS | **BUILD** — embed shell + display boundary per [`SPRINT_MSOS_USABLE_DEMO_V1.md`]({direction.active_sprint}) |
| Friends-first / research-first gating | **RETIRED** — pivot `{direction.pivot_id}` |

**Risk:** Premature "chapter COMPLETE" labels while demo is not walkable. Trust **evidence witness checkboxes** and operator demo script, not backlog status alone.
{MARKER_END}"""


def render_mcd_after_pass_block(direction: Direction) -> str:
    return f"""{MARKER_START}
| Field | Value |
|-------|--------|
| **After pass (updated)** | Primary focus → **BUILD usable demo** per [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) pivot `{direction.pivot_id}` |
| **Not a blocker** | Trader workflow research — optional parallel signal logging |
| **BUILD authority** | [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) + active relay plan |
{MARKER_END}"""


def render_factory_focus_block(direction: Direction) -> str:
    return f"""{MARKER_START}
| Priority | Focus |
|----------|--------|
| **1** | **Usable demo BUILD** — MSOS shell + PPE integration ([`SPRINT_MSOS_USABLE_DEMO_V1.md`]({direction.active_sprint})) |
| **2** | **Factory stability** — relay, autobuilder, gates, closeout |
| **Side channel** | Optional validation notes when demo is walkable — **not** a BUILD gate |
{MARKER_END}"""


def render_live_sequence_track_block(direction: Direction) -> str:
    return f"""{MARKER_START}
| Track | Phases | When |
|-------|--------|------|
| **Usable demo (active)** | Storyboard BUILD + production wiring + embed shell + walkable witness | **Now** — pivot `{direction.pivot_id}` |
| **Post-demo expansion** | 4a → 4b → 5 → 6 → 7a → 7b | **Only when SELECTION'd** after usable demo is walkable on production URLs |

Phases 4a–7b remain chartered for multi-user and commercial work — they are **not** the current default BUILD priority.
{MARKER_END}"""


def render_trader_research_banner(direction: Direction) -> str:
    return f"""{MARKER_START}
> **Status (pivot `{direction.pivot_id}`):** **Side channel — not primary BUILD gate.**  
> Run sessions **after** or **in parallel with** usable demo BUILD; log signal in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).  
> Scope authority: [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) · [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md).
{MARKER_END}"""


def render_continuity_active_build(direction: Direction) -> str:
    return f"""{MARKER_START}
**`{direction.active_chapter_id}`** — {direction.primary_focus}

- **Sprint:** [`{Path(direction.active_sprint).name}`]({direction.active_sprint})
- **Plan:** [`{Path(direction.active_plan_path).name}`]({direction.active_plan_path})
- **Direction SSOT:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) (pivot `{direction.pivot_id}`)
{MARKER_END}"""


def render_whats_next(direction: Direction) -> str:
    return f"""# What's next

{MARKER_START}
**Direction pivot:** `{direction.pivot_id}` · **as-of:** {direction.as_of}

**Primary focus:** {direction.primary_focus}

**Next action:** {direction.next_steward_action}

**Design complete:** storyboard v0.6 · **BUILD active:** `{direction.active_chapter_id}`
{MARKER_END}

_New Cursor chat: ask **what's next?** — agent reads this file + `AGENT_CONTINUITY_BRIEF.md` + [`ACTIVE_PRODUCT_DIRECTION.json`](docs/SOP/ACTIVE_PRODUCT_DIRECTION.json)._
"""


def _replace_marked_block(text: str, new_block: str) -> tuple[str, bool]:
    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        flags=re.DOTALL,
    )
    if not pattern.search(text):
        return text, False
    return pattern.sub(new_block, text, count=1), True


def propagate(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    direction = load_direction(repo)
    targets: list[tuple[str, str]] = [
        ("docs/SOP/MSOS_FRONTIER.md", render_frontier_block(direction)),
        ("docs/SOP/PPE_INTEGRATED_STATUS.md", render_integrated_status_block(direction)),
        ("docs/SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md", render_playbook_stage_block(direction)),
        ("docs/SOP/MINIMUM_CREDIBLE_DEMO_GATE_V1.md", render_mcd_after_pass_block(direction)),
        ("docs/SOP/BUILD_FACTORY_BOUNDARY_V1.md", render_factory_focus_block(direction)),
        ("docs/SOP/MSOS_LIVE_PRODUCT_SEQUENCE_V1.md", render_live_sequence_track_block(direction)),
        ("docs/SOP/TRADER_WORKFLOW_RESEARCH_V1.md", render_trader_research_banner(direction)),
        ("docs/SOP/AGENT_CONTINUITY_BRIEF.md", render_continuity_active_build(direction)),
    ]
    whats_next_path = "artifacts/control_plane/WHATS_NEXT.md"
    results: dict[str, Any] = {"pivotId": direction.pivot_id, "updated": [], "skipped": [], "errors": []}

    for rel, block in targets:
        path = repo / rel
        if not path.is_file():
            results["skipped"].append({"path": rel, "reason": "missing"})
            continue
        original = path.read_text(encoding="utf-8")
        if rel == "docs/SOP/AGENT_CONTINUITY_BRIEF.md":
            if MARKER_START in original:
                updated, ok = _replace_marked_block(original, block)
            else:
                updated = re.sub(
                    r"(## Active BUILD\s*\n)(.*?)(\n## )",
                    rf"\1{block}\3",
                    original,
                    count=1,
                    flags=re.DOTALL,
                )
                ok = updated != original
        else:
            updated, ok = _replace_marked_block(original, block)
        if not ok:
            results["skipped"].append({"path": rel, "reason": "markers not found"})
            continue
        if not dry_run:
            path.write_text(updated, encoding="utf-8")
        results["updated"].append(rel)

    wn_full = repo / whats_next_path
    wn_content = render_whats_next(direction)
    if not dry_run:
        wn_full.parent.mkdir(parents=True, exist_ok=True)
        wn_full.write_text(wn_content, encoding="utf-8")
    results["updated"].append(whats_next_path)

    return results
