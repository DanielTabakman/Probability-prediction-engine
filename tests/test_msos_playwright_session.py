"""MSOS Playwright session helpers — storage key parity with product."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_platform_tutorial_storage_key_matches_product() -> None:
    from scripts.msos_playwright_session import PLATFORM_TUTORIAL_STORAGE_KEY

    ts = (REPO_ROOT / "apps/msos-web/src/lib/platformTutorial.ts").read_text(encoding="utf-8")
    assert f'PLATFORM_TUTORIAL_STORAGE_KEY = "{PLATFORM_TUTORIAL_STORAGE_KEY}"' in ts
