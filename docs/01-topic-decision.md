# Research direction and contribution assessment

Assessment date: **2026-10-24**. Status: **provisional; no novelty claim accepted**.

## Current assessment

The team's intended direction connects **GNSS systems, secure software updates, and UAV swarms**. Safe rejoining is the initial use case. The broad idea is a valid research starting point, but its original contribution has not been established. The current evidence is not sufficient to conclude that the topic should be abandoned.

All three areas are core scope requirements. Narrowing the project to generic software update scheduling would not capture the intended scope. First determine which concrete interaction between navigation evidence, software state, and swarm operation is worth investigating.

The provided [Dong et al. reconnection paper](https://doi.org/10.1016/j.bcra.2026.100439) already describes identity checks, program integrity checks, and behavioral test tasks during reconnection. Its retrieved reconnection sections make the overlap material. This does not establish that the initial idea has no possible contribution; it establishes that identity-only comparisons would be insufficient.

Other nearby work also restricts possible claims:

- [Uptane](https://doi.org/10.1109/MVT.2017.2778751) and its [versioned specification](https://uptane.org/docs/2.1.0/standard/uptane-standard) already address vehicle update security. Signatures and version checks are established mechanisms.
- [RASUES](https://doi.org/10.1007/s10207-026-01233-1) integrates remote attestation with software updates. Its abstract describes expected states before and after updating. "Attestation plus updates" is not a defensible novelty claim by itself.
- [NeRTA](https://doi.org/10.1145/3623676) schedules dynamic updates in mobile robots around processor idle time. "Scheduling updates without disrupting robots" is also too broad a claim.

These are preliminary source-level observations. They show that several building blocks exist; they do not settle the originality of the team's proposed intersection. Full comparative reading and a reproducible search are still needed. No absence claim about the sources' other features is established here.

**Source follow-up, 2026-11-10:** [Uptane Deployment Best Practices 2.1.0](../research/library/uptane-deployment/README.md) already discusses secure time in section 3.1 and location-based updates in section 7.10 (PDF page 43). Using GPS/location to influence an update is therefore too broad an originality claim. This does not establish that the proposed navigation-integrity/swarm-recovery question is solved; it makes the required comparison more precise. See the [R02 foundations note](../research/reports/R02_Secure_Update_Foundations.md).

## Candidate directions

The [six-topic shortlist](09-topic-shortlist.md) expands the three directions below with signed navigation-configuration rollout, cooperative-localization updates, and navigation-state recovery. These are proposals for investigation, not changes to the accepted thesis question.

| Candidate | Concrete question and possible output | Main overlap to investigate | Feasibility and decision |
| --- | --- | --- | --- |
| **A. GNSS-aware secure updates and rejoining** | Can navigation integrity evidence guide update/defer/recovery and role admission choices for returning swarm members? Output: a joint navigation/software/swarm-state model and comparative experiments. | Uptane compatibility/recovery, RASUES state transitions, GNSS integrity monitors, mobile robot update scheduling, and reconnection protocols. The possible contribution lies in a precisely defined interaction and its evaluation. | Leading candidate for a two-week investigation. All three intended areas are central; no original method is claimed yet. |
| **B. Swarm update freshness when GNSS time is untrusted** | During bounded swarm disconnections and GNSS-time faults, how do time/counter policies affect stale update acceptance and legitimate rejoining? Output: a bounded model and comparison of existing freshness strategies in that swarm setting. | TUF expiration, Uptane's secure time requirements, secure clocks and disconnected-device update protocols. Nonces alone cannot establish that a repository release is the latest. | A narrower alternative within the same three-area direction. Novelty and availability guarantees remain uncertain. |
| **C. Joint GNSS/update/rejoining fault benchmark** | Which combinations of navigation faults, update failures, and swarm reconnections expose differences between admission policies? Output: scenario specification, baselines, trace format, and characterization. | Existing navigation fault, OTA testing, and robotics benchmarks must be searched explicitly. Useful coverage and credible models are required. | An empirical alternative within the same direction if a new controller is unjustified. Confirm that this contribution type meets thesis requirements. |

These alternatives are research proposals, not claims that an open problem has been found. An engineering integration may be a sound undergraduate thesis, but its contribution must be described accurately and accepted by the advisor.

## Recommended working question

> In an intermittently connected UAV swarm, can GNSS/IMU-based navigation integrity evidence improve secure update, recovery, and rejoining decisions compared with static policies, while preserving the same software authorization and role safety requirements?

Investigate two explicit links: **navigation evidence to role eligibility during rejoining**, and **navigation/mission state to whether a modeled software update or recovery can begin**. The second is a design hypothesis requiring a concrete operational model; a low GNSS score does not universally imply that an update should start or stop. GNSS time versus update freshness is a separate possible interaction. Do not conflate position uncertainty with clock integrity.

Ceren's work covers the navigation evidence model, validation, uncertainty propagation, and fault scenarios. Samet's work covers authorized updates and recovery. Halil's work covers joint decisions and swarm mission effects. A new GNSS spoofing detector is not automatically required, but navigation evidence must have a measurable role in the final question.

## Decision gate: 2026-11-07

The two-week date is a working team target. Move it if the team agrees, while protecting time for implementation and writing.

Before committing to A:

1. Each author reads the nearest work for their area and completes at least two evidence-backed notes. Cross-review the three closest papers together.
2. Complete targeted searches for all three candidates, plus backward/forward citation chasing. Record queries and screening decisions.
3. Identify at least one precise baseline limitation supported by a section-level comparison. Use "unknown" where a paper has not been fully checked.
4. Define a falsifiable hypothesis, a feasible comparator, and the exact outcomes that would refute the hypothesis.
5. Walk through one interrupted-update case with independent ground truth. Show why the proposed controller makes a different admissible decision from the strongest baseline.
6. Discuss the resulting one-page assessment with the advisor, including acceptable contribution type and hardware expectations.

**Retain A** if its question is distinct, implementable, and testable. **Narrow to B/C** if they offer a stronger question within the same direction. If none produces an acceptable contribution, discuss a replacement with the team before changing the intended domain. Reusing existing mechanisms is encouraged; mislabeling them as novel is not.

## Claims currently prohibited

- "The first secure UAV rejoining framework."
- "Signed firmware proves that the UAV is not compromised."
- "Combining three inputs is automatically novel."
- "A lower false acceptance rate against identity-only admission proves superiority over the literature."
- "A few simulation runs prove a security guarantee."

## Open decisions

- Accept A, B, C, or a replacement after the decision gate.
- Define the specific mission and role compatibility contract.
- Define concrete activation, health, and evidence contracts for the mission/coordination application target accepted in [ADR 0002](decisions/0002-update-mvp-requirements.md); the first prototype excludes flight-control firmware replacement.
- Confirm the official May deadline, thesis format, contribution expectations, and licensing/visibility choices.
