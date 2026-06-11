"""Print Cursor IDE BUILD automation setup and write a copy-paste artifact."""

from __future__ import annotations

import argparse
import json
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppe_ide_build_automation_trigger import TRIGGER_REL

PROMPT_REL = ".cursor/IDE_BUILD_AUTOMATION_PROMPT.md"
SETUP_REL = "artifacts/orchestrator/CURSOR_IDE_BUILD_AUTOMATION_SETUP.md"
AUTOMATIONS_URL = "https://cursor.com/automations"
DOCS_REL = "docs/SOP/CURSOR_IDE_BUILD_AUTOMATION_V1.md"
HANDOFF_STATE_REL = "artifacts/orchestrator/IDE_HANDOFF_STATE.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_prompt(repo: Path) -> str:
    path = repo / PROMPT_REL
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return (
        "Read .cursor/IDE_BUILD_TRIGGER.json.\n"
        "If status is not pending, exit with no-op.\n"
        "Load ONLY the starter path from the trigger.\n"
        "Follow starter ## When done (required). Execute autonomously."
    )


def build_setup_markdown(repo: Path) -> str:
    repo = repo.resolve()
    prompt = _load_prompt(repo)
    return f"""# Cursor IDE BUILD automation — setup checklist

Generated: {_utc_now()}

## Important

Cursor Automations **cannot** use `.md` as a file trigger. Use **JSON** instead.

## 1. Open Automations

- Cursor desktop: **Agents → Automations → Create automation**
- Or web: {AUTOMATIONS_URL}

## 2. Automation fields (primary)

| Field | Value |
|-------|-------|
| **Name** | `PPE IDE BUILD on handoff` |
| **Trigger** | File change |
| **Watch path** | `{TRIGGER_REL}` |
| **Workspace** | `{repo}` |
| **Action** | Run Agent |

## 3. Alternate trigger (if `.cursor/` not watchable)

| Field | Value |
|-------|-------|
| **Trigger** | File change |
| **Watch path** | `{HANDOFF_STATE_REL}` |

Prompt addition: read `last_handoff_slice` and `last_starter` from that JSON, then same BUILD steps.

## 4. Agent prompt (paste into Action)

```
{prompt}
```

Full prompt file: `{PROMPT_REL}`

## 5. Permissions

Allow terminal commands used in starter closeout:

- `python scripts/run_pushable_gate.py`
- `git commit`
- `mark_ide_product_ready.cmd`
- `run_ppe_local.cmd`

## 6. Optional webhook

Set in `ppe_operator_local.cmd` or environment:

- `PPE_CURSOR_AUTOMATION_WEBHOOK_URL` — Cursor Automation webhook URL
- `PPE_CURSOR_AUTOMATION_WEBHOOK_KEY` — Bearer token (if required)

Handoff POSTs after writing `{TRIGGER_REL}`.

## 7. Verify

1. `run_ppe_operator.cmd --brief` → `IDE_BUILD` when a product slice is pending
2. `open_ide_handoff.cmd` → `{TRIGGER_REL}` shows `"status": "pending"`
3. Automation starts Agent within ~1 minute
4. After closeout: trigger `"status": "idle"`; relay continues

## Related

- `{DOCS_REL}`
- `{PROMPT_REL}`
- `finish_ide_build.cmd`
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Cursor IDE BUILD automation setup helper")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--open-browser", action="store_true", help="Open cursor.com/automations")
    ap.add_argument("--json", action="store_true", help="Emit JSON summary to stdout")
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    body = build_setup_markdown(repo)
    out = repo / SETUP_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")

    summary = {
        "action": "cursor_ide_automation_setup",
        "setupArtifact": SETUP_REL.replace("\\", "/"),
        "automationsUrl": AUTOMATIONS_URL,
        "triggerPath": TRIGGER_REL,
        "alternateTriggerPath": HANDOFF_STATE_REL,
        "promptPath": PROMPT_REL.replace("\\", "/"),
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"ppe_cursor_ide_automation_setup: wrote {out}")
        print(f"ppe_cursor_ide_automation_setup: trigger {TRIGGER_REL} (not .md)")
        print(f"ppe_cursor_ide_automation_setup: open {AUTOMATIONS_URL}")
    if args.open_browser:
        webbrowser.open(AUTOMATIONS_URL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
