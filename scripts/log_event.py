from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_PATH_DEFAULT = Path("artifacts") / "logbook" / "ppe_events.jsonl"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Ref:
    kind: str
    path: str
    sha: str | None = None
    run_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"kind": self.kind, "path": self.path}
        if self.sha:
            d["sha"] = self.sha
        if self.run_id:
            d["run_id"] = self.run_id
        return d


def _parse_ref(raw: str) -> Ref:
    # Format: "kind=<k>,path=<p>[,sha=<sha>][,run_id=<id>]"
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    kv: dict[str, str] = {}
    for p in parts:
        if "=" not in p:
            raise ValueError(f"Bad ref segment (expected k=v): {p!r}")
        k, v = p.split("=", 1)
        kv[k.strip()] = v.strip()
    kind = kv.get("kind")
    path = kv.get("path")
    if not kind or not path:
        raise ValueError("Ref must include kind=<...> and path=<...>")
    return Ref(kind=kind, path=path, sha=kv.get("sha"), run_id=kv.get("run_id"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Append one PPE log event (JSONL).")
    ap.add_argument("--log-path", default=str(LOG_PATH_DEFAULT))
    ap.add_argument("--event-type", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--actor", default=os.environ.get("PPE_ACTOR", "local"))
    ap.add_argument("--phase", default=os.environ.get("PPE_PHASE", "mvp1"))
    ap.add_argument("--output-state", default=None)
    ap.add_argument("--ref", action="append", default=[], help="ref: kind=...,path=...[,sha=...][,run_id=...]")
    args = ap.parse_args()

    refs = [_parse_ref(r).to_dict() for r in (args.ref or [])]
    event: dict[str, Any] = {
        "ts_utc": _utc_now_iso(),
        "event_type": str(args.event_type),
        "summary": str(args.summary),
        "actor": str(args.actor),
        "phase": str(args.phase),
    }
    if args.output_state:
        event["output_state"] = str(args.output_state)
    if refs:
        event["refs"] = refs

    log_path = Path(args.log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

