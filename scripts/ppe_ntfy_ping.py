"""Send one ntfy ping (phone delivery test). Usage: after ppe_operator_local.cmd"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts.ppe_notify_push import ntfy_configured, notify_enabled, ntfy_topic, send_ntfy


def main() -> int:
    if not notify_enabled():
        print("FAIL: PPE_NOTIFY disabled", file=sys.stderr)
        return 1
    if not ntfy_configured():
        print("FAIL: PPE_NTFY_TOPIC not set", file=sys.stderr)
        return 1
    topic = ntfy_topic()
    ok = send_ntfy(
        "PPE ping",
        f"Delivery test from desktop. Topic={topic}",
        tags=["ppe", "test"],
        priority="high",
        bypass_throttle=True,
    )
    if ok:
        print(f"OK: sent to topic {topic}")
        return 0
    print("FAIL: ntfy POST failed (network or topic)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
