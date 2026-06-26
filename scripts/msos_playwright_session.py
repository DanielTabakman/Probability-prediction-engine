"""Shared Playwright session helpers for MSOS production witnesses.

Keeps browser contexts aligned with product UX (e.g. skip first-run tutorial overlay).
"""

from __future__ import annotations

from typing import Any

# Must match apps/msos-web/src/lib/platformTutorial.ts
PLATFORM_TUTORIAL_STORAGE_KEY = "msos.platform.tutorial.completed.v1"

_TUTORIAL_DISMISS_INIT_SCRIPT = f"""
try {{
  localStorage.setItem({PLATFORM_TUTORIAL_STORAGE_KEY!r}, "1");
}} catch (e) {{}}
"""


def prepare_msos_browser_context(
    browser: Any,
    *,
    viewport: dict[str, int] | None = None,
) -> Any:
    """Return a Playwright context with MSOS witness defaults (no tutorial scrim)."""
    context = browser.new_context(
        viewport=viewport or {"width": 1440, "height": 900},
    )
    context.add_init_script(_TUTORIAL_DISMISS_INIT_SCRIPT)
    return context


def dismiss_platform_tutorial_if_visible(page: Any) -> None:
    """Fallback when init script did not run (e.g. soft navigation edge)."""
    for label in ("Skip tour", "Done"):
        button = page.get_by_role("button", name=label, exact=True)
        try:
            if button.count() > 0 and button.first.is_visible(timeout=500):
                button.first.click()
                page.wait_for_timeout(250)
                return
        except Exception:
            continue
