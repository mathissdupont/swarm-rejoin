# Behavioral and archive tests

The first executable fixture has meaningful verification, lifecycle, role-evidence and CLI tests. Install the project as described in the [quickstart](../docs/16-prototype-quickstart.md), then run:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py"
```

| Test module | What is exercised |
| --- | --- |
| `test_verification.py` | Real TUF signatures/hash/length, trusted bootstrap, metadata expiry/replay, narrow authenticated project fields, target/compatibility/floor/revocation, input/payload limits and changed bytes |
| `test_lifecycle.py` | Interrupted transfer preserves active state, stage/ground separation, activation/interlock/health, permitted/prohibited fallback, current authorization, old session/context/sample rejection, permission expiry and role operational requirements |
| `test_demo.py` | Deterministic fixture transitions, separate authored labels, configuration rejection, output provenance/hash files and no overwrite of existing results |
| `test_source_library.py` | Archive records, rights/capture status, file hashes and local source integrity; not UAV security |

`python tools/check_repo.py` remains dependency-free for documentation/references/scenario-catalog consistency. It is not a substitute for the runtime behavioral tests. The unimplemented scenario catalog stays design-only.

The CI prototype matrix runs Windows/Linux and Python 3.12/3.14; inspect actual job outcomes before claiming platform validation. The tests do not validate real GNSS/IMU measurements, identity/attestation, a persistent crash-safe installer, physical arming enforcement, onboard timing or research-policy superiority.

Future implementation must add tests for real process/persistent-state crash points, selected sensor-model false alarms/misses, mission demand and independent truth, paired baselines, failed/censored runs and PX4 interfaces as those components are implemented. Do not replace these with assertions that merely mirror an implementation or label a policy safe from its own score.
