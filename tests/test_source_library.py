"""Check that the archive cannot silently claim missing or modified material."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from source_library import digest, resolve_source_links, validate_library, write_catalog


class SourceLibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "research/literature").mkdir(parents=True)
        (self.root / "research/literature/sources.json").write_text('[{"id":"example"}]', encoding="utf-8")
        folder = self.root / "research/library/example"
        folder.mkdir(parents=True)
        record = folder / "README.md"
        record.write_text("# Original source record\n", encoding="utf-8")
        content = folder / "full-text.md"
        content.write_text("# Original source text\n", encoding="utf-8")
        self.entry = {
            "source_id": "example", "canonical_url": "https://example.org/source",
            "retrieved_on": "2026-11-10", "status": "full_text",
            "record_path": "research/library/example/README.md", "record_sha256": digest(record),
            "pdf_status": "not_located", "reason": "No original PDF located.",
            "rights": {"license_id": "CC-BY-4.0", "redistribution": "permitted", "evidence_url": "https://example.org/license"},
            "artifacts": [{"kind": "markdown", "path": "research/library/example/full-text.md", "sha256": digest(content)}],
        }

    def check(self, entries=None):
        manifest = {"schema_version": "1.0", "sources": entries if entries is not None else [self.entry]}
        (self.root / "research/library/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return validate_library(self.root)[0]

    def test_valid_capture(self):
        self.assertEqual(self.check(), [])

    def test_changed_content_is_detected(self):
        (self.root / self.entry["artifacts"][0]["path"]).write_text("changed", encoding="utf-8")
        self.assertTrue(any("SHA-256 mismatch" in error for error in self.check()))

    def test_missing_registered_source_is_detected(self):
        self.assertTrue(any("coverage mismatch" in error for error in self.check([])))

    def test_full_text_requires_rights_evidence(self):
        self.entry["rights"]["redistribution"] = "unconfirmed"
        self.assertTrue(any("redistribution evidence" in error for error in self.check()))

    def test_full_text_requires_actual_markdown(self):
        self.entry["artifacts"] = []
        self.assertTrue(any("Markdown capture" in error for error in self.check()))

    def test_record_only_cannot_claim_a_full_text_file(self):
        self.entry["status"] = "record_only"
        self.assertTrue(any("conflicts" in error for error in self.check()))

    def test_pdf_error_page_is_rejected_even_with_a_matching_hash(self):
        path = self.root / "research/library/example/source.pdf"
        path.write_bytes(b"<html>Access denied</html>")
        self.entry["pdf_status"] = "archived"
        self.entry["artifacts"].append({"kind": "pdf", "path": path.relative_to(self.root).as_posix(), "sha256": digest(path)})
        self.assertTrue(any("not a PDF" in error for error in self.check()))

    def test_path_escape_is_rejected(self):
        self.entry["artifacts"][0]["path"] = "../outside.md"
        self.assertTrue(any("leaves workspace" in error for error in self.check()))

    def test_duplicate_records_are_rejected(self):
        self.assertTrue(any("duplicate" in error for error in self.check([self.entry, copy.deepcopy(self.entry)])))

    def test_source_relative_links_resolve_without_changing_anchors(self):
        text = "[Guide](../guide.md) [Part](#part) [External](https://example.net/)\n[ref]: ../ref.md\n"
        resolved = resolve_source_links(text, "https://example.org/en/topic/page.md")
        self.assertIn("[Guide](https://example.org/en/guide.md)", resolved)
        self.assertIn("[Part](#part)", resolved)
        self.assertIn("[ref]: https://example.org/en/ref.md", resolved)

    def test_catalog_uses_lf_on_windows_to_preserve_git_hashes(self):
        write_catalog(self.root, [self.entry])
        self.assertNotIn(b"\r\n", (self.root / "research/library/manifest.json").read_bytes())
        self.assertNotIn(b"\r\n", (self.root / "research/library/README.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
