# Contribution candidate and bounded decision gate

Prepared: **2026-11-27**. Status: proposed T1/T5 narrowing, not established novelty, advisor approval, a verified protocol or experimental findings. This supplies a new gate; the historical 7 November target was not a completed meeting.

## Recommended question

**Working title: Navigation Evidence Continuity Across Secure Updates and Swarm Re-admission.**

> After an authorized mission-application update or recovery, which navigation evidence remains usable for a specific swarm role, and can dependency-aware revalidation preserve useful service under the same security and role constraints as a competent static policy?

Keep the [accepted boundary](decisions/0003-companion-deployment-and-ground-activation.md): Linux companion mission application, ground-only activation/recovery with landed/disarmed evidence and an interlock. Flight-control firmware is excluded. Its estimator can continue while the consumer application restarts.

## What already exists

| Work / examined evidence | Existing mechanism limiting our claim | Remaining comparison, not an absence finding |
| --- | --- | --- |
| [Varadharajan et al., 2018](../research/literature/notes/varadharajan2018.md), update strategy, manuscript page 3 | Swarm code updates, rollback and membership management | Match script-update assumptions to companion recovery and navigation-role evidence |
| [RobOTAP, 2024](../research/literature/notes/robotap2024.md), III-IV, VI | Authenticated image transfer for robot swarms on constrained hardware | Our application/estimator continuity and role contract need separate comparison; its timings cannot calibrate our Linux target |
| [RASUES, 2026](../research/literature/notes/usman2026.md), 4-5, 7-8 | Updates linked to software-state appraisal, with stated recovery/security limitations | Match trust, measurement and recovery assumptions |
| [OpenSwarm D2.4](../research/literature/notes/openswarm-d24.md), executive summary | Firmware-state attestation for network admission | Selected reading only; full protocol comparison remains open |
| [Shagor, 2026](../research/literature/notes/shagor2026.md), abstract and limitations | Software-level admission and rollback/persistence checks | Firmware admission differs from measured navigation fitness; no hardware assurance follows |
| [Navigation reintegration](../research/literature/notes/aljaafreh2026.md), selected mode/recovery passages; [RFC 9334](../research/library/rfc9334/README.md) | Sensor reintegration and freshness appraisal have established foundations | Our task is a specific cross-component contract and its assessment, not inventing freshness or quarantine |

Dong access, NeRTA's full method review and citation chasing remain incomplete in [R01](../research/reports/R01_Closest_Work_Comparison.md). Neither an unsuccessful search nor a different deployment target establishes originality.

## Proposed artifact: a dependency-aware admission contract

Model three separate lifecycles: **release authorization/recovery**, **navigation production**, and **swarm-role permission**. A small dependency graph states which event invalidates which claim. Begin with explicit rules, not a weighted trust score or a new optimizer.

| Evidence group | Required meaning / feasibility question |
| --- | --- |
| Software | Current authorized release, security floor, application session, health, configuration/schema compatibility. A manifest signature does not establish running state |
| Navigation | Producer and boot/session context, configuration digest, frame/reset generation, original sample time/sequence, validity/uncertainty and any monitor history required by the chosen method |
| Time/provenance | Clock domain, reception context and justified age bound. Unknown cross-boot mapping means unknown freshness; a fresh outer challenge cannot refresh an old inner sample |
| Role permission | Role prerequisites, evidence context at issuance, bounded validity and invalidating events. Disconnection must not preserve authority indefinitely |

These are semantic requirements, not a completed wire schema. Unavailable fields mean unavailable continuity claims. Small reset counters and boot-relative timestamps alone are insufficient. Initially assume an honest modeled producer and protected collection boundary; hardware attestation and resistance to privileged compromise are not demonstrated.

### Decision procedure to specify and test

1. Apply identity, current release authorization, artifact/compatibility, health and operational gates separately. Mission demand cannot offset a hard failure.
2. Revoke the old application session's grants during activation/recovery. Invalidate navigation claims affected by producer, configuration, frame, time or continuity changes. Unknown continuity takes the conservative path.
3. Obtain current producer output. Retain compatible calibration/history only if the selected monitor needs it and its trusted continuity can be established. Cached position/confidence never becomes fresh through authorized fallback.
4. Appraise each role against current evidence; bind a permission to that context, expire it and reappraise when relevant changes arrive or evidence ages.
5. Compare eligible roles and defer/update/recovery choices within the same team constraints as B3. Airborne reconnects without replacement can be appraised; replacement waits for permitted ground activation.

Valid-looking current evidence may still be wrong. This contract targets context inconsistencies under stated assumptions; it does not guarantee spoofing detection or physical safety. Delayed event delivery, finite grant intervals and hidden faults remain visible to the independent evaluator.

## Contributions to attempt

| ID | Deliverable | Evidence needed |
| --- | --- | --- |
| C1 | Product-state model, dependency rules and counterexample set | Nearest-work comparison and bounded trace exploration identify cross-component errors excluded under explicit assumptions |
| C2 | Dependency-aware revalidation and admission policy | A justified difference from a competent comparator, held-out service benefit and unchanged hard gates |
| C3 | Reproducible joint-fault study and failure characterization | Shared observations, independent truth, paired runs, released traces/configuration and reported equivalence/failure regions |

Signatures, TUF, A/B storage, freshness, role permissions and dependency tracking are supporting ideas with prior art. No field or ordinary invalidation rule is claimed as an invention. C1/C3 may support an empirical undergraduate thesis if the advisor agrees; publication-level originality remains unestablished.

## Strong comparator and falsification

The main [B3 comparator](06-evaluation-plan.md) receives the same evidence and feasible roles/recovery options. It may reacquire fresh output and preserve an uninterrupted estimator. **Do not force a filter reset or arbitrary warm-up after an application-only restart.** If a competent static policy can use the same safe continuity checks, give it those checks and isolate any remaining scheduling/role difference. Unsafe cache reuse is diagnostic only.

Separate two questions:

- **Contract correctness:** Can specified event interleavings violate context/authorization invariants? Deliberately flawed variants explain failure classes. Future exhaustive checks would cover a bounded model, not every real system.
- **Service benefit:** Does P improve paired useful-service fraction or time to eligible service over equally constrained B3 on held-out cases? Retain denied/censored episodes; report unsafe physical admissions separately. Equal context checks do not imply equal true-position risk.

Refute C2 if B3 is equivalent, provenance cannot be obtained/validated, benefits require an unjustified warm-up or weakened comparator, or extra service comes from unsafe roles. Freeze practical margins and risk criteria before confirmatory testing; no numeric improvement threshold is justified yet.

## Six designed traces for the gate

Specifications only, not executed experiments. Map them to the existing [scenario catalog](../experiments/scenarios.json) when implementing; no new implemented scenarios are asserted.

| Trace | Independent condition | Required decision / question |
| --- | --- | --- |
| A: application-only recovery | Authorized fallback, continuing producer/configuration/frame and fresh output | Rebind session and reappraise roles; both P and competent B3 may use the continuing estimator |
| B: fresh wrapper, stale sample | Recovered application responds freshly with an old inner navigation sample | Reject for age-dependent roles; authentication cannot refresh the sample |
| C: producer/configuration/frame change | Release passes health but dependencies change or continuity is unknown | Invalidate affected claims; follow justified monitor/producer initialization conditions |
| D: revocation during recovery | Formerly valid fallback is prohibited before commit/grant | Reject under current authorization; service demand cannot authorize it |
| E: hidden navigation fault | Context and monitor look valid but true role prerequisites fail | Count unsafe physical admission if granted; the policy cannot grade itself |
| F: team role contention | Returning member and other members compete for scarce useful capability | Show whether fixed/joint decisions differ without inventing a useful or feasible grounded/airborne role |

## Gate: 30 November-2 December 2026

Accelerated at Samet's request on 2026-11-27. Reuse the authored notes and A-F trace specifications; cross-check the minimum shared assumptions concurrently over three working days. This is a working scope decision, not a completed literature review, advisor acceptance or a meeting. Log unanswered advisor questions and material source gaps explicitly. Do not wait for every optional topic or inaccessible PDF.

| Owner | Required artifact |
| --- | --- |
| Samet Ünsal | Dependency/invalidation table and A-D traces; OTA/RobOTAP/RASUES section comparison; check which provenance fields a real adapter supplies |
| Ceren Tolunay | One feasible GNSS/IMU monitor/model, justified age/error inputs, continuity versus history-reset conditions, annotated clean/faulted traces and calibration gaps |
| Halil Abacı | One mission and useful-role table, independent eligibility labels and B3/P hand decisions on A-F, including a difference or honest equivalence |
| All | Cross-review; ask whether C1/C3 with a negative C2 satisfies thesis requirements; confirm official deadline and hardware expectation |

**Go:** observable contract, justified GNSS role, feasible comparison and accepted contribution type. Start the selected implementation with assumptions labeled.

**Narrow:** no new-policy advantage, but a useful reproducible fault characterization and advisor acceptance of C1/C3. Use the [T6 assessment](../research/reports/R11_T6_Joint_Fault_Benchmark_Assessment.md).

**Pivot:** neither contribution is defensible/feasible. Reassess the already investigated [T3 configuration-rollout candidate](../research/reports/R08_T3_Navigation_Configuration_Assessment.md) against navigation/canary literature before adoption; its novelty is not promised either.

Extend the gate only for a newly found validity problem. Maintain related work during development. Follow the dated [roadmap](07-roadmap-and-team.md).
