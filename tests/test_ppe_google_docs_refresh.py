"""Tests for queue-idle Google Docs refresh helpers."""

from __future__ import annotations

import os
import unittest

from scripts.ppe_google_docs_refresh import idle_refresh_enabled, mirror_credentials_configured


class TestPpeGoogleDocsRefresh(unittest.TestCase):
    def test_idle_refresh_default_on(self) -> None:
        os.environ.pop("PPE_GOOGLE_DOCS_ON_IDLE", None)
        self.assertTrue(idle_refresh_enabled())

    def test_idle_refresh_opt_out(self) -> None:
        os.environ["PPE_GOOGLE_DOCS_ON_IDLE"] = "0"
        self.assertFalse(idle_refresh_enabled())
        os.environ.pop("PPE_GOOGLE_DOCS_ON_IDLE", None)

    def test_mirror_credentials_requires_mirror_id(self) -> None:
        for key in (
            "PPE_MSOS_MIRROR_DOC_ID",
            "MSOS_REPO_TRUTH_DOC_ID",
            "GOOGLE_OAUTH_CLIENT_ID",
            "GOOGLE_OAUTH_CLIENT_SECRET",
            "GOOGLE_OAUTH_REFRESH_TOKEN",
        ):
            os.environ.pop(key, None)
        self.assertFalse(mirror_credentials_configured())


if __name__ == "__main__":
    unittest.main()
