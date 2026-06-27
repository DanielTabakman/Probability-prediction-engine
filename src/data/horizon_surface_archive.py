"""Options Horizon surface archive — daily BTC options surface snapshots."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from src.engine.implied_distribution import build_distribution_chart_data

SCHEMA_VERSION = 1
REPLAY_THRESHOLD_DAYS = 30
DEFAULT_ARCHIVE_ROOT_NAME = "horizon_surface_archive"
CALL_LADDER_MAX = 24
DEFAULT_GRID_POINTS = 80


def default_archive_root(repo_root: Path | None = None) -> Path:
    root = repo_root or Path(__file__).resolve().parents[2]
    return root / "artifacts" / DEFAULT_ARCHIVE_ROOT_NAME


def default_snapshot_path(
    *,
    as_of_utc: datetime,
    root: Path,
) -> Path:
    day = as_of_utc.astimezone(UTC).strftime("%Y-%m-%d")
    stamp = as_of_utc.astimezone(UTC).strftime("%H%M%S")
    return root / day / f"horizon_surface_{stamp}Z.json"


def _pdf_checksum(pdf_raw: list[float]) -> str:
    payload = json.dumps([round(float(x), 12) for x in pdf_raw], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _nearest_call_ladder(
    calls: list[dict[str, Any]],
    *,
    spot_usd: float,
    max_strikes: int = CALL_LADDER_MAX,
) -> list[dict[str, Any]]:
    if not calls:
        return []
    ranked = sorted(calls, key=lambda row: abs(float(row.get("strike") or 0) - spot_usd))
    out: list[dict[str, Any]] = []
    for row in ranked[:max_strikes]:
        strike = float(row.get("strike") or 0)
        mark_btc = float(row.get("mark_btc") or 0)
        mark_usd = mark_btc * spot_usd
        mark_iv = row.get("mark_iv")
        entry: dict[str, Any] = {"strike": strike, "mark_usd": mark_usd}
        if mark_iv is not None:
            try:
                iv = float(mark_iv)
                if iv > 2:
                    iv = iv / 100.0
                entry["mark_iv"] = iv
            except (TypeError, ValueError):
                pass
        out.append(entry)
    out.sort(key=lambda row: row["strike"])
    return out


def build_expiry_surface_row(
    *,
    expiry_ts: int,
    expiry_date: str,
    spot_usd: float,
    forward_usd: float,
    atm_iv_annual: float,
    T_years: float,
    calls: list[dict[str, Any]],
    asset_id: str = "BTC",
) -> dict[str, Any]:
    price_min = max(1000.0, forward_usd * 0.4)
    price_max = forward_usd * 2.2
    if asset_id != "BTC":
        price_min = max(1.0, forward_usd * 0.35)
        price_max = forward_usd * 2.5
    chart = build_distribution_chart_data(
        forward=forward_usd,
        vol_annual=max(atm_iv_annual, 0.01),
        T_years=max(T_years, 0.02),
        price_min=price_min,
        price_max=price_max,
        num_points=DEFAULT_GRID_POINTS,
    )
    pdf_raw = chart.get("pdf_raw") or []
    return {
        "expiry_ts": int(expiry_ts),
        "expiry_date": expiry_date,
        "forward_usd": forward_usd,
        "atm_iv_annual": atm_iv_annual,
        "T_years": T_years,
        "call_ladder": _nearest_call_ladder(calls, spot_usd=spot_usd),
        "reference_lognormal": {
            "pdf_checksum_sha256": _pdf_checksum(pdf_raw) if pdf_raw else "",
            "grid_points": DEFAULT_GRID_POINTS,
        },
    }


def build_surface_snapshot(
    *,
    as_of_utc: str,
    spot_usd: float,
    expiries: list[dict[str, Any]],
    forward_iv_fn: Callable[[int, float], dict[str, Any] | None],
    marks_full_fn: Callable[[int], dict[str, Any]],
    now_ms: float,
    asset_id: str = "BTC",
    venue: str = "deribit",
) -> dict[str, Any]:
    expiry_rows: list[dict[str, Any]] = []
    for exp in expiries:
        exp_ts = exp.get("expiry_ts")
        if exp_ts is None:
            continue
        try:
            exp_ts_i = int(exp_ts)
        except (TypeError, ValueError):
            continue
        fwd_iv = forward_iv_fn(exp_ts_i, float(spot_usd))
        if not fwd_iv:
            continue
        forward = float(fwd_iv.get("forward") or spot_usd)
        vol = float(fwd_iv.get("atm_iv") or 0.6)
        if vol <= 0:
            vol = 0.6
        T_years = max(0.02, (exp_ts_i - now_ms) / 1000 / (365.25 * 24 * 3600))
        marks = marks_full_fn(exp_ts_i) or {}
        calls = marks.get("calls") or []
        expiry_date = str(exp.get("expiry_date_str") or exp.get("expiry_date") or "")
        expiry_rows.append(
            build_expiry_surface_row(
                expiry_ts=exp_ts_i,
                expiry_date=expiry_date,
                spot_usd=float(spot_usd),
                forward_usd=forward,
                atm_iv_annual=vol,
                T_years=T_years,
                calls=calls,
                asset_id=asset_id,
            )
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "as_of_utc": as_of_utc,
        "asset_id": asset_id,
        "venue": venue,
        "spot_usd": float(spot_usd),
        "expiries": expiry_rows,
    }


def serialize_surface_snapshot(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True)


def load_surface_snapshot(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_as_of(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC)
    text = str(value).strip()
    if len(text) == 10:
        return datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=UTC)
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def list_snapshot_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    files: list[Path] = []
    for day_dir in sorted(root.iterdir()):
        if not day_dir.is_dir():
            continue
        for path in sorted(day_dir.glob("horizon_surface_*.json")):
            files.append(path)
    return files


def archive_meta(root: Path) -> dict[str, Any]:
    files = list_snapshot_files(root)
    if not files:
        return {
            "available_days": 0,
            "earliest_utc": None,
            "latest_utc": None,
            "replay_ready": False,
            "replay_threshold_days": REPLAY_THRESHOLD_DAYS,
        }
    day_dirs = {p.parent.name for p in files}
    earliest = None
    latest = None
    for path in files:
        try:
            snap = load_surface_snapshot(path)
            as_of = _parse_as_of(str(snap.get("as_of_utc") or ""))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if earliest is None or as_of < earliest:
            earliest = as_of
        if latest is None or as_of > latest:
            latest = as_of
    available_days = len(day_dirs)
    return {
        "available_days": available_days,
        "earliest_utc": earliest.isoformat() if earliest else None,
        "latest_utc": latest.isoformat() if latest else None,
        "replay_ready": available_days >= REPLAY_THRESHOLD_DAYS,
        "replay_threshold_days": REPLAY_THRESHOLD_DAYS,
    }


def load_latest_snapshot(root: Path, *, asset_id: str = "BTC") -> dict[str, Any] | None:
    files = list_snapshot_files(root)
    aid = str(asset_id).strip().upper()
    for path in reversed(files):
        try:
            snap = load_surface_snapshot(path)
        except (OSError, json.JSONDecodeError):
            continue
        if str(snap.get("asset_id") or "BTC").upper() == aid:
            return snap
    return None


def load_nearest_snapshot(
    root: Path,
    *,
    as_of: str | datetime,
    asset_id: str = "BTC",
) -> dict[str, Any] | None:
    target = _parse_as_of(as_of)
    aid = str(asset_id).strip().upper()
    best: tuple[datetime, dict[str, Any]] | None = None
    for path in list_snapshot_files(root):
        try:
            snap = load_surface_snapshot(path)
            snap_asset = str(snap.get("asset_id") or "BTC").upper()
            if snap_asset != aid:
                continue
            snap_ts = _parse_as_of(str(snap.get("as_of_utc") or ""))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if snap_ts > target:
            continue
        if best is None or snap_ts > best[0]:
            best = (snap_ts, snap)
    return best[1] if best else None


def build_surface_api_response(
    snapshot: dict[str, Any] | None,
    *,
    archive_root: Path,
) -> dict[str, Any]:
    return {
        "kind": "horizon_surface",
        "snapshot": snapshot,
        "archive_meta": archive_meta(archive_root),
        "meta": {
            "read_only": True,
            "http_path": "/ppe-display-api/horizon/surface.json",
        },
    }
