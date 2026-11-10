# Research issues and backlog

The live research issues were created on **2026-10-24**. Leads below are proposed research owners. GitHub contains the current completion state and formal assignments; pending collaborator invitations can delay assignment without changing the proposed lead.

## Live research issues

| ID | GitHub issue | Proposed lead | Completion artifact |
| --- | --- | --- | --- |
| R01 | [#1 — Closest reconnection, attestation, and update studies](https://github.com/mathissdupont/swarm-rejoin/issues/1) | All | Three section-cited, cross-reviewed notes |
| R02 | [#2 — Secure-update requirements and clock assumptions](https://github.com/mathissdupont/swarm-rejoin/issues/2) | Samet | [Source note and two designed traces](../research/reports/R02_Secure_Update_Foundations.md); [six MVP decisions accepted](decisions/0002-update-mvp-requirements.md); verification-library evaluation and source cross-review pending |
| R03 | [#3 — GNSS/IMU integrity evidence](https://github.com/mathissdupont/swarm-rejoin/issues/3) | Ceren | [Consolidated draft report](../research/reports/R03_GNSS_IMU_Integrity_Research_Report.md), administratively closed; [2026-11-01 review](../research/reviews/2026-11-01-r03-review.md) records checks and remaining acceptance work |
| R04 | [#4 — Swarm, localization, and update literature](https://github.com/mathissdupont/swarm-rejoin/issues/4) | Halil | Search log, reading notes, and comparator table |
| R07 | [#5 — T2: update freshness under GNSS time faults](https://github.com/mathissdupont/swarm-rejoin/issues/5) | Ceren + Samet | One candidate assessment and refutation criterion |
| R08 | [#6 — T3: signed navigation configuration rollout](https://github.com/mathissdupont/swarm-rejoin/issues/6) | Samet + Ceren | One candidate assessment and minimal study |
| R09 | [#7 — T4: updates and cooperative localization](https://github.com/mathissdupont/swarm-rejoin/issues/7) | Halil + Ceren | One candidate assessment and checked update sequence |
| R10 | [#8 — T5: navigation recovery after rollback](https://github.com/mathissdupont/swarm-rejoin/issues/8) | Samet + Ceren + Halil | Stale-evidence example and candidate assessment |
| R11 | [#9 — T6: joint fault benchmark](https://github.com/mathissdupont/swarm-rejoin/issues/9) | All | Coverage/overlap table and reusable artifact plan |
| R05 | [#10 — Compare T1–T6](https://github.com/mathissdupont/swarm-rejoin/issues/10) | All | One-page comparison and proposed decision |
| R06 | [#11 — Confirm the main question with the advisor](https://github.com/mathissdupont/swarm-rejoin/issues/11) | All | Accepted decision record and revised scope |
| D01 | [#12 — Shared evidence and role contracts](https://github.com/mathissdupont/swarm-rejoin/issues/12) | All | Versioned contract and three checked traces |
| D03 | [#13 — Baselines, independent truth, and metrics](https://github.com/mathissdupont/swarm-rejoin/issues/13) | Halil + team | Evaluation specification and worked metric examples |

Start with [milestone 1: research scope and topic selection](https://github.com/mathissdupont/swarm-rejoin/milestone/1). Its 7 November date is a provisional review target. [Milestone 2](https://github.com/mathissdupont/swarm-rejoin/milestone/2) covers shared models after the topic decision; it has no fixed due date.

## Later implementation scope

The table below keeps the larger scope visible. It is not a claim that every implementation task already has a GitHub issue. Do not mark work complete without an inspectable artifact.

| ID | Priority | Lead | Task | Acceptance evidence |
| --- | --- | --- | --- | --- |
| R01 | Now | All | Review the three nearest studies together | Section-level notes for Dong, RASUES, NeRTA; overlapping claims corrected |
| R02 | Now | Samet | Read TUF/Uptane and relevant SUIT requirements | Threat-to-mechanism table; clear distinction between reused mechanism and candidate contribution |
| R03 | Now | Ceren | Define navigation evidence and its limits | A monitor design, uncertainty/time-source assumptions, and benign/faulted trace examples |
| R04 | Now | Halil | Find team-level update/recovery and benchmark literature | Logged queries, candidate screening, and nearest comparator analysis |
| R05 | Now | All | Compare the six candidate topics T1–T6 | Evidence-backed overlap assessment, feasible minimum study, and refutation criterion; no automatic novelty score |
| R06 | Now | All | Decide topic with advisor | Decision record with accepted contribution type, chosen question, scope, and reasons |
| D01 | Next | All | Freeze mission/role and evidence contracts | Versioned definitions consumed by all three workstreams |
| D02 | Next | Samet | Design security floor and permitted fallback transitions | Failure traces including no-authorized-recovery and persistent-state crash points |
| D03 | Next | Halil | Specify B3 and independent evaluator | Fixed priority rules; hidden truth cannot leak into policy inputs |
| I01 | Later | Samet | Implement actual artifact/manifest verification | Invalid signature, digest, target, freshness, and epoch cases fail correctly |
| I02 | Later | Ceren | Implement sensor/fault model and estimator validation | Calibration plots and false-alarm/missed-detection results with known truth |
| I03 | Later | Halil | Implement baselines and candidate controller | Identical hard constraints and resources in B3/P; bounded runtime and infeasible-case traces |
| I04 | Later | All | Integrate staged update/recovery simulation | End-to-end interruption, activation failure, recovery failure, and reconnect traces |
| E01 | Later | All | Pilot and freeze confirmatory analysis | Reproducible pilot report, final margins, held-out configurations, precision justification |
| E02 | Later | All | Execute main experiments and ablations | Revision/seed/configuration records, raw traces, failures, intervals, negative cases |
| S01 | Optional | All | Build two/three-vehicle PX4 case study | Pinned environment and measured reconnect/update-service traces; fidelity limits stated |
| W01 | Ongoing | All | Write thesis and maintain bibliography | Claims linked to sources or run IDs; peer-reviewed draft sections |
| O01 | Setup | Samet | Publish the public repository and invite the team | Public repository created; write invitations sent to the verified accounts; acceptance checked separately; license remains a team decision |

Use [research issue templates](../.github/ISSUE_TEMPLATE/research_task.md) and [decision records](../research/templates/decision-record.md) as work begins. Live task state and assignments belong in [GitHub issues](https://github.com/mathissdupont/swarm-rejoin/issues). The table above is a scope map, not an automatically synchronized issue-status report.
