# R10 / T5: Navigation evidence after authorized application recovery

- Date: 2026-11-27
- Task: [issue #8](https://github.com/mathissdupont/swarm-rejoin/issues/8)
- Preparation: assisted candidate assessment for Samet Ünsal; not an implemented protocol or Ceren/Halil cross-review
- Status: author-stage model, counterexample and refutation delivered; final topic selection remains open

## Narrow question and system boundary

After an authorized restart/fallback of the mission application, can conditional navigation-evidence revalidation reduce loss of useful swarm service compared with full reinitialization while preserving the same admission constraints?

Do not conflate three events:

| Event | What may remain continuous | Required interpretation |
| --- | --- | --- |
| Mission companion application restarts; flight controller/estimator continues | The estimator's internal state and producer clock may continue | Renew application/session binding and obtain current producer output; do not assume the filter restarted |
| Localization producer or its configuration restarts/changes | Some calibration or stored configuration may persist | Check producer/configuration identity, warm-up, reference frame and current uncertainty; old confidence is not automatically reusable |
| Flight controller/producer boot changes or continuity cannot be established | No trustworthy continuity follows from a matching small counter | Treat the continuity-dependent evidence as unknown and follow the defined conservative reinitialization/revalidation policy |

The first event matches the accepted application-update target. The other events are explicit fault/model cases, not a plan to flash flight-critical firmware. Restarting a process is not itself a detector-state reset or proof of hardware isolation.

The proposed producer-state abstraction is `STARTING`, `WARMING`, `TRACKING`, `DEGRADED` and `UNAVAILABLE`. A genuine producer restart enters startup/warm-up; a companion-only restart does not force that transition when producer continuity is established. Warm-up ends through the selected estimator's declared initialization/calibration conditions, not merely because a timer elapsed. Exact timing and covariance behavior require the chosen sensor model and are not fabricated here. Retained calibration may be reused only under a compatible authenticated configuration; it does not make a cached position estimate or confidence report fresh. Faults may move a tracking producer to degraded/unavailable state while application health remains good.

## Source-backed overlap

| Source | Examined evidence | Consequence |
| --- | --- | --- |
| [RASUES](../literature/notes/usman2026.md), sections 4-5, 7-8, Figure 4 | Update processing, changed expected measurements, attestation, recovery and stated limitations | Before/after software-state checking and A/B recovery are already established; a signed package is not current navigation evidence |
| [RFC 9334](../library/rfc9334/README.md), sections 7.4, 8.1 and 10 | Evidence appraisal/trust and freshness options | Freshness must apply to the claim/measurement context, not only an outer message |
| [Pinned PX4 message definition](../library/px4-local-position/README.md) | Boot-relative timestamps, validity, reset counters and error estimates | Possible adapter inputs exist, but these fields do not supply our session/configuration/trust contract or guarantee correct position |
| [Alja'afreh et al. selected-source note](../literature/notes/aljaafreh2026.md) | Publisher mode-management/recovery passages already discuss sustained evidence before source reintegration | Generic waiting for stable GNSS or sensor reintegration is not our novel contribution; source reintegration and swarm-role admission remain distinct decisions |

PX4's `uint8` reset counters can wrap and do not identify a boot or prove cryptographic continuity. Timestamps from different boots/clock domains cannot be subtracted as though they were one trusted clock. Confidence/error estimates require calibration in the chosen sensor/trajectory model.

## Designed stale-evidence counterexample

This is a conceptual trace with no measured numerical values. Assume a trusted release authority, honest modeled producer, protected security state and a controller that receives only observable evidence.

1. Vehicle U has a still-authorized release A and caches navigation report E from producer boot F1, configuration C1 and application session S1.
2. E ages during an outage; current GNSS/IMU conditions no longer justify E's former role eligibility. Independent world truth records the actual error; the policy cannot read it.
3. On the ground, candidate B fails health. A is an authorized, data-compatible fallback above the unchanged security floor, so application recovery is allowed.
4. The recovered application starts session S2 and answers a new authentication challenge, but incorrectly reuses cached E. A fresh wrapper/challenge does not make E's sample current or prove producer/configuration continuity.
5. An immediate-reuse policy grants a navigation-dependent role based on E. The independent evaluator labels that grant unsafe if its true prerequisites are unmet.
6. A revalidation policy invalidates the old session permission, checks the producer/boot/configuration/frame and age context, and obtains current evidence before role appraisal. If the flight-controller estimator actually continued, it need not be forcibly reset just because the companion restarted.

If the trusted producer is allowed to lie about sample provenance, the initial trust model is exceeded. Do not claim this policy solves arbitrary compromised measurement agents or establishes remote attestation without a protected measurement mechanism.

## Comparison and possible falsification

| Policy | Proposed handling | Cost/risk to evaluate |
| --- | --- | --- |
| Immediate reuse | Reuse cached navigation state after application health succeeds | Contextual weak baseline; stale-state unsafe admissions may result |
| Full reinitialization | Invalidate old context and require a defined complete warm-up/revalidation after every recovery | Conservative comparator; may discard a continuously operating estimator's usable state |
| Conditional revalidation | Reuse only the underlying state whose trusted continuity is established, obtain fresh output, and reappraise roles | Candidate rule; unknown continuity follows the same conservative path, never an optimistic default |

Use identical actual release authorization, recovery images, producer observations, role requirements and independent truth across policies. Candidate benefit must survive comparison with a credible conservative policy that can already reacquire current output, not only with deliberately unsafe immediate reuse.

Measure false re-admission, time to a genuinely eligible role, useful service and failed recovery. Include producer-continues, producer-resets, changed configuration, stale samples, correlated navigation faults and no-authorized-fallback cases. Warm-up and uncertainty behavior are research-model inputs requiring Ceren's justified sensor/trajectory assumptions, not guessed constants supplied here.

Refute the benefit claim if conditional revalidation is equivalent to the credible conservative comparator, relies on unavailable provenance, admits unsafe roles, or loses any useful-service advantage on held-out faults. A negative result is a valid observation only if the advisor accepts the empirical contribution.

## Disposition

Recommend T5 as a precise subquestion within the existing T1 application-recovery/rejoining direction, rather than a separate flight-controller updater. This is a proposed narrowing, not an accepted novelty or advisor decision. It gives issue #8 a concrete model, source comparison, counterexample, comparable policies and refutation condition; hardware assurance, calibration, implementation and independent acceptance remain separate.
