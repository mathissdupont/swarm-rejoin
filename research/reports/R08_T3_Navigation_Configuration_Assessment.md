# R08 / T3: Signed navigation-configuration rollout

- Date: 2026-11-27
- Task: [issue #6](https://github.com/mathissdupont/swarm-rejoin/issues/6)
- Preparation: assisted candidate assessment for Samet Ünsal; Ceren's sensor/model choices and independent review are not implied
- Status: author-stage assessment delivered; an alternative topic, not a change to the accepted mission-application update target

## Concrete candidate

Study a signed, versioned configuration package for a companion localization service: a finite set of measurement-noise or consistency-monitor settings with exact schema/component compatibility. Do not change flight-controller firmware or call this configuration-only candidate firmware updating. A config-only study would require a separate scope decision before replacing the accepted application target.

The proposed question is whether navigation-specific validation can stop harmful but authorized configurations from propagating through a swarm more effectively than a fixed canary rule. The signature establishes authorized configuration bytes, not that the chosen values are operationally good.

## Evidence and overlap

| Evidence | What is established | What is not established |
| --- | --- | --- |
| [RFC 9019](../library/rfc9019/README.md), architecture scope and section 6 | Update metadata and application of protected configuration information are existing building blocks | A new navigation-specific rollout policy or empirical benefit |
| [RFC 9124](../library/rfc9124/README.md), sections 3.3-3.6, 3.13-3.16 | Applicability and exact authenticated payload binding | Correct navigation behavior from a valid signature |
| [Flagger official guide](../library/flagger-canary/README.md), Canary analysis | Periodic metric-based promotion/rollback is established deployment practice | A Kubernetes traffic metric is not a UAV navigation-integrity criterion |
| [RASUES review](../literature/notes/usman2026.md), sections 4-5 and 8 of the paper | Updates and before/after software-state appraisal already interact | Successful attestation alone does not establish navigation performance |

The targeted discovery query `robot navigation configuration updates canary deployment regression testing software` returned general deployment guidance as well as unrelated material. Technical claims here use the retained primary/official sources; no absence or first-work claim follows. Exact queries, screening and acquisition outcomes are in the [search log](../literature/search-log.md).

## Minimal proposed experiment

Use the same authenticated configurations, device class, navigation/fault traces, mission tasks, available telemetry and rollback restrictions for three policies:

| Policy | Proposed behavior |
| --- | --- |
| Immediate rollout | Activate on each otherwise eligible vehicle at its first permitted ground opportunity |
| Fixed canary | Update a preselected subset; promote after fixed checks/time; abort on the same mandatory failure rules |
| Navigation-evidence rule | Use a declared, frozen navigation-specific promotion/abort rule on appraised telemetry, with the same security/role constraints |

All three require ground-only activation and retain only permitted fallback configurations. A canary's validation episode is a simulated representative trajectory or replay in the first study, not permission to conduct a physical flight with unvalidated settings. Ground activation by itself cannot establish dynamic navigation performance.

Hold the diagnostic/appraisal rule fixed when the candidate configuration changes a monitor: a candidate must not certify its own quality merely by relaxing its thresholds. Policies cannot access the evaluator's true position or fault labels. Use independent truth to label harmful promotion, missed harm and false aborts. Legitimate adverse conditions and harmful-but-signed parameters both belong in the model.

Predeclare development and held-out maneuvers, configuration families, role requirements and mission-capacity shortfalls. Include an unrepresentative-canary case: the first vehicle never encounters the condition that harms the remaining vehicles. Configuration and fallback data-schema compatibility must be explicit.

Candidate maneuver families are stationary/hover, straight motion, turns and acceleration/deceleration, with separate benign noise and GNSS-degraded conditions. Their exact trajectories and noise ranges must come from the selected navigation model. Include optimistic uncertainty settings that hide error and overly conservative settings that unnecessarily exclude usable roles; neither signed setting is assumed beneficial. Calibration data used to choose the promotion rule must be separated from held-out cases used to judge it.

## Measurements and refutation

Measure harmful promotions, false aborts, affected-vehicle count, useful-service loss, rollout completion and permitted-recovery success with denominators and censored cases. No values have been measured. Refute the proposed advantage if it vanishes against fixed canary under the same inputs, depends on hidden truth, or only works because a candidate's own relaxed monitor defines success.

## Disposition

Keep T3 as an alternative if the advisor prefers a configuration-regression study. It is more concrete than generic secure OTA, but a navigation-specific rule still needs justification and nearest-work checking before any novelty claim. It does not replace T1 merely because canary deployment is available. The author-stage artifact answers issue #6's target, existing mechanisms, minimal comparison and refutation requirements; no experiment or team approval is claimed.
