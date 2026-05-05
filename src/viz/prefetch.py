"""
Cache warming helpers (Streamlit-friendly).

Goal: improve perceived latency by warming `@st.cache_data` wrappers while the user
is reading/scrolling, so later UI interactions hit warm caches.
"""

from __future__ import annotations

import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable

import streamlit as st


@dataclass
class PrefetchTask:
    label: str
    started_at_s: float
    future: Future


def _get_pool() -> ThreadPoolExecutor:
    # Keep concurrency low to avoid rate-limit bursts.
    # Cache as a resource so it persists across reruns.
    @st.cache_resource
    def _pool() -> ThreadPoolExecutor:
        return ThreadPoolExecutor(max_workers=2)

    return _pool()


def maybe_submit_prefetch(
    *,
    key: str,
    label: str,
    fn: Callable[[], Any],
) -> None:
    """
    Submit a background prefetch if not already running/completed for this key.
    Stores a lightweight handle in session_state.
    """
    state_key = f"prefetch::{key}"
    existing = st.session_state.get(state_key)
    if isinstance(existing, PrefetchTask):
        if not existing.future.done():
            return
        # Completed: keep as a record but don't resubmit automatically.
        return

    pool = _get_pool()
    fut = pool.submit(fn)
    st.session_state[state_key] = PrefetchTask(label=label, started_at_s=time.time(), future=fut)


def prefetch_status() -> dict[str, Any]:
    """Summarize outstanding prefetch tasks (for debug/perf panels)."""
    out: dict[str, Any] = {}
    for k, v in list(st.session_state.items()):
        if not str(k).startswith("prefetch::"):
            continue
        if not isinstance(v, PrefetchTask):
            continue
        try:
            done = bool(v.future.done())
        except Exception:
            done = False
        out[str(k)] = {"label": v.label, "done": done, "age_s": round(time.time() - v.started_at_s, 1)}
    return out

