"""One-shot: verify Cursor Automation webhook credentials (no secrets printed)."""

from __future__ import annotations

import sys
from pathlib import Path

from scripts.ppe_ide_build_automation_trigger import post_automation_webhook


def main() -> int:
    repo = Path(".").resolve()
    result = post_automation_webhook(
        repo,
        {"event": "ppe_connectivity_ping", "note": "local wiring check — ignore unless slice pending"},
    )
    if result.get("skipped"):
        print(f"ppe_test_automation_webhook: skipped ({result.get('reason')})")
        return 1
    if result.get("ok"):
        print(f"ppe_test_automation_webhook: ok HTTP {result.get('status')}")
        return 0
    print(f"ppe_test_automation_webhook: failed {result.get('error')} {result.get('detail', '')}".strip())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
