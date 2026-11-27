"""Check the CLI contract, independent fixture labels and repeatable trace."""

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from swarm_rejoin.demo import label_role, load_config, main, run_fixture


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_expected_transition_sequence_and_session_reappraisal(self):
        events, truth, public = run_fixture(load_config(), self.root / "cache")
        self.assertEqual(len(events), 9)
        self.assertEqual(len(truth), 54)
        self.assertEqual(events[1]["expected_rejection"], "TUF_VERIFICATION_FAILED")
        self.assertEqual(events[1]["active_release"], "release-1")
        self.assertEqual(events[3]["phase"], "HEALTH_CHECK")
        self.assertEqual(events[4]["phase"], "RECOVERING")
        self.assertEqual(events[5]["reason"], "NAVIGATION_SESSION_MISMATCH")
        self.assertEqual(events[7]["roles"]["U1"], "precision-search")
        self.assertIsNone(events[-1]["roles"]["U1"])
        self.assertEqual(events[-1]["reason"], "PERMISSION_EXPIRED")
        self.assertEqual(len({e["producer_boot"] for e in events}), 1)
        self.assertIn("bootstrap", public)
        self.assertTrue(all("BEGIN PRIVATE KEY" not in str(value) for value in public.values()))

    def test_event_trace_is_repeatable_with_fresh_random_signing_keys(self):
        first = run_fixture(load_config(), self.root / "one")
        second = run_fixture(load_config(), self.root / "two")
        self.assertEqual(first[:2], second[:2])
        self.assertNotEqual(first[2]["bootstrap"], second[2]["bootstrap"])

    def test_independent_label_can_report_unsafe_grant_despite_policy_acceptance(self):
        self.assertTrue(label_role("precision-search", False)["unsafe_grant"])
        self.assertFalse(label_role(None, True)["unsafe_grant"])

    def test_invalid_configuration_is_rejected_before_running(self):
        for transform in (
            lambda c: {**c, "schema_version": True},
            lambda c: {**c, "vehicles": ["U1"] * 6},
            lambda c: {**c, "seed": False},
            lambda c: {**c, "events": [None]},
            lambda c: {**c, "events": [{"time": -1, "action": "initial_evidence"}] + c["events"][1:]},
            lambda c: {**c, "unknown": "do not ignore"},
            lambda c: [],
        ):
            path = self.root / "invalid.json"
            path.write_text(json.dumps(transform(load_config())), encoding="utf-8")
            with self.subTest(configuration=path.read_text()):
                with self.assertRaises(ValueError):
                    load_config(path)

    def test_output_contains_provenance_truth_and_public_material_only(self):
        output = self.root / "run"
        with redirect_stdout(StringIO()):
            self.assertEqual(main(["--output", str(output)]), 0)
        self.assertEqual({p.name for p in output.iterdir()}, {
            "run.json", "events.jsonl", "fixture-truth.jsonl", "public-repository.json",
            "artifacts.sha256.json",
        })
        run = json.loads((output / "run.json").read_text())
        self.assertIn("revision", run)
        self.assertEqual(run["seed"], 0)
        self.assertEqual(run["dependencies"]["tuf"], "7.0.1")
        self.assertEqual(run["fixture_outcomes"]["events"], 9)
        for path in output.iterdir():
            self.assertNotIn("BEGIN PRIVATE KEY", path.read_text())
        self.assertEqual(json.loads((output / "events.jsonl").read_text().splitlines()[0])["time"], 1)
        hashes = json.loads((output / "artifacts.sha256.json").read_text())
        for name, expected in hashes.items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), expected)

    def test_existing_output_is_not_overwritten(self):
        output = self.root / "run"
        output.mkdir()
        sentinel = output / "sentinel.txt"
        sentinel.write_text("preserve existing work", encoding="utf-8")
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as caught:
                main(["--output", str(output)])
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(sentinel.read_text(), "preserve existing work")


if __name__ == "__main__":
    unittest.main()
