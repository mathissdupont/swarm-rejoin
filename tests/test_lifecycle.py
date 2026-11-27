"""Behavioral lifecycle/role tests with actual verified artifact fixtures."""

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from swarm_rejoin.fixture_repository import SignedFixtureRepository, release_fields
from swarm_rejoin.lifecycle import (
    ModeledVehicle, NavigationEvidence, OperationalEvidence, Phase, ProducerContext, RoleRule,
)
from swarm_rejoin.verification import Rejected, ReleaseVerifier, SecurityPolicy


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = SignedFixtureRepository()
        self.repo.add("old.bin", b"healthy existing application", release_fields("old"))
        self.repo.add("new.bin", b"candidate application", release_fields("new", 2))
        self.repo.publish()
        self.policy = SecurityPolicy()
        self.verifier = ReleaseVerifier(self.repo.bootstrap, Path(self.temp.name), self.repo.fetcher,
                                        self.policy, trusted_host_clock=True)
        self.node = ModeledVehicle("U1", self.verifier, self.verifier.verify("old.bin"))
        self.context = ProducerContext("boot-1", "config-1", "frame-1")
        self.node.set_producer(self.context)
        self.rule = RoleRule()

    def evidence(self, time=1, **changes):
        return replace(NavigationEvidence("U1", self.node.session, self.context, time, 0.5), **changes)

    def airborne(self, time=1):
        self.node.observe_operational(OperationalEvidence(False, True, time))
        self.node.observe_navigation(self.evidence(time))

    def ground(self, time=1):
        self.node.observe_operational(OperationalEvidence(True, False, time))

    def activate(self):
        self.ground()
        self.node.stage("new.bin")
        self.node.begin_activation(1)

    def test_partial_transfer_preserves_active_application_and_grant(self):
        self.airborne()
        self.assertIsNotNone(self.node.request_role(1, self.rule))
        before = self.node.active
        self.repo.fetcher.truncate_targets = True
        with self.assertRaises(Rejected):
            self.node.stage("new.bin")
        self.assertEqual(self.node.phase, Phase.IDLE)
        self.assertIsNone(self.node.staged)
        self.assertEqual(self.node.active, before)
        self.assertEqual(self.node.role_at(2), self.rule.role)

    def test_stage_is_allowed_airborne_but_activation_is_deferred(self):
        self.airborne()
        self.node.stage("new.bin")
        with self.assertRaisesRegex(Rejected, "GROUND_REQUIRED"):
            self.node.begin_activation(1)
        self.assertEqual(self.node.active.release.release_id, "old")
        self.assertEqual(self.node.phase, Phase.STAGED)

    def test_stale_ground_report_does_not_allow_activation(self):
        self.ground()
        self.node.stage("new.bin")
        with self.assertRaisesRegex(Rejected, "OPERATIONAL_EVIDENCE_STALE"):
            self.node.begin_activation(6)

    def test_activation_rechecks_revocation_after_staging(self):
        self.ground()
        self.node.stage("new.bin")
        self.policy.revoked.add("new")
        with self.assertRaisesRegex(Rejected, "RELEASE_REVOKED"):
            self.node.begin_activation(1)
        self.assertEqual(self.node.active.release.release_id, "old")

    def test_modified_staged_bytes_cannot_activate(self):
        self.ground()
        self.node.stage("new.bin")
        self.node.staged = replace(self.node.staged, payload=b"different bytes")
        with self.assertRaisesRegex(Rejected, "ARTIFACT_CHANGED"):
            self.node.begin_activation(1)

    def test_activation_interlock_and_no_role_while_unhealthy(self):
        self.activate()
        self.assertFalse(self.node.arming_permitted())
        self.assertIsNone(self.node.request_role(1, RoleRule(role="observation", requires_airborne=False)))
        with self.assertRaisesRegex(Rejected, "TRANSITION_BUSY"):
            self.node.stage("new.bin")

    def test_candidate_failure_recovers_authorized_image_with_new_session(self):
        initial_session = self.node.session
        self.node.observe_navigation(self.evidence())
        self.activate()
        self.node.report_health(False, 2)
        self.assertEqual(self.node.phase, Phase.RECOVERING)
        self.assertEqual(self.node.active.release.release_id, "old")
        self.assertFalse(self.node.healthy)
        self.node.report_health(True, 3)
        self.assertEqual(self.node.phase, Phase.IDLE)
        self.assertNotEqual(self.node.session, initial_session)
        self.assertEqual(self.node.producer, self.context)
        self.assertIsNone(self.node.request_role(3, RoleRule(role="observation", requires_airborne=False)))
        self.assertEqual(self.node.last_reason, "NAVIGATION_SESSION_MISMATCH")
        self.node.observe_navigation(self.evidence(3))
        self.assertIsNotNone(self.node.request_role(3, RoleRule(role="observation", requires_airborne=False)))

    def test_new_successful_candidate_requires_fresh_appraisal(self):
        self.activate()
        self.node.report_health(True, 2)
        self.assertEqual(self.node.active.release.release_id, "new")
        self.assertIsNone(self.node.grant)
        self.assertTrue(self.node.arming_permitted())

    def test_revoked_fallback_is_not_used(self):
        self.activate()
        self.policy.revoked.add("old")
        self.node.report_health(False, 2)
        self.assertEqual(self.node.phase, Phase.FAILED)
        self.assertIn("RELEASE_REVOKED", self.node.last_reason)
        self.assertFalse(self.node.arming_permitted())
        self.assertIsNone(self.node.grant)

    def test_fallback_below_current_security_floor_is_not_used(self):
        self.activate()
        self.policy.raise_floor(2)
        self.node.report_health(False, 2)
        self.assertEqual(self.node.phase, Phase.FAILED)
        self.assertIn("SECURITY_EPOCH_PROHIBITED", self.node.last_reason)
        self.assertEqual(self.policy.floor, 2)

    def test_unavailable_current_metadata_prevents_automatic_fallback(self):
        self.activate()
        self.verifier.trusted_host_clock = False
        self.node.report_health(False, 2)
        self.assertEqual(self.node.phase, Phase.FAILED)
        self.assertIn("TRUSTED_TIME_UNAVAILABLE", self.node.last_reason)

    def test_fallback_health_failure_isolates_without_infinite_retry(self):
        self.activate()
        self.node.report_health(False, 2)
        self.node.report_health(False, 3)
        self.assertEqual(self.node.phase, Phase.FAILED)
        self.assertEqual(self.node.last_reason, "RECOVERY_HEALTH_FAILED")

    def test_recovery_commit_rechecks_authorization(self):
        self.activate()
        self.node.report_health(False, 2)
        self.policy.revoked.add("old")
        self.node.report_health(True, 3)
        self.assertEqual(self.node.phase, Phase.FAILED)
        self.assertEqual(self.node.last_reason, "RELEASE_REVOKED")

    def test_interlock_violation_never_restarts_fallback_airborne(self):
        self.activate()
        candidate_session = self.node.session
        self.node.observe_operational(OperationalEvidence(False, True, 2))
        self.assertEqual(self.node.phase, Phase.FAILED)
        self.assertEqual(self.node.session, candidate_session)
        self.assertEqual(self.node.active.release.release_id, "new")
        self.assertIsNone(self.node.grant)

    def test_fresh_wrapper_does_not_refresh_old_inner_sample(self):
        self.airborne(10)
        self.node.observe_navigation(self.evidence(1))
        self.assertIsNone(self.node.request_role(10, self.rule))
        self.assertEqual(self.node.last_reason, "NAVIGATION_STALE")

    def test_producer_reset_immediately_withdraws_grant(self):
        self.airborne()
        self.node.request_role(1, self.rule)
        self.node.set_producer(ProducerContext("boot-2", "config-1", "frame-1"))
        self.assertIsNone(self.node.role_at(2))
        self.assertIsNone(self.node.navigation)

    def test_expiration_does_not_renew_from_queries(self):
        self.airborne()
        self.node.request_role(1, self.rule)
        self.assertEqual(self.node.role_at(2), self.rule.role)
        self.assertEqual(self.node.role_at(3), self.rule.role)
        self.assertIsNone(self.node.role_at(4))

    def test_authorization_change_withdraws_existing_role(self):
        self.airborne()
        self.node.request_role(1, self.rule)
        self.policy.revoked.add("old")
        self.assertIsNone(self.node.role_at(2))
        self.assertEqual(self.node.last_reason, "RELEASE_REVOKED")

    def test_navigation_invalid_context_and_values_fail_closed(self):
        for changes, reason in (
            ({"application_session": "old-session"}, "NAVIGATION_SESSION_MISMATCH"),
            ({"vehicle": "other-vehicle"}, "NAVIGATION_SESSION_MISMATCH"),
            ({"producer": ProducerContext("other", "config-1", "frame-1")}, "NAVIGATION_CONTEXT_MISMATCH"),
            ({"clock": "gnss-only"}, "NAVIGATION_TIME_UNKNOWN"),
            ({"sample_time": 100}, "NAVIGATION_STALE"),
            ({"sample_time": float("nan")}, "NAVIGATION_TIME_UNKNOWN"),
            ({"error_bound": float("nan")}, "NAVIGATION_ERROR_BOUND"),
            ({"error_bound": 9}, "NAVIGATION_ERROR_BOUND"),
            ({"valid": False}, "NAVIGATION_NOT_READY"),
            ({"monitor_ready": False}, "NAVIGATION_NOT_READY"),
        ):
            with self.subTest(changes=changes):
                self.airborne()
                self.node.observe_navigation(self.evidence(**changes))
                self.assertIsNone(self.node.request_role(1, self.rule))
                self.assertEqual(self.node.last_reason, reason)

    def test_grounded_vehicle_cannot_supply_airborne_search(self):
        self.ground()
        self.node.observe_navigation(self.evidence())
        self.assertIsNone(self.node.request_role(1, self.rule))
        self.assertEqual(self.node.last_reason, "AIRBORNE_ROLE_REQUIRES_FLIGHT")

    def test_rewound_permission_time_cannot_restore_role(self):
        self.airborne(5)
        self.node.request_role(5, self.rule)
        self.assertIsNone(self.node.role_at(4))
        self.assertEqual(self.node.last_reason, "INVALID_PERMISSION_TIME")

    def test_unsupported_or_grounded_search_role_is_not_defined(self):
        with self.assertRaises(ValueError):
            RoleRule(requires_airborne=False)
        with self.assertRaises(ValueError):
            RoleRule(role="invented-useful-relay")


if __name__ == "__main__":
    unittest.main()
