"""Exercise the real signed metadata chain, payload bytes and project gates."""

from dataclasses import replace
from datetime import timedelta
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from swarm_rejoin.fixture_repository import SignedFixtureRepository, release_fields
from swarm_rejoin.verification import Rejected, ReleaseVerifier, SecurityPolicy


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = SignedFixtureRepository()
        self.repo.add("app.bin", b"actual payload bytes for verification", release_fields("v1"))
        self.repo.publish()
        self.policy = SecurityPolicy()
        self.client = ReleaseVerifier(self.repo.bootstrap, self.root / "client", self.repo.fetcher,
                                      self.policy, trusted_host_clock=True)

    def rejects(self, reason, target="app.bin"):
        with self.assertRaises(Rejected) as caught:
            self.client.verify(target)
        self.assertEqual(caught.exception.reason, reason)

    def republish(self, **changes):
        payload, custom = self.repo.packages["app.bin"]
        self.repo.add("app.bin", payload, {**custom, **changes})
        self.repo.publish()

    def test_real_signed_chain_and_exact_bytes(self):
        artifact = self.client.verify("app.bin")
        self.assertEqual(artifact.payload, self.repo.packages["app.bin"][0])
        self.assertEqual(artifact.sha256, hashlib.sha256(artifact.payload).hexdigest())
        self.assertEqual(artifact.release.release_id, "v1")

    def test_valid_json_with_wrong_timestamp_signature_is_rejected(self):
        path = "/metadata/timestamp.json"
        obj = json.loads(self.repo.routes[path])
        obj["signed"]["version"] += 1
        self.repo.routes[path] = json.dumps(obj).encode()
        self.rejects("TUF_VERIFICATION_FAILED")

    def test_tampered_payload_same_length_is_rejected(self):
        target = next(p for p in self.repo.routes if p.startswith("/targets/"))
        data = self.repo.routes[target]
        self.repo.routes[target] = bytes([data[0] ^ 1]) + data[1:]
        self.rejects("TUF_VERIFICATION_FAILED")

    def test_partial_transfer_cannot_return_verified_artifact(self):
        self.repo.fetcher.truncate_targets = True
        self.rejects("TUF_VERIFICATION_FAILED")

    def test_expired_metadata_is_not_accepted(self):
        self.repo.publish(expires=self.repo.created_at - timedelta(days=1))
        self.rejects("TUF_VERIFICATION_FAILED")

    def test_cached_metadata_rejects_replayed_timestamp(self):
        self.repo.publish(version=2)
        self.client.verify("app.bin")
        self.repo.publish(version=1)
        self.rejects("TUF_VERIFICATION_FAILED")

    def test_unrelated_trust_anchor_rejects_repository(self):
        self.client.bootstrap = SignedFixtureRepository().bootstrap
        self.rejects("TUF_VERIFICATION_FAILED")

    def test_untrusted_clock_defers_without_target_transfer(self):
        self.client.trusted_host_clock = False
        self.rejects("TRUSTED_TIME_UNAVAILABLE")
        self.assertEqual(self.repo.fetcher.target_requests, 0)

    def test_signed_but_inapplicable_project_fields(self):
        for changes, reason in (
            ({"platform": "another-device"}, "WRONG_TARGET"),
            ({"component": "flight-controller"}, "WRONG_TARGET"),
            ({"protocol": "incompatible"}, "INCOMPATIBLE_PROTOCOL"),
            ({"data_schema": "migration-required"}, "INCOMPATIBLE_DATA_SCHEMA"),
            ({"security_epoch": 0}, "SECURITY_EPOCH_PROHIBITED"),
            ({"security_epoch": True}, "INVALID_RELEASE_FIELDS"),
            ({"schema_version": 2}, "UNSUPPORTED_RELEASE_SCHEMA"),
            ({"activation_profile": "airborne"}, "UNSUPPORTED_ACTIVATION_PROFILE"),
            ({"health_profile": "ignore-health"}, "UNSUPPORTED_HEALTH_PROFILE"),
            ({"new_mandatory_field": "ignored?"}, "INVALID_RELEASE_FIELDS"),
        ):
            with self.subTest(changes=changes):
                payload = self.repo.packages["app.bin"][0]
                self.repo.add("app.bin", payload, release_fields("v1", **changes))
                self.repo.publish()
                # Each subtest uses a distinct local cache, avoiding test order
                # effects from same-version but modified signed metadata.
                self.client.cache = self.root / ("client-" + str(len(list(self.root.iterdir()))))
                (self.client.cache / "metadata").mkdir(parents=True)
                (self.client.cache / "targets").mkdir()
                self.rejects(reason)

    def test_missing_required_project_field(self):
        payload, fields = self.repo.packages["app.bin"]
        fields.pop("security_epoch")
        self.repo.add("app.bin", payload, fields)
        self.repo.publish()
        self.rejects("INVALID_RELEASE_FIELDS")

    def test_revoked_release_is_rejected(self):
        self.policy.revoked.add("v1")
        self.rejects("RELEASE_REVOKED")

    def test_payload_limit_is_checked_before_download(self):
        self.policy.max_payload_bytes = 1
        self.rejects("PAYLOAD_TOO_LARGE")
        self.assertEqual(self.repo.fetcher.target_requests, 0)

    def test_malicious_target_paths_are_rejected(self):
        for target in ("../app.bin", "/app.bin", "x/app.bin", "https://evil/app.bin", "C:\\app.bin"):
            with self.subTest(target=target):
                self.rejects("INVALID_TARGET_PATH", target)

    def test_unknown_target_is_rejected(self):
        self.rejects("TARGET_NOT_AUTHORIZED", "missing.bin")

    def test_bytes_are_rechecked_at_use(self):
        original = self.client.verify("app.bin")
        changed = replace(original, payload=b"unverified replacement")
        with self.assertRaisesRegex(Rejected, "ARTIFACT_CHANGED"):
            self.policy.appraise(changed)

    def test_security_floor_cannot_regress(self):
        self.policy.raise_floor(2)
        with self.assertRaisesRegex(Rejected, "SECURITY_FLOOR_REGRESSION"):
            self.policy.raise_floor(1)
        self.assertEqual(self.policy.floor, 2)


if __name__ == "__main__":
    unittest.main()
