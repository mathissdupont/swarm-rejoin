# R11 / T6: Joint-fault characterization candidate

- Date: 2026-11-27
- Task: [issue #9](https://github.com/mathissdupont/swarm-rejoin/issues/9)
- Preparation: assisted research candidate, not a completed benchmark or joint team review

## Existing coverage and why a new coverage claim is not yet justified

| Existing source/artifact | Checked coverage | Unresolved comparison |
| --- | --- | --- |
| [MIXED-SENSE preprint](../literature/notes/pant2024.md), sections III-VI | Physical/virtual sensor-fault emulation; a single-real-UAV demonstration; swarm experiments described as future work | Update authorization, permitted fallback and our role contract are not established by this reading |
| [Rodriguez et al. selected methods](../literature/notes/rodriguez2025.md) | CoFI formation-state analysis involving GNSS/link/energy faults | Exact artifact availability and update-security coverage require full-text confirmation |
| [RASUES review](../literature/notes/usman2026.md) | Attestation/update processing and recovery with explicit trust assumptions | Its hardware-backed evidence model is different from our proposed simulation |
| [TUF specification](../library/tuf-spec/README.md) and [reference client assessment](R02_Verification_Library_Assessment.md) | Metadata/artifact verification requirements and an existing implementation to exercise later | Passing cryptographic checks would not validate our motion, navigation or mission model |

These references rule out calling ordinary fault injection, sensor simulation or update verification new. They do not establish that a particular combined benchmark is missing. The search log records a targeted pass, not an exhaustive benchmark survey.

## Minimal reusable artifact plan

Use the existing [design-only scenario catalog](../../experiments/scenarios.json) to select a small initial set:

| Catalog scenario | Why retain it |
| --- | --- |
| S01 clean reconnect | Reference behavior and measurement overhead |
| S06 stale/replayed evidence | Session/sample-context errors after a restart |
| S10 interrupted download | Separation of active software and incomplete staging |
| S11/S12 permitted/no-usable fallback | Both successful recovery and explicit infeasibility |
| S14 joint navigation/link/update failure | Interaction that a single isolated fault cannot characterize |
| S15 infeasible capacity | Check that service pressure does not relax hard constraints |

Specify a versioned scenario/configuration, exogenous event trace, hidden world truth, observations, decisions/transitions and per-run metric record. Retain revision/dirty state, environment, exact command, independent seed streams, artifact/config hashes and failed/censored outcomes. Share inputs and hard constraints across B3/P; policies cannot access ground truth. Keep all four release/security/evidence/mission properties separate.

The first model may simulate movement, GNSS/IMU faults, outage timing, application downtime, health and trust assumptions. If real TUF verification is later integrated, report those actual signature/metadata/hash checks separately from simulated attestation, disk atomicity and physical flight safety. A Python object named `trusted` is an assumption, not hardware security. A later PX4 case study does not retroactively calibrate every simulated duration.

Reuse value would come from exact combined fault/provenance semantics, fair policies, independently labeled role outcomes and rerunnable negative cases. It would not come merely from collecting fifteen named scenarios. Confirm that another researcher can reproduce a trace and its outcome before claiming a usable benchmark artifact.

## Refutation and advisor question

The candidate is weak if existing artifacts already cover the same decision/state contract, combined faults add no useful characterization, outcome labels are circular, or the motion/sensor assumptions are too weak to support the intended inference. A new controller is not required if a rigorous comparative characterization is accepted.

**Question prepared for the advisor, not already asked/answered:** Would a reproducible study of joint navigation/update/recovery faults with credible baselines and negative results satisfy the thesis contribution requirement if no adaptive-policy improvement is found?

This delivers the authored coverage/overlap assessment and minimal artifact plan. The advisor conversation and the wider artifact/primary-source follow-up are not claimed complete; issue #9 should not be closed as an accepted thesis contribution on this document alone.
