# Originality assessment: navigation eligibility after authorized recovery

Date: **2026-11-27**. Assisted author-stage analysis for Samet Ünsal, Ceren Tolunay and Halil Abacı. Scope: research/design reasoning, not a measured result, implemented planner, completed model check or independent team approval.

## Decision from this pass

**Do not use stale-evidence rejection or selective reacquisition as the main novelty claim.** A competent comparator can perform them. Retain them as shared requirements.

The more concrete candidate is **pre-activation planning using the navigation roles achievable after an authorized software recovery**. A release may remain authorized and recover successfully while its fresh navigation evidence is insufficient, too late or incompatible with a role. Investigate when that distinction changes which member to update or whether to defer.

Working title: **Navigation-Qualified Recovery for Secure Updates in UAV Swarms**. This is a research candidate within T1/T5, not a proven first work or a claimed new robust-optimization technique. The [D01 draft](../../docs/14-recovery-and-role-contract.md) makes its inputs, invalidations, branch semantics, action rule and strong baselines explicit.

## Evidence and nearest-work challenge

| Source / actual reading depth | Existing contribution relevant here | Consequence and uncertainty |
| --- | --- | --- |
| [Swarm OTA, 2018](../literature/notes/varadharajan2018.md), selected update strategy | Swarm updates, rollback and membership handling | Those mechanisms are not our contribution; navigation-readiness comparison remains incomplete |
| [RobOTAP](../literature/notes/robotap2024.md), selected III-IV/VI | Authenticated transfer and constrained-device update workflow | Use established update primitives; future recovery extensions cannot be treated as demonstrated |
| [RASUES](../literature/notes/usman2026.md), comparative author reading | Update/state appraisal and recovery, with explicit assurance limits | Update-plus-attestation is not new; software appraisal and role eligibility remain distinct |
| [NeRTA](../literature/notes/yaacoub2023.md), selected target/model/limits | Scheduling low-level robot updates around processor idle time | Generic disruption-aware scheduling exists; full adjacent-method checking remains open |
| [Notomista et al., arXiv v1](../literature/notes/notomista2021.md), abstract only | Feature/capability-aware resilient allocation under environmental/component changes | Capability-aware resilience is not our invention. Full mathematical comparison is unknown; it could subsume a proposed policy |
| [Swarmada pinned source](../literature/notes/swarmada-rollouts.md), selected API/controller sections | Robot rollout limits, failure pauses, capability-sensitive update context and model-recovery handling | Existing software also overlaps integration claims. We did not execute or audit its full controller/security/navigation behavior |

The source table does not establish that the remaining intersection is absent from the literature. Patent descriptions, commercial deployment guidance, unrelated preprints and search silence were not used as evidence of novelty or measured capability. See the [search log](../literature/search-log.md).

## Two questions that must be separated

1. Can the system recover to an authorized, intact, compatible and healthy application?
2. After that recovery, when can it produce fresh enough navigation evidence for a particular role, under the current mission demand?

Question 1 can be true while question 2 is false. That is a logical distinction, not itself a new theorem. The candidate contribution is a precise navigation/software transition model and a fair study of the decisions this distinction changes.

## Worked decision example: a designed fixture, not an experiment

This example deliberately specifies projected capabilities. It does not establish that a chosen estimator produces them. Ceren must validate or reject that premise, including better state retention or buffer replay that could eliminate the difference.

Six vehicles share one mission. Four incumbents can supply other capabilities but cannot supply a designated precision-search role `P` in the next mission phase. Two returning vehicles, U and V, are on the ground with otherwise authorized, compatible current applications. Both have a feasible plan to supply P by a common dispatch deadline D if not replaced. The next phase requires two P vehicles; the demand is not incorrectly imposed during the preceding ground-maintenance window.

There is time and capacity to update one vehicle before dispatch. Both candidate packages are verified and authorized under the same mandatory checks. Both retain an authorized, compatible recovery image. Each action's modeled completion includes health, evidence appraisal and any required launch time/energy; no vehicle supplies airborne search while grounded. The hypothetical mission value of updating U is greater than updating V under success. That ordering is a design input, not a measured utility.

The declared failure class is one candidate activation/health failure with the recovery manager and retained image still usable. Navigation qualification can differ after recovery: for example, application-owned monitor history may need revalidation under degraded GNSS. A flight-controller estimator need not reset. The precise reason for U/V asymmetry must be supported by a model; a companion restart alone cannot justify it.

| Update action | Successful transition: P-capable vehicles by D | Authorized healthy fallback branch: P-capable vehicles by D | Requirement met in both modeled branches? |
| --- | --- | --- | --- |
| Update U | U and V: 2 | U lacks justified fresh role evidence by D; V qualifies: 1 | No |
| Update V | U and V: 2 | U qualifies unchanged; V requalifies after recovery: 2 | Yes |
| Defer both | U and V: 2 | No update-induced failure branch in this bounded fixture | Yes, with no update progress |

A nominal role-aware rule selects U under the stated success-value ordering. If its activation fails, it correctly withholds U's role and records a capability shortfall; it does not commit an unsafe admission. A branch-aware rule can select V, preserving the modeled demand while making update progress. A count limit of one simultaneous updater does not distinguish these consequences.

**This example establishes a difference against a specified nominal rule only.** A generic contingency-aware role planner supplied with the same readiness branches also selects V. Therefore it does not establish a new algorithm, superiority over MRTA literature, or an empirical improvement. That stronger comparator is mandatory in the final study.

### Conditions that erase or reverse the example

- Both vehicles requalify promptly after fallback: the branch distinction disappears; prefer the success-value ordering if other criteria agree.
- Neither vehicle can requalify by D after failure: a branch-conservative rule defers both or reports conflict with an urgent update requirement.
- The failure envelope permits loss of the recovery manager/image, arbitrary delay or correlated GNSS failure on both vehicles: the stated continuity result does not follow.
- U can safely retain/restore monitor history or consume a current independent producer stream: do not invent a history reset; recalculate U's readiness.
- There is time to update both, demand is lower or another incumbent can supply P: the original action difference may vanish.
- Predictions depend on inaccessible future GNSS truth: the example is not a valid deployable policy comparison.

These are required negative cases, not inconvenient exceptions to omit.

## Minimal identifiability argument

Suppose a decision procedure sees only an authorized recovered release, a new application session and a wrapped navigation report. It sees no trustworthy original sample age or producer/configuration continuity.

Consider two permitted model histories that produce exactly these observations: one has current qualifying producer evidence; the other reuses an old nonqualifying observation after conditions changed. A procedure using only the shared observations must choose the same action in both histories. It cannot guarantee immediate role admission in the first and rejection in the second. It must request distinguishing evidence, use another justified observation, or deny/defer the affected role.

This is a simple indistinguishability deduction under the specified observation model, not a new general impossibility theorem or a claim that every real adapter lacks those fields. It explains why the contract needs original-sample provenance and why a freshness wrapper alone cannot supply it.

## Defensible contribution statement to investigate

> We model how authorized mission-application recovery changes the navigation evidence available for swarm roles, characterize cases where image-level recovery does not restore timely mission capability, and evaluate update/re-admission decisions against nominal and generic contingency-aware baselines under identical security constraints.

Add a new-method claim only if a specific algorithmic distinction survives that stronger comparison and the nearest-work analysis. Otherwise C1/C3 remains a possible model/empirical contribution, which requires advisor acceptance and evidence of useful distinct coverage. Samet's originality requirement is not satisfied merely by giving generic robust planning a new name.

## What this pass actually completes

- Delivers a draft shared evidence/recovery/role contract, dependency table, bounded branch-aware decision rule, designed differing trace and negative/equivalence cases.
- Removes standalone stale-cache handling as the proposed source of originality.
- Adds resilient allocation and current robot-rollout software to the nearest-work comparison, with reading and licensing limits.
- Identifies the concrete scientific blocker: defensible recovery-to-navigation readiness behavior, followed by comparison against generic contingency-aware allocation. No implementation or experiment is needed to conceal that uncertainty.

Next artifacts are a validated sensor/monitor recovery trace (Ceren), an installer-consistent recovery trace (Samet), and the generic contingency-aware assignment comparison (Halil). Those responsibilities are proposed. No existing issue is closed or peer review inferred by this analysis.
