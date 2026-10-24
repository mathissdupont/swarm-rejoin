# Evaluation plan

Status: proposed; no experiments or outcomes exist. Finalize this plan after topic selection and pilot measurements.

## Fair comparisons

| ID | Policy | Purpose |
| --- | --- | --- |
| B0 | Identity-only full admission | Weak contextual baseline from the initial idea |
| B1 | Identity plus navigation threshold | Shows the effect of navigation checks without secure update controls |
| B2 | Static secure-update admission with a fixed full-role navigation gate | Established security mechanisms; no adaptive role assignment or update timing |
| **B3** | Static joint policy with the same appraised inputs, hard constraints, permitted fallback images, and role menu as the proposal | Main comparator: fixed priority rules for roles, updates, and recovery |
| P | GNSS-aware joint update/rejoining policy | Candidate method: uses navigation evidence in timing and role choices under the same constraints and resource budget |

B0/B1 intentionally lack controls and are not adequate evidence for the main contribution. For the P–B3 comparison, keep cryptography, release metadata, available observations, fault traces, update costs, role eligibility rules, and recovery mechanisms identical. Specify B3's fixed rules before final evaluation. Do not weaken B3 after observing P's performance.

Do not describe B2/B3 as implementations of published protocols unless their requirements are actually implemented. A comparison with Dong/RASUES/NeRTA needs careful assumption matching; otherwise use a feature/assumption comparison and label it accordingly.

## Staged experiments

1. **Unit and state-machine validation:** Known transition traces, hard invariants, invalid inputs, replay, and every update crash point. Use real signature checks in the update component when implemented.
2. **Pilot simulation:** Six agents, a small set of deterministic fault traces, and manual label inspection. Use pilots to find modeling bugs and choose measurement scales, not to claim benefits.
3. **Controlled comparative study:** Paired seeded traces across policies, predeclared scenario families, held-out configurations, and uncertainty estimates.
4. **PX4 SITL case study:** Two or three vehicles, repeatable disconnect/reconnect and companion-service update cases. Report integration limits and observed timing separately from abstract simulation.

## Independent ground truth

Separate the world model from the evidence visible to the policies. Ground truth includes actual position, true artifact/running state, authorization/revocation state, protocol compatibility, link events, and mission progress. Fault generators alter observations without overwriting truth. The evaluator labels the selected action against the actual role requirements and current authorization.

An unsafe admission occurs if the granted role's true prerequisites are unmet at the decision time or during its granted interval. Include hidden faults that evade the monitor. Do not label an admission safe because the policy's score exceeded its own threshold.

## Metrics and denominators

| Metric | Definition |
| --- | --- |
| Unsafe role admission rate | Unsafe role grants / all role grants; also report counts and breakdown by role and fault |
| False exclusion at decision | Denials of an actually eligible requested role / all requests actually eligible for that role; evaluate every policy on the same request set |
| Eventual service failure | Reconnection episodes eligible for some permitted useful role that never reach it within a fixed horizon / all such episodes |
| Time to useful service | Reconnect-to-first-permitted-useful-role interval; retain never-admitted cases as failures/censored observations |
| Time to full role | Reconnect-to-full-role interval, reported separately from restricted service |
| Recovery success | Failed-activation episodes restored to an authorized healthy state by the horizon / episodes where recovery was attempted; also report how many failures had no feasible recovery |
| Useful-service fraction | Time integral of capped useful mission capability / time integral of required mission capability; report requirement shortfalls separately |
| Mission completion | Missions meeting the fixed task/coverage goal by the deadline / all missions |
| Cost | Transferred bytes, verification time, controller time, retries, update downtime, and peak memory where measured |

Restricted roles count only toward capabilities they can actually supply. A relay role does not create search coverage. Do not confuse communication reconnection, authenticated admission, useful service, and full formation participation.

## Scenario families and controls

Use the [scenario catalog](../experiments/scenarios.json) as the initial specification. Include clean reconnects, temporary GNSS loss, step/ramp errors, IMU drift, stale evidence, incompatible versions, tampering, replay, partial updates, activation failure, recovery failure, untrusted time, and combinations. Label synthetic distributions explicitly.

Vary team size (5, 6, 8), outage duration, link bandwidth/loss, update size/duration, agent battery budget, role demand, evidence age, fault prevalence, and detector calibration. Choose pilot ranges first; freeze final ranges with justification. Include benign degradation to measure false exclusions. Do not run an enormous Cartesian product before verifying the models.

## Ablations and negative cases

Compare P against variants with fixed update timing, fixed role selection, and no recovery option, keeping all remaining hard security constraints. To isolate the GNSS contribution, compare against a version using a fixed conservative navigation gate with no navigation-dependent timing/role adaptation. Report detector accuracy separately from decision quality. Do not disable signature or epoch gates as a supposed safe variant of P.

Include cases where all vehicles are compatible and healthy, where updates always fail, where no fallback is authorized, where navigation confidence is falsely high, and where mission requirements are infeasible. P should not be expected to dominate everywhere. If benefits vanish with credible baselines, report the negative result and revise the contribution.

## Statistical and reproducibility plan

- Use a mission run, rather than every correlated sensor sample, as the main independent unit. Pair policies on exogenous fault/mission seeds; keep policy-internal randomness separately recorded.
- Start with a provisional 30 independent seeds per selected configuration for pilot stability, then choose final counts based on precision requirements and cost. Thirty is not a guarantee of statistical power.
- For the primary P–B3 comparison, report paired effect sizes and a paired bootstrap interval over independent missions. Handle rate denominators and censored delays explicitly; predeclare the exact analysis before final runs.
- Report unsafe counts even when zero, with an appropriate upper confidence bound. Zero observed violations is not proof of zero risk.
- Separate development scenarios from confirmatory runs, and retain raw traces, failed runs, exact revisions, dependency/environment records, and configuration hashes.
- Freeze practical improvement margins and any tolerable risk criterion with the advisor before confirmatory testing. Do not invent those thresholds after seeing results.

Avoid comparing abstract simulated seconds with measured cryptographic or PX4 timing as if they came from one calibrated system. Report the fidelity and limits of each experiment layer.
