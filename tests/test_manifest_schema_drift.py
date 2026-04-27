"""Drift-detection test: asserts that MANIFEST_SCHEMA_VERSION in harness matches
the canonical version declared in docs/SOP/MANIFEST_SCHEMA.md.

Failure message:
    Schema drift: code MANIFEST_SCHEMA_VERSION=<code>, docs=<docs>.
    Update docs/SOP/MANIFEST_SCHEMA.md or bump the constant.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.implied_lab_ui_smoke_harness import MANIFEST_SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DOC = ROOT / "docs" / "SOP" / "MANIFEST_SCHEMA.md"

_VERSION_RE = re.compile(r"Canonical schema version:\s*v(\d+)", re.IGNORECASE)


class TestManifestSchemaDrift(unittest.TestCase):
    def test_code_matches_docs(self) -> None:
        self.assertTrue(
            SCHEMA_DOC.is_file(),
            f"Schema doc not found: {SCHEMA_DOC}",
        )
        text = SCHEMA_DOC.read_text(encoding="utf-8")
        m = _VERSION_RE.search(text)
        self.assertIsNotNone(
            m,
            f"Could not find 'Canonical schema version: vN' in {SCHEMA_DOC}",
        )
        assert m is not None
        docs_version = int(m.group(1))
        self.assertEqual(
            MANIFEST_SCHEMA_VERSION,
            docs_version,
            (
                f"Schema drift: code MANIFEST_SCHEMA_VERSION={MANIFEST_SCHEMA_VERSION}, "
                f"docs={docs_version}. "
                f"Update docs/SOP/MANIFEST_SCHEMA.md or bump the constant."
            ),
        )
