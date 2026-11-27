"""Modeled lifecycle and role gates; no processes or flight commands are run.

Identity, producer honesty, operational reports and health observations are
trusted fixture inputs. They are not implemented authentication/attestation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math

from .verification import Rejected, ReleaseVerifier, VerifiedArtifact


class Phase(StrEnum):
    IDLE = "IDLE"
    DOWNLOADING = "DOWNLOADING"
    STAGED = "STAGED"
    HEALTH_CHECK = "HEALTH_CHECK"
    RECOVERING = "RECOVERING"
    FAILED = "FAILED"


def finite_nonnegative(value: float) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


@dataclass(frozen=True)
class ProducerContext:
    boot: str
    configuration: str
    frame: str


@dataclass(frozen=True)
class NavigationEvidence:
    vehicle: str
    application_session: str
    producer: ProducerContext
    sample_time: float
    error_bound: float
    valid: bool = True
    monitor_ready: bool = True
    clock: str = "fixture-monotonic"


@dataclass(frozen=True)
class OperationalEvidence:
    landed: bool
    armed: bool
    observed_at: float


@dataclass(frozen=True)
class RoleRule:
    role: str = "precision-search"
    max_age: float = 4.0
    max_error: float = 1.0
    permission_ttl: float = 3.0
    requires_airborne: bool = True

    def __post_init__(self) -> None:
        if type(self.requires_airborne) is not bool or not isinstance(self.role, str) or not self.role:
            raise ValueError("Invalid role rule")
        if self.role not in ("precision-search", "observation"):
            raise ValueError("Unsupported fixture role")
        if self.role == "precision-search" and not self.requires_airborne:
            raise ValueError("Precision search cannot be supplied while grounded")
        if any(not finite_nonnegative(x) or x == 0 for x in (
            self.max_age, self.max_error, self.permission_ttl
        )):
            raise ValueError("Role limits must be finite positive numbers")


@dataclass(frozen=True)
class RoleGrant:
    role: str
    application_session: str
    artifact_digest: str
    producer: ProducerContext
    issued_at: float
    expires_at: float


class ModeledVehicle:
    def __init__(self, name: str, verifier: ReleaseVerifier, active: VerifiedArtifact):
        verifier.policy.appraise(active)
        self.name = name
        self.verifier = verifier
        self.active = active
        self.staged: VerifiedArtifact | None = None
        self.fallback: VerifiedArtifact | None = None
        self.phase = Phase.IDLE
        self.healthy = True  # Initial model provisioning, not measured health.
        self.interlock = False
        self.session_number = 1
        self.producer: ProducerContext | None = None
        self.navigation: NavigationEvidence | None = None
        self.operational: OperationalEvidence | None = None
        self.operational_max_age = 5.0
        self.grant: RoleGrant | None = None
        self.last_reason = "PROVISIONED_FIXTURE"
        self.role_rule: RoleRule | None = None

    @property
    def session(self) -> str:
        return f"{self.name}-session-{self.session_number}"

    def set_producer(self, context: ProducerContext | None) -> None:
        if context is not None and any(not isinstance(x, str) or not x or len(x) > 80 for x in (
            context.boot, context.configuration, context.frame
        )):
            raise ValueError("Producer context requires bounded nonempty identifiers")
        if self.producer != context:
            self.grant = None
            self.navigation = None
        self.producer = context

    def observe_navigation(self, evidence: NavigationEvidence) -> None:
        self.navigation = evidence
        self.grant = None  # Every new report must be appraised, including degradation.

    def observe_operational(self, evidence: OperationalEvidence) -> None:
        self.operational = evidence
        self.grant = None
        # A broken modeled interlock is detected, never silently repaired by
        # restarting the application in flight.
        if self.interlock and (not evidence.landed or evidence.armed):
            self._isolate("GROUND_INTERLOCK_VIOLATED")

    def _operational_gate(self, now: float, *, ground: bool) -> None:
        state = self.operational
        if not finite_nonnegative(now) or state is None or not finite_nonnegative(state.observed_at):
            raise Rejected("OPERATIONAL_EVIDENCE_UNKNOWN")
        if type(state.landed) is not bool or type(state.armed) is not bool:
            raise Rejected("OPERATIONAL_EVIDENCE_UNKNOWN")
        if not 0 <= now - state.observed_at < self.operational_max_age:
            raise Rejected("OPERATIONAL_EVIDENCE_STALE")
        if ground and (not state.landed or state.armed):
            raise Rejected("GROUND_REQUIRED")

    def _navigation_gate(self, now: float, rule: RoleRule) -> None:
        nav = self.navigation
        if self.producer is None or nav is None:
            raise Rejected("NAVIGATION_UNKNOWN")
        if nav.vehicle != self.name or nav.application_session != self.session:
            raise Rejected("NAVIGATION_SESSION_MISMATCH")
        if nav.producer != self.producer:
            raise Rejected("NAVIGATION_CONTEXT_MISMATCH")
        if nav.clock != "fixture-monotonic" or not finite_nonnegative(nav.sample_time):
            raise Rejected("NAVIGATION_TIME_UNKNOWN")
        if not 0 <= now - nav.sample_time < rule.max_age:
            raise Rejected("NAVIGATION_STALE")
        if not finite_nonnegative(nav.error_bound) or nav.error_bound > rule.max_error:
            raise Rejected("NAVIGATION_ERROR_BOUND")
        if nav.valid is not True or nav.monitor_ready is not True:
            raise Rejected("NAVIGATION_NOT_READY")

    def stage(self, target: str) -> None:
        if self.phase not in (Phase.IDLE, Phase.STAGED):
            raise Rejected("TRANSITION_BUSY")
        self.phase = Phase.DOWNLOADING
        self.staged = None
        try:
            self.staged = self.verifier.verify(target)
        except Rejected as exc:
            self.phase = Phase.IDLE
            self.last_reason = exc.reason
            raise
        except Exception:
            # An I/O/programming failure must not strand a downloading state or
            # leave a half-candidate. Propagate unexpected failures to the caller.
            self.phase = Phase.IDLE
            self.last_reason = "STAGING_ABORTED"
            raise
        self.phase = Phase.STAGED
        self.last_reason = "CANDIDATE_VERIFIED"

    def _revalidate(self, artifact: VerifiedArtifact) -> VerifiedArtifact:
        artifact.check_bytes()
        fresh = self.verifier.verify(artifact.target)
        if fresh.sha256 != artifact.sha256 or fresh.release != artifact.release:
            raise Rejected("STAGED_ARTIFACT_CHANGED")
        return fresh

    def begin_activation(self, now: float) -> None:
        if self.phase != Phase.STAGED or self.staged is None:
            raise Rejected("NO_STAGED_CANDIDATE")
        self._operational_gate(now, ground=True)
        candidate = self._revalidate(self.staged)
        self.fallback = self.active  # Preserve the actual current image, not an invented older slot.
        self.active = candidate
        self.staged = None
        self.grant = None
        self.healthy = False
        self.interlock = True
        self.session_number += 1
        self.phase = Phase.HEALTH_CHECK
        self.last_reason = "AWAITING_MODELED_HEALTH"

    def _isolate(self, reason: str) -> None:
        self.healthy = False
        self.grant = None
        self.interlock = True
        self.phase = Phase.FAILED
        self.last_reason = reason

    def report_health(self, healthy: bool, now: float) -> None:
        if self.phase not in (Phase.HEALTH_CHECK, Phase.RECOVERING):
            raise Rejected("NO_HEALTH_TRANSITION")
        if type(healthy) is not bool:
            raise Rejected("INVALID_HEALTH_OBSERVATION")
        try:
            self._operational_gate(now, ground=True)
            if not self.interlock:
                raise Rejected("GROUND_INTERLOCK_VIOLATED")
        except Rejected as exc:
            self._isolate(exc.reason)
            return
        if healthy:
            try:
                self.active = self._revalidate(self.active)
            except Rejected as exc:
                self._isolate(exc.reason)
                return
            self.healthy = True
            self.phase = Phase.IDLE
            self.interlock = False
            self.grant = None
            self.last_reason = "HEALTHY_REAPPRAISAL_REQUIRED"
            return
        if self.phase == Phase.RECOVERING or self.fallback is None:
            self._isolate("RECOVERY_HEALTH_FAILED")
            return
        try:
            fallback = self._revalidate(self.fallback)
        except Rejected as exc:
            self._isolate("NO_AUTHORIZED_RECOVERY:" + exc.reason)
            return
        self.active = fallback
        self.session_number += 1
        self.phase = Phase.RECOVERING
        self.last_reason = "RECOVERY_AWAITING_MODELED_HEALTH"

    def arming_permitted(self) -> bool:
        # A model decision, not a physical flight-controller interlock.
        try:
            self.verifier.policy.appraise(self.active)
        except Rejected:
            return False
        return not self.interlock and self.healthy and self.phase in (Phase.IDLE, Phase.STAGED)

    def request_role(self, now: float, rule: RoleRule) -> RoleGrant | None:
        self.grant = None
        try:
            self.verifier.policy.appraise(self.active)
            if not self.healthy or self.phase not in (Phase.IDLE, Phase.STAGED) or self.interlock:
                raise Rejected("APPLICATION_UNAVAILABLE")
            self._operational_gate(now, ground=False)
            if rule.requires_airborne and (self.operational.landed or not self.operational.armed):
                raise Rejected("AIRBORNE_ROLE_REQUIRES_FLIGHT")
            self._navigation_gate(now, rule)
        except Rejected as exc:
            self.last_reason = exc.reason
            return None
        self.role_rule = rule
        self.grant = RoleGrant(
            rule.role, self.session, self.active.sha256, self.producer,
            now,
            min(now + rule.permission_ttl,
                self.navigation.sample_time + rule.max_age,
                self.operational.observed_at + self.operational_max_age),
        )
        self.last_reason = "ROLE_GRANTED_FROM_FIXTURE_EVIDENCE"
        return self.grant

    def role_at(self, now: float) -> str | None:
        old = self.grant
        if old is None:
            return None
        if not finite_nonnegative(now) or now < old.issued_at:
            self.grant = None
            self.last_reason = "INVALID_PERMISSION_TIME"
            return None
        if now >= old.expires_at:
            self.grant = None
            self.last_reason = "PERMISSION_EXPIRED"
            return None
        if old.application_session != self.session or old.artifact_digest != self.active.sha256:
            self.grant = None
            return None
        # Reappraise changing authorization/navigation/operational constraints,
        # but do not extend an existing grant's expiry through this query.
        current = self.request_role(now, self.role_rule)
        if current is None:
            return None
        self.grant = old
        return old.role
