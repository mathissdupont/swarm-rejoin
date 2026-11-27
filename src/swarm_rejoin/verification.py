"""Real TUF verification plus bounded application-specific release appraisal.

The cache is local and single-writer. Its protection/durability and the host UTC
clock are explicit assumptions. This module does not install or execute bytes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import re
from typing import Any

from tuf.api.exceptions import DownloadError, RepositoryError
from tuf.ngclient import Updater
from tuf.ngclient.config import UpdaterConfig
from tuf.ngclient.fetcher import FetcherInterface


class Rejected(Exception):
    """An expected fail-closed outcome, with a stable machine-readable reason."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def identifier(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9_.-]{1,80}", value):
        raise Rejected("INVALID_RELEASE_FIELDS")
    return value


@dataclass(frozen=True)
class Release:
    release_id: str
    component: str
    platform: str
    protocol: str
    security_epoch: int
    data_schema: str

    @classmethod
    def parse(cls, custom: Any) -> Release:
        if not isinstance(custom, dict) or type(custom.get("schema_version")) is not int:
            raise Rejected("INVALID_RELEASE_FIELDS")
        if custom["schema_version"] != 1:
            raise Rejected("UNSUPPORTED_RELEASE_SCHEMA")
        required = {
            "schema_version", "release_id", "component", "platform", "protocol",
            "security_epoch", "data_schema", "activation_profile", "health_profile",
        }
        if set(custom) != required:
            raise Rejected("INVALID_RELEASE_FIELDS")
        epoch = custom["security_epoch"]
        if type(epoch) is not int or not 0 <= epoch <= 2**63 - 1:
            raise Rejected("INVALID_RELEASE_FIELDS")
        if custom["activation_profile"] != "modeled-ground-v1":
            raise Rejected("UNSUPPORTED_ACTIVATION_PROFILE")
        if custom["health_profile"] != "fixture-health-v1":
            raise Rejected("UNSUPPORTED_HEALTH_PROFILE")
        return cls(
            *(identifier(custom[key]) for key in (
                "release_id", "component", "platform", "protocol"
            )),
            epoch, identifier(custom["data_schema"]),
        )


@dataclass(frozen=True)
class VerifiedArtifact:
    target: str
    release: Release
    payload: bytes
    sha256: str
    length: int

    def check_bytes(self) -> None:
        if len(self.payload) != self.length or hashlib.sha256(self.payload).hexdigest() != self.sha256:
            raise Rejected("ARTIFACT_CHANGED")


@dataclass
class SecurityPolicy:
    """Trusted local model state, not a hardware-protected persistent store."""

    platform: str = "companion-model-v1"
    component: str = "mission-app"
    protocol: str = "swarm-v1"
    data_schema: str = "data-v1"
    max_payload_bytes: int = 1024 * 1024
    _floor: int = 1
    revoked: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if type(self._floor) is not int or not 0 <= self._floor <= 2**63 - 1:
            raise ValueError("Invalid security floor")
        if type(self.max_payload_bytes) is not int or not 1 <= self.max_payload_bytes <= 16 * 1024 * 1024:
            raise ValueError("Invalid payload limit")
        for value in (self.platform, self.component, self.protocol, self.data_schema):
            identifier(value)

    @property
    def floor(self) -> int:
        return self._floor

    def raise_floor(self, value: int) -> None:
        if type(value) is not int or not self._floor <= value <= 2**63 - 1:
            raise Rejected("SECURITY_FLOOR_REGRESSION")
        self._floor = value

    def appraise(self, artifact: VerifiedArtifact) -> None:
        artifact.check_bytes()
        release = artifact.release
        if release.release_id in self.revoked:
            raise Rejected("RELEASE_REVOKED")
        if release.security_epoch < self.floor:
            raise Rejected("SECURITY_EPOCH_PROHIBITED")
        if release.component != self.component or release.platform != self.platform:
            raise Rejected("WRONG_TARGET")
        if release.protocol != self.protocol:
            raise Rejected("INCOMPATIBLE_PROTOCOL")
        if release.data_schema != self.data_schema:
            raise Rejected("INCOMPATIBLE_DATA_SCHEMA")
        if artifact.length > self.max_payload_bytes:
            raise Rejected("PAYLOAD_TOO_LARGE")


class ReleaseVerifier:
    def __init__(
        self, bootstrap: bytes, cache: Path, fetcher: FetcherInterface,
        policy: SecurityPolicy, *, trusted_host_clock: bool,
    ):
        self.bootstrap = bootstrap
        self.cache = cache
        self.fetcher = fetcher
        self.policy = policy
        self.trusted_host_clock = trusted_host_clock
        (cache / "metadata").mkdir(parents=True, exist_ok=True)
        (cache / "targets").mkdir(parents=True, exist_ok=True)

    def verify(self, target: str) -> VerifiedArtifact:
        # Only a fixed component's opaque single-file package is supported.
        # There is no publisher-selected extraction path or shell command.
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}\.bin", target):
            raise Rejected("INVALID_TARGET_PATH")
        if not self.trusted_host_clock:
            raise Rejected("TRUSTED_TIME_UNAVAILABLE")
        try:
            updater = Updater(
                str(self.cache / "metadata"), "https://repository.invalid/metadata/",
                str(self.cache / "targets"), "https://repository.invalid/targets/",
                fetcher=self.fetcher,
                config=UpdaterConfig(
                    max_root_rotations=8, max_delegations=8,
                    root_max_length=65536, timestamp_max_length=16384,
                    snapshot_max_length=65536, targets_max_length=65536,
                ),
                bootstrap=self.bootstrap,
            )
            updater.refresh()
            info = updater.get_targetinfo(target)
            if info is None:
                raise Rejected("TARGET_NOT_AUTHORIZED")
            if info.length > self.policy.max_payload_bytes:
                raise Rejected("PAYLOAD_TOO_LARGE")
            if "sha256" not in info.hashes:
                raise Rejected("REQUIRED_HASH_MISSING")
            release = Release.parse(info.custom)
            # Verify complete bytes using the real TUF client before returning
            # an artifact. Project semantics are enforced separately below.
            path = updater.download_target(info)
            payload = Path(path).read_bytes()
            artifact = VerifiedArtifact(target, release, payload, info.hashes["sha256"], info.length)
            self.policy.appraise(artifact)
            return artifact
        except (RepositoryError, DownloadError) as exc:
            raise Rejected("TUF_VERIFICATION_FAILED") from exc
