# Research brief

Working title: **GNSS-Aware Secure Updates and Rejoining in UAV Swarms**.

This brief describes candidate A in the [topic decision](01-topic-decision.md). Every method below is proposed, not implemented or validated.

## Problem

A six-UAV search mission loses one member's connection. While it is disconnected, the team adopts a newer coordination-service release. The returning vehicle authenticates successfully but carries an older release, uncertain navigation evidence, or an unfinished update. Immediate full admission could be inappropriate; indefinite exclusion could also reduce mission service unnecessarily.

The research problem is to understand how **navigation integrity evidence and secure software state together affect swarm rejoining**, including choices among restricted service, update, defer, permitted recovery, full admission, and isolation. The decision is temporal: navigation evidence ages, an update may fail, and both can change which roles a node may perform later.

The intended scope keeps GNSS, secure updates, and swarm behavior together. A specific link between GNSS confidence and update timing must be justified by the modeled operation; it is not assumed to hold for every UAV architecture.

## Proposed contribution hierarchy

| Item | Candidate contribution | What would support it |
| --- | --- | --- |
| C1 | A joint navigation-evidence/software-update/swarm-rejoining model | Explicit interactions, invariants, finite counterexamples, and traceable assumptions |
| C2 | A GNSS-aware update/recovery and re-admission policy for this model | Measurable use of navigation evidence, differences from static policies, and held-out comparisons |
| C3 | A reproducible comparative study of joint navigation/update faults | Public configurations, credible baselines, independent labels, uncertainty reporting, and rerunnable traces |

The project may conclude with C1/C3 and a negative result for C2. Agreement that this is a sufficient thesis outcome belongs in the topic gate. Existing signatures, secure-update metadata, and GNSS monitors are supporting mechanisms.

## Research questions

- **RQ1 — Joint decisions:** Does using navigation integrity evidence in update/rejoining decisions increase useful swarm mission service over static policies under the same hard constraints?
- **RQ2 — Recovery:** How do interrupted transfers, failed activation, incompatible releases, and permitted fallback choices affect recovery success and time to useful service?
- **RQ3 — Uncertainty:** When does navigation uncertainty change admissible role choices, and how sensitive are outcomes to estimator calibration and evidence age?
- **RQ4 — Cost and limits:** What computation, communication, and additional assumptions are required? Under which conditions does the adaptive controller offer no benefit?

## Falsifiable hypotheses

- **H1:** The proposed GNSS-aware policy improves the paired mean useful-service fraction relative to B3 on held-out joint navigation/link/update-fault scenarios. Reject the benefit claim if the confidence interval includes no practically meaningful improvement, using a margin fixed before final runs.
- **H2:** Permitted recovery reduces time without useful service after failed activation compared with a policy that always restarts updating, without admitting a prohibited image. Refute this claim if recovery is no better or violates the security floor.
- **H3:** Role-specific navigation requirements preserve more useful service than a single all-or-nothing threshold at a predeclared role-safety criterion. Refute it if additional service comes from unsafe role allocation or disappears under calibration shifts.

Final hypotheses, margins, metrics, and scenario families must be frozen before confirmatory experiments. These statements are not experimental findings.

## Minimum scope

- Five to eight simulated agents; one explicit search/coverage mission abstraction.
- One trusted coordinator and preprovisioned update-authority keys.
- One updateable companion application/service; keep flight control stable.
- Two or three release configurations with an explicit role/protocol compatibility table.
- A/B-style staged activation and a permitted fallback model, initially simulated.
- GNSS/IMU consistency evidence with noise, drift, stale data, and failures.
- A transparent rule policy first, then a bounded lookahead or small enumerative controller if justified.
- A small PX4 SITL demonstration with two or three vehicles only after the Python study is credible.

## Scope limits

Do not require new cryptography, blockchain, reinforcement learning, a new estimator, a new autopilot, or a hardware root of trust to start. Reusing a GNSS/IMU monitor still requires validating its behavior in the chosen scenarios. Do not claim tolerance of a Byzantine coordinator or a fully compromised measurement agent. Do not hot-flash flight-critical firmware during flight for the MVP.

## Worked decision example

Suppose release 1 is still authorized for relay service but cannot perform release-2 cooperative search. A returning node with fresh evidence may be eligible for relay service while another node takes the search role. If a later attempt to activate release 2 fails, fallback to release 1 is permitted only while its security epoch and recovery authorization remain valid. A newly revoked release must remain excluded even if it would improve coverage.

This is a designed example. The final study must also include cases with no compatible fallback, no safe restricted role, insufficient remaining battery, untrusted time, and failed recovery. There must be a legitimate way for the controller to say that service cannot be preserved.
