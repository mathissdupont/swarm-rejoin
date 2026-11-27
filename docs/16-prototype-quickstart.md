# Exploratory verified-rejoining fixture

Status: first executable integration fixture, **2026-11-27**. It connects real TUF package verification to a modeled application lifecycle and navigation-bound role permissions. It is not the full six-agent mission simulator, a GNSS/IMU estimator, an onboard installer or an originality result.

## Install and run on Windows

From the repository root, use Python 3.12 or newer and a virtual environment. This does not need Linux, PX4, Docker or a physical UAV.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -c requirements-runtime.txt -e .
.venv/Scripts/python.exe -m swarm_rejoin.demo
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py"
```

If the environment already exists, use its interpreter and install the project rather than replacing the environment. Runtime constraints pin the direct libraries and transitive runtime packages; `pyproject.toml` pins the build backend. No signing key is required in your checkout.

Linux/WSL equivalents after creating a separate Linux environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -c requirements-runtime.txt -e .
.venv/bin/python -m swarm_rejoin.demo
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

Do not copy/reuse a Windows virtual environment in Linux. See the [implementation handoff](15-implementation-handoff.md) for the later Linux process and PX4/Gazebo stages. No WSL distribution was installed, started or configured to implement this fixture.

## The nine-event scenario

The [packaged configuration](../src/swarm_rejoin/fixtures/rejoin.json) declares six vehicles and a deterministic sequence. Five incumbents receive fresh authored reports. U1 follows these events:

1. Start on a verified authorized release with an authored ground/navigation observation.
2. Attempt a deliberately truncated download. TUF rejects it; the active artifact remains unchanged.
3. Download the complete candidate through the same real verification workflow.
4. Enter a modeled landed/disarmed activation; change the application session, withhold health/roles and maintain the modeled arming interlock.
5. Receive a fixture health-failure observation. Reverify the actual retained image under current metadata, project authorization and security floor before modeled recovery.
6. Receive a fixture fallback-health success observation. The old application session's navigation evidence still fails appraisal.
7. Obtain a current authored navigation report from the continuing producer. A companion restart did not reset that producer.
8. Receive a modeled departure observation after the interlock clears; grant precision-search only while all current modeled prerequisites pass.
9. Expire the permission. Querying a grant never extends its old expiry.

This scenario uses authored evidence and ground/airborne states. It does not calculate a trajectory, measure physical position, run a GNSS filter or execute the opaque application payload. The seed is recorded but reserved: no pseudorandom sensor draws occur. Cryptographic keys are freshly generated with the library's secure randomness, independently of that seed.

An `observation` test role is distinct from airborne `precision-search` and is not counted as search coverage. The prototype does not yet implement a full mission role/release matrix, team allocation, B3/P policies or demand optimization.

## Keep an inspectable run

Choose a new directory; the CLI refuses to overwrite an existing one:

```powershell
.venv/Scripts/python.exe -m swarm_rejoin.demo --output experiments/results/smoke-001
```

Run output is ignored by Git by default. Inspect:

| File | Contents |
| --- | --- |
| `run.json` | Configuration/hash, seed usage, source revision/dirty state and source-code hash, invocation, Python/platform/library versions, start time, assumptions and fixture outcome counts |
| `events.jsonl` | Event times, release/digest, session/producer context, lifecycle, reasons and role decisions |
| `fixture-truth.jsonl` | Independent authored eligibility labels and whether each grant contradicts them; these are not measured position/error truth |
| `public-repository.json` | Public bootstrap root, signed metadata and harmless opaque payload bytes for the run; no private keys |
| `artifacts.sha256.json` | SHA-256 of the four preceding run artifacts |

Replaying the same fixture with newly generated repository keys produces the same event/label behavior, not identical signed metadata. TUF metadata uses actual host UTC with a one-day fixture expiration and a seven-day root expiration. Exact archived metadata eventually expires; regenerate a fresh fixture for later behavior checks instead of disabling expiration. No claim of latest-release knowledge during arbitrary suppression is made.

## Implemented boundaries and remaining gaps

| Implemented | Important limit |
| --- | --- |
| Python-TUF 7.0.1 client workflow with provisioned bootstrap, signed root/timestamp/snapshot/targets and complete payload verification | Fixed in-memory transport and trusted host UTC; no public repository service, offline-current-authorization proof or GNSS-time adapter |
| Authenticated custom-field parsing for the exact v1 fixture profile; component/platform/protocol/data-schema checks | Not the full [manifest draft](11-update-manifest-draft.md); unknown fields fail this narrow profile, not a general TUF conformance rule |
| Revocation and monotonic floor checks at modeled stage/activation/recovery/health/grant boundaries | Trusted in-memory project state; not a protected crash-safe journal, key rotation system or secure-boot implementation |
| Ground/health/recovery state transitions and grant withdrawal | Trusted fixture health/operational observations; no physical arming interlock, process supervisor, recovery timeout or electrical crash recovery |
| Original sample age, clock/session/producer/configuration/frame checks and bounded grant expiry | Trusted fixture producer and one shared monotonic time domain; no authenticated reconnect protocol, remote attestation, GNSS detector or calibrated confidence |
| A new sample or producer context change invalidates the old grant; current authorization is rechecked when a role is queried | Synchronous in-process decisions; not a distributed revocation protocol under packet delay/loss |

Recovery deliberately requires a successful fresh TUF lookup in this first fixture. If current metadata or trusted host time is unavailable, modeled recovery fails closed. That is a conservative prototype limitation, not a demonstrated available offline recovery design. Already-active service is appraised using modeled local authorization; this does not establish current remote revocation knowledge while disconnected.

Identity and measurement-agent honesty remain assumptions. A valid signature proves authorized bytes under the configured policy, not that an uncompromised UAV is running them. A valid-looking fixture observation can still be mislabeled against independent physical truth in a later sensor model; no zero-risk claim follows from the authored scenario.

## Tests and next contributions

Behavioral tests exercise the actual signed chain, metadata expiry/replay, tampering, partial transfer, compatibility/floor/revocation, changed staged bytes, ground/interlock constraints, fallback failure, original-sample freshness, producer/session changes, grant expiry and CLI provenance/output behavior. The archive tests continue separately. CI runs the prototype on Windows/Linux with Python 3.12 and 3.14; a configured CI matrix is not evidence of results until those jobs pass.

- **Samet:** replace lifecycle observations with a real Linux service/health probe and develop crash-safe installer/data/security-state transactions. Do not claim those from this state-machine fixture.
- **Ceren:** supply the observation/truth generator and justified recovery-history/readiness behavior. Replace authored error bounds; retain cases where the proposed U/V distinction disappears.
- **Halil:** build one mission, the nominal and generic contingency-aware B3 variants, demand labels and paired-run evaluation. The current role gate is shared infrastructure, not P or a comparative policy result.

The [2 December contract/model gate and accelerated roadmap](07-roadmap-and-team.md) still apply. This exploratory work does not invent a completed gate, advisor decision, calibrated sensor model or novel algorithm.
