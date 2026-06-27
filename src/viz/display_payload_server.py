"""WSGI entrypoint for read-only distribution display API (platform proxy target)."""

from __future__ import annotations

import os
from wsgiref.simple_server import make_server

from src.viz.embed_display_boundary import (
    build_cached_live_distribution_display_payload,
    create_display_payload_wsgi_app,
)


def main() -> None:
    port = int(os.environ.get("PORT", "8765"))
    app = create_display_payload_wsgi_app(build_cached_live_distribution_display_payload)
    with make_server("", port, app) as httpd:
        print(f"ppe_display_api listening on :{port}", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
