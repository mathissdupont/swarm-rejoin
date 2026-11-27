# Research closeout assessment

- Date: **2026-11-16**
- Preparation: assisted evidence synthesis; no team meeting, independent cross-review or advisor approval is claimed
- Status: research disposition and topic recommendation for review, not a declaration that every research issue is complete
- Inputs: repository artifacts and live issue bodies/states checked on 2026-11-16

## Assessment

The immediate obstacle is no longer a lack of possible manifest fields. The secure-update mechanisms have a source-based synthesis and a verification-library recommendation. The remaining research gate concerns the closest-work comparison, navigation-model justification and acceptance of one bounded research question.

Recommend continuing the existing **T1 joint navigation/software-state rejoining study**, with **T6 comparative fault characterization** as the fallback contribution if an adaptive policy does not improve a credible static comparator. This is a recommendation, not an accepted final topic or novelty claim. There is no evidence here that all six alternatives should be implemented or that the intended domain must be abandoned.

## Candidate question to take to the topic gate

> Under identical update authorization, ground-only activation, permitted recovery and role-safety constraints, how does navigation-evidence-dependent restricted-role re-admission affect useful mission service compared with a fixed joint policy during combined navigation, connectivity and application-update faults?

This makes GNSS evidence relevant to mission eligibility, rather than assuming that a generic software installation inherently needs GNSS. A benefit claim would be refuted if the predeclared service improvement disappears against B3, depends on relaxed hard constraints, or produces unacceptable unsafe admissions under independent truth. Practical margins and the sensor/mission model remain to be agreed before confirmatory evaluation.

The question is an empirical candidate. Existing signing, metadata, A/B recovery and attestation mechanisms are reused background; their integration alone is not an established original contribution.

## Nearest-work comparison supported so far

| Work | What checked evidence establishes | Consequence and remaining uncertainty |
| --- | --- | --- |
| Dong et al., 2026 | Previously retrieved reconnection passages include identity, program-integrity and behavioral test-task checks | Identity-only admission is an insufficient main literature comparator. Complete-text access remains unresolved in the [source record](../library/dong2026/README.md); navigation/update/recovery coverage remains unknown |
| RASUES / Usman et al., 2026 | Sections 3, 5 and 7 connect trusted measurement/attestation to updates and discuss dual-copy recovery and limitations | A claim of newly combining updates and software-state evidence would overlap. Our assurance assumptions differ; the [expanded note](../literature/notes/usman2026.md) records exact passages and unknown navigation/swarm coverage |
| NeRTA / El Yaacoub et al., 2023 | Sections 3.1-3.2 require scheduler/release-time and update-stage assumptions; section 8 explicitly evaluates a modeled update task rather than an actual update | Ground-only companion updates and mission-role choices need their own comparator. Do not transfer low-level scheduling guarantees or reported timing; see the [expanded note](../literature/notes/yaacoub2023.md) |
| TUF / Uptane / SUIT background | Established authorization, artifact binding, freshness, compatibility and recovery obligations are summarized in [R02](R02_Secure_Update_Foundations.md) | These form shared mechanisms in B3/P, not the proposed novelty. The [library assessment](R02_Verification_Library_Assessment.md) recommends a reference implementation without claiming an installer or secure clock |
| Uptane Deployment 2.1.0 | Sections 3.1 and 7.10 already discuss secure time and location-based updates | Neither GNSS-time caution nor location-aware update gating alone is a defensible new claim |

These are selected-passage comparisons, not completed full-paper reviews. Missing a feature in these passages is not evidence that the complete work lacks it.

## Research acceptance audit

| Research item | Verified disposition on 2026-11-16 | Exact remaining acceptance evidence |
| --- | --- | --- |
| R02 / [#2](https://github.com/mathissdupont/swarm-rejoin/issues/2) | Open. Requirements, section-cited mechanism/threat table, two failure traces, fallback/downgrade examples and a versioned library desk assessment are now available | Ceren or Halil checks the source interpretations and traces, with disagreements/resolution recorded. Runtime tests and a final executable schema are later work, not fabricated completed research |
| R01 / [#1](https://github.com/mathissdupont/swarm-rejoin/issues/1) | Open. RASUES/NeRTA notes now use selected full-text passages; Dong remains access-limited | Complete the three comparative reading notes to the issue's stated depth and another-author review; retain unknowns where access fails rather than invent findings |
| R03 / [#3](https://github.com/mathissdupont/swarm-rejoin/issues/3) | Administratively closed; the local draft and [2026-11-01 review](../reviews/2026-11-01-r03-review.md) explicitly retain scientific acceptance gaps | Original-method reading and one justified sensor/trajectory/evidence model. Administrative closure is not evidence of detector validation |
| R04 / [#4](https://github.com/mathissdupont/swarm-rejoin/issues/4) | Open. The local source matrix and NeRTA note give a starting comparison; no completed R04 report was found in the inspected main-workspace reports | Logged targeted swarm/update comparator search, at least two accessible full reading notes and an assumption table. This audit does not infer that Halil has done no work outside the inspected artifacts |
| R05/R06 / [#10](https://github.com/mathissdupont/swarm-rejoin/issues/10), [#11](https://github.com/mathissdupont/swarm-rejoin/issues/11) | Topic recommendation is proposed here; no advisor acceptance is recorded in the inspected artifacts | Evidence-backed topic comparison and an explicit team/advisor disposition on question, contribution type and scope |
| D01/D02 | The [manifest draft](../../docs/11-update-manifest-draft.md) and lifecycle boundaries are preliminary designs | Final fields, units, numerical bounds, trusted-time interface and durable-state transitions follow the selected question. Do not expand the manifest indefinitely as a substitute for the literature/topic gate |

Live issue state and local artifact acceptance are separate. Issue #3's body retains an old PR-state sentence; this audit uses the local merged report/review as artifact evidence and does not treat that sentence as current PR verification. No issue was closed, assigned, or represented as independently reviewed by this audit.

## Bounded path to research sign-off

1. Cross-review R02 against the explicit four checks at the end of the library assessment. Its desk evidence is ready; another-author acceptance is not yet recorded.
2. Finish nearest-work and navigation-model evidence at the defined issue acceptance depth. Concentrate on the main question and fallback; report any unresolved source-access limitation explicitly.
3. Use the same inputs, hard constraints, recovery options and role menu for B3 and P. Keep identity-only comparisons contextual. Define one joint-fault and one infeasible-capacity example before claiming a policy distinction.
4. Record the team/advisor topic disposition and acceptable contribution type. A negative policy result can support the empirical fallback only if that contribution is accepted.

No simulator, updater, benchmark or flight study was implemented for this closeout assessment. It identifies completed desk deliverables and finite research acceptance gaps; it does not certify novelty or silently replace missing team review with an assistant's approval.
