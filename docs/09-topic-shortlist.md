# Alternative thesis topics

Assessment date: **2026-10-24**. These are candidate questions within the team's **GNSS + secure update + UAV swarm** direction. None is presented as a proven literature gap. The workload estimates below are planning judgments, not novelty scores.

The current rejoining topic remains available. Alternatives let the team choose a more precise interaction before committing to an implementation.

## Shortlist

| ID | Working title | Central interaction | Expected scope |
| --- | --- | --- | --- |
| **T1** | **GNSS-Aware Secure Updates and Rejoining in UAV Swarms** | Navigation evidence and software state jointly determine update/recovery actions and permitted roles after reconnection | Broadest integration; needs careful scope control |
| **T2** | **Secure Update Freshness under GNSS Time Faults in UAV Swarms** | Untrusted navigation time can affect update expiration decisions during swarm disconnections | Narrower mechanism; requires explicit clock and connectivity assumptions |
| **T3** | **Secure Deployment of Navigation Configuration Updates in UAV Swarms** | Signed navigation parameter/configuration changes must remain compatible and behave acceptably before fleet-wide promotion | Concrete update target; potentially manageable without autopilot flashing |
| **T4** | **Rolling Updates for Cooperative Localization in UAV Swarms** | Updating localization services changes which neighbors can supply usable measurements and which software versions can cooperate | Strong shared problem for the three workstreams; more modeling work |
| **T5** | **Rollback-Aware Navigation Recovery and Swarm Re-Admission** | A recovered software image must not reuse stale navigation confidence or regain roles before revalidation | Focused failure-state study; overlap with T1 and recovery literature must be checked |
| **T6** | **A Reproducible Benchmark for Joint GNSS and Secure-Update Faults in UAV Swarms** | Joint navigation, update, and reconnection faults are evaluated with independent truth and common baselines | Empirical contribution; advisor must accept benchmark/characterization scope |

T1 corresponds to candidate A, T2 to candidate B, and T6 to candidate C in the [contribution assessment](01-topic-decision.md). T3–T5 are additional candidates, not approved scope changes.

## T1 — GNSS-aware update and rejoining decisions

**Question:** Does explicitly using navigation evidence in a joint software-remediation and role-admission policy improve useful swarm service over a static joint policy with the same mandatory checks?

**Smallest study:** Six agents, two role types, two or three signed releases, one selected GNSS/IMU monitor, disconnects, and interrupted updates. Compare static admission, static joint control, and the proposed policy.

**Division of work:** Ceren models and validates navigation evidence; Samet implements update authorization and permitted recovery; Halil designs the joint policy and independent evaluation.

**Decision risk:** Adding inputs to a score may be ordinary integration. A credible contribution needs a specific temporal decision and a matched baseline. Use the existing [brief](02-research-brief.md) as a proposal to challenge.

## T2 — GNSS time and update freshness

**Question:** How do bounded clock uncertainty, authenticated external time, and monotonic release state affect stale metadata acceptance and legitimate service recovery when a swarm member's GNSS-derived time is faulty?

**Why investigate:** [Uptane Deployment Best Practices 2.1.0, section 3.1](https://uptane.org/docs/2.1.0/deployment/best-practices) discusses update problems caused by clocks running ahead or behind and explicitly warns against using unsecured civilian GPS as a secure time source. This is an established concern, not our discovery.

**Smallest study:** Model a returning swarm node, independently adjustable position and time faults, bounded offline duration, and a trusted time-source availability model. Compare existing freshness strategies and measure false update refusals, stale acceptance, and return-to-service time. Add a new policy only if existing strategies expose a precise, relevant limitation.

**Division of work:** Ceren specifies GNSS-time faults and clock uncertainty; Samet implements metadata/freshness validation; Halil models the swarm availability consequences and comparison.

**Decision risk:** A counter or nonce cannot prove that a suppressed release does not exist. Unlimited isolation prevents a blanket promise of both latest-release knowledge and unrestricted availability. Position confidence is not evidence of clock integrity.

## T3 — Signed navigation configuration rollout

**Question:** Can staged deployment of signed navigation configurations detect harmful estimator behavior and limit its propagation through a UAV swarm more effectively than immediate rollout, under identical authorization requirements?

**Concrete update target:** A versioned set of estimator parameters, fault-monitor thresholds, or a companion localization-service configuration. This is a secure configuration update study unless executable firmware is actually changed. [RFC 9019](https://datatracker.ietf.org/doc/html/rfc9019) includes configuration updates within its architectural scope; signing configuration is an established mechanism.

**Smallest study:** Design both legitimate beneficial changes and authorized but operationally poor configurations. Compare all-at-once rollout, fixed canary rollout, and a proposed evidence-informed promotion/abort rule. Measure true position error, monitor misses/false alarms, role eligibility, service continuity, and rollback outcomes on held-out maneuvers.

**Division of work:** Ceren defines navigation quality and representative trajectories; Samet implements signed packages, version compatibility, and allowed rollback; Halil implements staged promotion and mission-level analysis.

**Decision risk:** A valid signature does not imply correct parameters, and a canary that does not encounter representative conditions can give false confidence. Do not call ordinary canary deployment novel. The possible contribution must lie in a justified navigation-specific criterion or comparative evidence.

## T4 — Cooperative localization during rolling updates

**Question:** Can update ordering preserve the measurement relationships needed for a chosen cooperative localization method while keeping release compatibility and mission-role constraints intact?

**Why investigate:** Cooperative localization already has resource-aware measurement scheduling research, for example [Yan et al. (2020)](https://doi.org/10.1109/LRA.2020.2969916). This motivates examining localization dependencies; it does not demonstrate a gap in update scheduling.

**Smallest study:** A 2D cooperative-localization model with known relative-measurement availability, GNSS degradation, a specified compatibility matrix, and companion-service downtime during updates. Compare fixed order, topology-only order, and an uncertainty-aware order. Evaluate actual localization error, mission service, and update completion. Use the same update checks for every secure policy.

**Division of work:** Ceren models localization and uncertainty; Samet models authenticated releases and mixed-version interfaces; Halil studies update ordering and team capacity.

**Decision risk:** Graph connectivity alone does not establish localization observability or bounded error. Define the chosen estimator's actual requirements. Do not assume that neighbor agreement proves trustworthy GNSS when faults may be correlated.

## T5 — Recovery and stale navigation confidence

**Question:** After software rollback or restart, which navigation-state reset and evidence-revalidation policies prevent premature swarm re-admission without causing excessive legitimate downtime?

**Smallest study:** Model estimator warm-up, stored calibration/configuration, old confidence reports, challenge/session changes, software fallback, and role permission expiry. Compare immediate reuse, conservative full reinitialization, and a justified selective revalidation policy. Measure false re-admission, position error after recovery, and time to a genuinely eligible role.

**Division of work:** Ceren models estimator recovery and confidence calibration; Samet models authorized rollback and evidence/session binding; Halil models re-admission and mission effects.

**Decision risk:** [RASUES](https://doi.org/10.1007/s10207-026-01233-1) already relates updates to before/after attested states. We have not established whether an existing system covers this exact navigation recovery case. Full-text comparison is required before claiming a new protocol.

## T6 — Joint fault benchmark

**Question:** Which combinations of navigation faults and software update/recovery failures cause different safe-service outcomes across credible swarm rejoining policies?

**Smallest study:** Implement a documented subset of the [scenario catalog](../experiments/scenarios.json), common truth/evidence traces, and three credible reference policies. Publish reproducible configurations, outcome definitions, failure traces, and sensitivity analysis. Keep simulated security assumptions explicit.

**Division of work:** Ceren owns navigation scenarios and truth; Samet owns update/recovery scenarios and verification; Halil owns common baselines, metrics, and reproducibility. All authors cross-review labels.

**Decision risk:** A collection of handpicked examples is insufficient. Search existing benchmarks, justify scenario coverage, and demonstrate that the artifacts answer a useful comparative question. A negative result is acceptable if the characterization is sound and the advisor accepts the contribution type.

## A separate GNSS authentication caution

Galileo OSNMA could be a later source of navigation-data authentication evidence, but it is not required by this shortlist. The [European GNSS Service Centre FAQ](https://www.gsc-europa.eu/galileo/faq) distinguishes navigation-data authentication from authentication of the complete position/velocity/time solution. Do not treat an OSNMA success flag as guaranteed correct position or universally trustworthy update time. Adding a real receiver implementation would require a separate feasibility assessment.

## How to choose

Start by reviewing **T2, T3, and T4 alongside T1**: they expose different, concrete links between the three fields. This is a suggested reading priority, not a claim that they are more original.

For each candidate, complete one page with the nearest work, a verified limitation or unknown, a minimal model, a fair comparator, a measurable claim, and a plausible refutation. Select one main question after the literature/topic gate. Do not implement all six as one thesis.
