"""Tests for the production display payload WSGI server."""

from __future__ import annotations

from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer

from src.viz.display_payload_server import ThreadingWSGIServer


def test_display_payload_server_is_threaded() -> None:
    assert issubclass(ThreadingWSGIServer, ThreadingMixIn)
    assert issubclass(ThreadingWSGIServer, WSGIServer)
    assert ThreadingWSGIServer.daemon_threads is True
