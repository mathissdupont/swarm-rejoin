"""Deterministic six-vehicle plumbing fixture with actual TUF verification.

No GNSS/IMU estimator, trajectory dynamics, policy optimizer, process restart or
physical authentication/attestation is implemented by this demonstration.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata, resources
import json
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory

from .fixture_repository import SignedFixtureRepository, release_fields
from .lifecycle import (
    ModeledVehicle, NavigationEvidence, OperationalEvidence, ProducerContext, RoleRule,
)
from .verification import Rejected, ReleaseVerifier, SecurityPolicy, identifier


ACTIONS = (
    "initial_evidence", "interrupted_stage", "complete_stage", "activate",
    "candidate_health_fails", "fallback_health_passes", "fresh_navigation",
    "modeled_departure_and_role", "permission_expiry",
)


def load_config(path: Path | None = None) -> dict:
    raw = path.read_bytes() if path else resources.files("swarm_rejoin").joinpath("fixtures/rejoin.json").read_bytes()
    if len(raw) > 65536:
        raise ValueError("Fixture configuration too large")
    config = json.loads(raw)
    if not isinstance(config, dict) or type(config.get("schema_version")) is not int:
        raise ValueError("Fixture configuration must have an integer schema version")
    if config["schema_version"] != 1 or config.get("kind") != "authored_evidence_fixture":
        raise ValueError("Only the authored evidence fixture schema is supported")
    if set(config) != {"schema_version", "kind", "seed", "vehicles", "subject", "events"}:
        raise ValueError("Unknown or missing fixture fields")
    vehicles = config.get("vehicles")
    if not isinstance(vehicles, list) or not 5 <= len(vehicles) <= 8:
        raise ValueError("Provide five to eight unique vehicle identifiers")
    for name in vehicles:
        identifier(name)
    if len(set(vehicles)) != len(vehicles) or config.get("subject") not in vehicles:
        raise ValueError("Vehicle IDs must be unique; subject must exist")
    if type(config.get("seed")) is not int or config["seed"] < 0:
        raise ValueError("Seed must be a nonnegative integer")
    events = config.get("events")
    if not isinstance(events, list) or any(not isinstance(e, dict) for e in events):
        raise ValueError("Events must be objects")
    if [e.get("action") for e in events] != list(ACTIONS):
        raise ValueError("This smoke fixture requires the documented nine-event sequence")
    last = -1
    for event in events:
        if set(event) != {"action", "time"}:
            raise ValueError("Unknown or missing event fields")
        t = event.get("time")
        if type(t) is not int or t < 0 or t <= last:
            raise ValueError("Event times must be strictly increasing nonnegative integers")
        last = t
    return config


def label_role(role: str | None, eligible_in_fixture_truth: bool) -> dict:
    """Independent authored labels, never supplied to the role appraiser."""
    return {"role_granted": role is not None,
            "truth_eligible": eligible_in_fixture_truth,
            "unsafe_grant": role is not None and not eligible_in_fixture_truth}


def run_fixture(config: dict, cache_root: Path) -> tuple[list[dict], list[dict], dict]:
    repository = SignedFixtureRepository()
    repository.add("release-1.bin", b"Opaque fixture mission application release 1\n", release_fields("release-1"))
    repository.add("release-2.bin", b"Opaque fixture mission application release 2\n", release_fields("release-2", 2))
    repository.publish()
    nodes = {}
    producer = ProducerContext("producer-boot-1", "monitor-config-1", "local-frame-1")
    for name in config["vehicles"]:
        verifier = ReleaseVerifier(repository.bootstrap, cache_root / name, repository.fetcher,
                                   SecurityPolicy(), trusted_host_clock=True)
        node = ModeledVehicle(name, verifier, verifier.verify("release-1.bin"))
        node.set_producer(producer)
        nodes[name] = node
    subject = nodes[config["subject"]]
    rule = RoleRule()
    events, truth = [], []

    def evidence(node: ModeledVehicle, now: int) -> NavigationEvidence:
        # A declared fixture observation, not a computed navigation estimate.
        return NavigationEvidence(node.name, node.session, producer, now, 0.5)

    for event in config["events"]:
        now, action = event["time"], event["action"]
        expected_rejection = None
        # Incumbents have explicit continuously refreshed fixture reports.
        for name, node in nodes.items():
            if node is subject:
                continue
            node.observe_operational(OperationalEvidence(False, True, now))
            node.observe_navigation(evidence(node, now))
            node.request_role(now, rule)
        if action == "initial_evidence":
            subject.observe_operational(OperationalEvidence(True, False, now))
            subject.observe_navigation(evidence(subject, now))
        elif action == "interrupted_stage":
            repository.fetcher.truncate_targets = True
            try:
                subject.stage("release-2.bin")
            except Rejected as exc:
                expected_rejection = exc.reason
            finally:
                repository.fetcher.truncate_targets = False
            if expected_rejection is None:
                raise AssertionError("Incomplete download unexpectedly accepted")
        elif action == "complete_stage":
            subject.stage("release-2.bin")
        elif action == "activate":
            subject.observe_operational(OperationalEvidence(True, False, now))
            subject.begin_activation(now)
        elif action == "candidate_health_fails":
            subject.report_health(False, now)
        elif action == "fallback_health_passes":
            subject.report_health(True, now)
            # The original evidence remains bound to the pre-update session.
            # An observation-only rule lets this test isolate the session check.
            subject.request_role(now, RoleRule(role="observation", requires_airborne=False))
        elif action == "fresh_navigation":
            subject.observe_navigation(evidence(subject, now))
        elif action == "modeled_departure_and_role":
            if not subject.arming_permitted():
                raise AssertionError("Modeled departure attempted while interlocked")
            subject.observe_operational(OperationalEvidence(False, True, now))
            subject.request_role(now, rule)
        elif action == "permission_expiry":
            subject.role_at(now)
        roles = {name: node.role_at(now) for name, node in nodes.items()}
        events.append({
            "time": now, "event": action, "subject": subject.name,
            "phase": subject.phase.value, "active_release": subject.active.release.release_id,
            "active_digest": subject.active.sha256, "application_session": subject.session,
            "producer_boot": subject.producer.boot if subject.producer else None,
            "healthy": subject.healthy, "modeled_interlock": subject.interlock,
            "reason": subject.last_reason, "expected_rejection": expected_rejection,
            "roles": roles,
        })
        # These independent labels describe the authored scenario; no physical
        # true position or detector accuracy is inferred from them.
        for name, node in nodes.items():
            eligible = name != subject.name or action == "modeled_departure_and_role"
            truth.append({"time": now, "vehicle": name, **label_role(roles[name], eligible)})
    return events, truth, repository.export_public()


def environment(config: dict) -> dict:
    source = Path(__file__).parent
    digest = hashlib.sha256()
    for path in sorted(source.rglob("*.py")):
        digest.update(path.relative_to(source).as_posix().encode())
        digest.update(path.read_bytes())
    try:
        revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
                                           text=True, timeout=5).strip()
        dirty = bool(subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"],
                                            stderr=subprocess.DEVNULL, timeout=5).strip())
    except (OSError, subprocess.SubprocessError):
        revision, dirty = None, None
    encoded = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    return {
        "kind": "integration_smoke_with_authored_evidence", "configuration": config,
        "config_sha256": hashlib.sha256(encoded).hexdigest(), "seed": config["seed"],
        "seed_usage": "reserved; the authored event sequence uses no pseudorandom draws",
        "revision": revision, "worktree_dirty": dirty, "source_sha256": digest.hexdigest(),
        "python": platform.python_version(), "platform": platform.platform(),
        "dependencies": {p: metadata.version(p) for p in (
            "swarm-rejoin", "tuf", "securesystemslib", "cryptography", "urllib3", "cffi", "pycparser"
        )},
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "tuf_time_assumption": "trusted host UTC, independent of fixture navigation time",
        "crypto_keys": "fresh Ed25519 private keys in memory only; not derived from fixture seed",
        "limits": ["no GNSS estimator or vehicle dynamics", "no comparative policy experiment",
                   "modeled operational interlock, health and recovery", "no real identity or attestation protocol"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path, help="New output directory; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        run = environment(config)
        run["invocation"] = ["python", "-m", "swarm_rejoin.demo", *(argv if argv is not None else sys.argv[1:])]
        if args.output and args.output.exists():
            raise FileExistsError("Output directory already exists; select a new run ID")
        # Private signing material is only in memory. Client caches use an OS
        # temporary directory, never a key directory under the checkout.
        with TemporaryDirectory(prefix="swarm-rejoin-smoke-") as temporary:
            events, truth, public_repository = run_fixture(config, Path(temporary))
        run["fixture_outcomes"] = {
            "events": len(events), "vehicles": len(config["vehicles"]),
            "unsafe_grants_against_authored_labels": sum(x["unsafe_grant"] for x in truth),
            "final_release": events[-1]["active_release"],
            "final_subject_role": events[-1]["roles"][config["subject"]],
        }
        if args.output:
            args.output.mkdir(parents=True, exist_ok=False)
            for filename, value in (("run.json", run), ("public-repository.json", public_repository)):
                (args.output / filename).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
            for filename, values in (("events.jsonl", events), ("fixture-truth.jsonl", truth)):
                (args.output / filename).write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in values),
                                                   encoding="utf-8", newline="\n")
            checksums = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in sorted(args.output.iterdir())}
            (args.output / "artifacts.sha256.json").write_text(json.dumps(checksums, indent=2) + "\n",
                                                             encoding="utf-8", newline="\n")
        print(json.dumps({"status": "fixture_completed", **run["fixture_outcomes"],
                          "scientific_result": False, "output": str(args.output) if args.output else None}))
        return 0
    except (Rejected, ValueError, OSError) as exc:
        parser.exit(1, f"Smoke run failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
