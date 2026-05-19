"""
Seed the Validation Chapter evidence clock (operator-prep).

Uses the same SQLite store as the implied lab. Idempotent: skips insert if DB already
meets targets (≥10 freezes, ≥5 non-pending reviews).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
from src.viz.frozen_evaluation_store import (
    default_db_path,
    init_schema,
    insert_record,
    list_completed_review_snapshots,
    open_store,
    review_horizon_ref_from_frozen,
    upsert_review,
)

TARGET_FREEZES = 10
TARGET_REVIEWS = 5
_REVIEW_STATUSES = ("supportive", "contradictory", "not_judgeable", "supportive", "contradictory")


def _sample_verification(i: int) -> dict:
    states = ("candidate", "watch_only", "no_trade")
    return {
        "verification_summary": {
            "as_of_utc": f"2026-05-19T12:{i:02d}:00Z",
            "disagreement_category_id": "width_vol",
            "contract_schema_version": "validation-chapter-seed-v0",
            "primary_output_state": states[i % 3],
            "data_quality": "usable",
        },
        "density": {
            "reference_risk_neutral": {
                "method": "seed",
                "forward_usd": 100_000.0 + i * 100,
                "atm_iv_annual": 0.5,
                "T_years": 0.08,
                "grid_price_min_usd": 50_000.0,
                "grid_price_max_usd": 150_000.0,
                "grid_points": 12,
            }
        },
        "belief_disagreement": {"contract_schema_version": "validation-chapter-seed-v0"},
    }


def main() -> int:
    path = default_db_path()
    conn = open_store(path)
    try:
        init_schema(conn)
        frozen_n = conn.execute("SELECT COUNT(*) FROM frozen_evaluations").fetchone()[0]
        review_n = len(list_completed_review_snapshots(conn, limit=500))
        if frozen_n >= TARGET_FREEZES and review_n >= TARGET_REVIEWS:
            print(f"Already at targets: frozen={frozen_n} reviews={review_n} ({path})")
            return 0

        ids: list[str] = []
        need = max(0, TARGET_FREEZES - frozen_n)
        for i in range(need):
            v = _sample_verification(frozen_n + i)
            rec = build_frozen_evaluation_record(
                verification=v,
                expiry_str=f"{(frozen_n + i) % 28 + 1}MAY26",
                operator_note=f"validation-chapter-seed-{frozen_n + i}",
            )
            ids.append(insert_record(conn, rec))

        existing_ids = [
            r["id"]
            for r in conn.execute(
                "SELECT id FROM frozen_evaluations ORDER BY created_at DESC LIMIT ?",
                (TARGET_FREEZES,),
            ).fetchall()
        ]
        review_n = len(list_completed_review_snapshots(conn, limit=500))
        need_reviews = max(0, TARGET_REVIEWS - review_n)
        for j in range(need_reviews):
            sid = existing_ids[j % len(existing_ids)]
            got = conn.execute(
                "SELECT record_json FROM frozen_evaluations WHERE id = ?", (sid,)
            ).fetchone()
            import json

            record = json.loads(got["record_json"]) if got else {}
            status = _REVIEW_STATUSES[j % len(_REVIEW_STATUSES)]
            upsert_review(
                conn,
                snapshot_id=sid,
                review_status=status,
                outcome_notes=f"validation-chapter-seed review {j}",
                review_horizon_ref=review_horizon_ref_from_frozen(record) if record else None,
            )

        frozen_n = conn.execute("SELECT COUNT(*) FROM frozen_evaluations").fetchone()[0]
        review_n = len(list_completed_review_snapshots(conn, limit=500))
        print(f"Seeded evidence clock: frozen={frozen_n} completed_reviews={review_n} ({path})")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
