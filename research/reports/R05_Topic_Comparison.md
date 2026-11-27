# R05: Bounded topic comparison and proposed research decision

- Date: 2026-11-27
- Tasks: [#10](https://github.com/mathissdupont/swarm-rejoin/issues/10), preparation for [#11](https://github.com/mathissdupont/swarm-rejoin/issues/11)
- Preparation: assisted desk comparison for Samet Ünsal and team discussion; no joint meeting, completed source cross-review or advisor approval

## Shared comparison boundary

Retain GNSS/navigation evidence, authenticated software state and swarm service as the three areas. Use a trusted modeled coordinator/measurement boundary, the accepted companion application target and ground-only activation, identical security constraints in B3/P, and independent outcome truth. Alternatives that change the target or require a cooperative estimator need an explicit scope decision. No numerical novelty or feasibility score is justified by this reading.

| Candidate | Minimal model and possible contribution | Nearest evidence / material uncertainty | Comparator, measurable claim and refutation |
| --- | --- | --- | --- |
| T1 joint update/rejoining | Companion updates and navigation-dependent role appraisal during bounded outages; empirical policy/model study | Dong's retrieved reconnection integrity checks, RASUES update/state appraisal, existing navigation recovery. Full reconnection comparison is still access-limited | B3 with the same inputs/constraints versus P; useful service/unsafe grants. Refuted if gains require weaker constraints or vanish against B3 |
| T2 untrusted GNSS time | Separate position and clock faults; authenticated metadata, persisted state and bounded disconnection | [Uptane Deployment](../library/uptane-deployment/README.md) section 3.1 already describes clock risks; TUF reference-time integration is unresolved | Existing freshness strategies under identical time-source assumptions; stale acceptance/false refusal/service delay. Refuted if it is only a restatement of expiration or a nonce is incorrectly treated as latest-release knowledge |
| T3 signed navigation configuration | One configuration schema, bad-but-authorized settings, representative replay/maneuvers and staged promotion | [T3 assessment](R08_T3_Navigation_Configuration_Assessment.md); signatures and canary rollout are established. This changes the accepted update target if adopted | Immediate/fixed-canary/evidence-informed promotion with the same authorization; harmful promotion and service loss. Refuted by no gain, truth leakage or unrepresentative canaries |
| T4 cooperative localization during rolling updates | A specifically chosen cooperative estimator with relative-measurement dependencies and service downtime | [Yan seed](../library/yan2020/README.md) is access-limited; estimator/observability assumptions are not selected. Graph connectivity alone is insufficient | Fixed/topology-only/uncertainty-aware order; actual error and service. Refuted if gains vanish under the estimator's true information requirements. This remains a planning-level assessment, not a completed R04 method review |
| T5 evidence after recovery | Distinguish application versus producer restart; current output and continuity-aware role revalidation | [T5 assessment](R10_T5_Navigation_Recovery_Assessment.md); RASUES and navigation reintegration overlap restrict broad claims; provenance availability is central | Credible conservative reacquisition versus conditional revalidation; time to genuinely eligible service. Refuted by equivalent behavior, unavailable evidence or unsafe grants |
| T6 joint-fault characterization | Common traces, security checks, hidden truth and fair policies for a justified subset of combined faults | [T6 assessment](R11_T6_Joint_Fault_Benchmark_Assessment.md); existing sensor/formation test frameworks prevent a generic first-benchmark claim | Characterization/reproducibility rather than a guaranteed winning controller; weak if coverage is already equivalent, labels are circular or models do not support conclusions |

## Proposed decision, not an accepted replacement topic

Keep **T1** as the main direction and use **T5's recovery/evidence-continuity question** to bound its first study. Keep **T6** as an empirical fallback if a new policy is unjustified or gives no improvement. This preserves the accepted mission-application target and the team's three areas. Do not combine T2-T6 into mandatory implementation features.

Suggested question: **Under the same software authorization, ground-only activation and role-safety rules, does explicit navigation-evidence revalidation after companion-application recovery improve time to useful swarm service compared with a credible fixed joint policy?** The model must allow the estimator to continue when only the companion application restarts. The comparison is not merely against unsafe cached-state reuse.

Current evidence supports investigating this question; it does not establish originality. T2 remains an important threat/model boundary, T3 changes the update target if adopted, and T4 adds unresolved estimator assumptions. These are evidence/scope judgments, not a claim that one topic is easier or more novel by a numerical score.

## Concrete advisor/team handoff

The proposed baseline minimum is B3/P under shared security and role constraints, plus contextual weak baselines. Proposed responsibilities remain Ceren for navigation/model calibration, Samet for update/recovery/provenance and Halil for policies/mission evaluation. Confirm rather than silently assign final ownership.

Ask the advisor to decide whether an adapted-system evaluation with possible negative policy results and reusable traces is sufficient; confirm the final main question, physical-hardware expectation, first-semester output and official deadline. May 2027 remains provisional. Record this as an accepted decision only after the actual discussion.

R05's comparison/proposal is now available for review, but missing full reconnection access, T4 method review, other-author checks and advisor acceptance are not fabricated as complete. The [2026-11-16 closeout audit](Research_Closeout_Assessment_2026-11-16.md) remains a dated historical snapshot rather than being silently rewritten as a meeting record.
