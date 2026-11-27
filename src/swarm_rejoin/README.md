# Exploratory implementation boundary map

The first [executable fixture](../../docs/16-prototype-quickstart.md) implements the modules below. It is reusable infrastructure authorized by Samet, not the final model/contribution decision or the complete mission simulator.

| Module | Implemented responsibility | Limit |
| --- | --- | --- |
| `verification.py` | Actual Python-TUF bootstrap/metadata/payload workflow and narrow project release appraisal | No installer, hardware protection or latest-release knowledge guarantee |
| `fixture_repository.py` | Real signed in-memory repository, ephemeral in-memory signing keys, deterministic transfer-fault transport | Test/demo publisher, not deployment infrastructure or an identity protocol |
| `lifecycle.py` | Ground/health/update/fallback transitions, current authorization and session/producer/age-bound role grants | In-process operational/health/navigation observations and protected-state assumptions; no real process or flight commands |
| `demo.py` and `fixtures/rejoin.json` | Six-vehicle, nine-event authored fixture with saved provenance, public metadata and independent authored labels | No vehicle dynamics, GNSS/IMU estimation, B3/P comparison or scientific performance result |

Future modules remain `navigation` (selected sensor/truth model), `policies` (fair nominal/contingency baselines and P if justified), `simulation` (mission/event/fault models), `evaluation` (independent physical labels/metrics) and `adapters` (Linux process/PX4 integration). They are not implemented by merely naming them here.

The [handoff](../../docs/15-implementation-handoff.md) and [D01 draft](../../docs/14-recovery-and-role-contract.md) define pending team/model work. A process/session change is not a flight-controller reset; a verified artifact is not proof of uncompromised running software or correct navigation.
