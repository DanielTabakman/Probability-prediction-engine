"""Print Validation Chapter evidence-clock counts from the snapshot SQLite DB."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.frozen_evaluation_store import default_db_path, init_schema, list_completed_review_snapshots, open_store


def main() -> int:
    path = default_db_path()
    if not path.is_file():
        print(f"frozen_count=0")
        print(f"completed_review_count=0")
        print(f"db_path={path} (missing)")
        return 0
    conn = open_store(path)
    try:
        init_schema(conn)
        frozen = conn.execute("SELECT COUNT(*) FROM frozen_evaluations").fetchone()[0]
        completed = len(list_completed_review_snapshots(conn, limit=500))
        print(f"frozen_count={frozen}")
        print(f"completed_review_count={completed}")
        print(f"db_path={path}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
