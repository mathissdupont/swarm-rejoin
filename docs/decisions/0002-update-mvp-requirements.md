# ADR 0002: Accepted update requirements for the first prototype

- Date: 2026-11-10
- Status: Accepted prototype requirements; implementation and final thesis-topic selection remain open
- Decision owner: Samet Ünsal, through explicit approval of the six choices below
- Related work: [R02](../../research/reports/R02_Secure_Update_Foundations.md), [system design](../04-system-design.md), [issue #2](https://github.com/mathissdupont/swarm-rejoin/issues/2)

## Context

The source-based R02 note describes established update mechanisms and two designed failure traces. A concrete prototype needs agreed behavior for the update target, authority, verification, interrupted transfers, failed activation, and unreliable time. This record captures accepted project choices, not experimental findings or approval by other team members.

## Decisions

| ID | Accepted requirement | Required consequence |
| --- | --- | --- |
| U1 | Update the onboard mission/coordination companion application | The first prototype does not replace the flight-control firmware; activation and health checks concern the companion application |
| U2 | Use a trusted release authority associated with the ground station, with its verification key provisioned on each UAV | Verify the signature and the signer's update authority against the configured trust anchor; authority-key compromise and unauthorized replacement of trust state are excluded from the initial model |
| U3 | Check authorized signature, complete payload size/digest, target/component identity, compatibility, freshness/persistent security restrictions, then activation health | Every mandatory pre-activation check must pass before a candidate runs; startup success requires a separate post-activation health check and role re-appraisal |
| U4 | Preserve the authorized active application during an interrupted download | Never activate a partial candidate; retry/resume only under valid metadata; retain a mission role only while its current navigation/software prerequisites hold |
| U5 | Recover only to a still-authorized, verified working fallback | Do not reset security restrictions to permit a prohibited image; recheck health and role eligibility after fallback; isolate from cooperative mission roles if no usable authorized fallback exists |
| U6 | Do not rely solely on GNSS-derived time for update freshness | Defer acceptance of a new update when sufficient trusted time/freshness evidence is unavailable; evaluate any continued service by the active application separately |

U3 defines the required gates, not permission to process unbounded untrusted input. Bounded syntax/format checks are needed to locate signed bytes safely. Metadata target, compatibility, and freshness checks may be performed earlier to avoid unnecessary transfer, but none may be skipped or compensated by mission utility. Payload verification still requires the complete bytes before activation.

## Trust terminology and assurance

The ground-station release authority is an organizational/protocol role. Its preprovisioned verification key is a **trust anchor** on the device. The trusted mechanism that protects that anchor and verifies authorized software belongs to the trusted computing base; stronger root-of-trust claims depend on its actual protection and measurement design.

The MVP assumes trustworthy provisioning, verifier behavior, and protected persistent security state in its model. It does not implement or demonstrate a hardware root of trust, secure boot, or TPM-based remote attestation. A valid update signature does not prove that a remote UAV is uncompromised or that the signed bytes are currently executing.

Terminology references: [RFC 9019](../../research/library/rfc9019/README.md), sections 2 and 7; [RFC 9334](../../research/library/rfc9334/README.md), sections 7.4 and 12. These references support the distinction; the concrete protection assumptions above are project choices.

## Implementation acceptance examples

1. Tampered manifest or payload: no activation and no new mission permission based on the candidate.
2. Interrupted transfer: active authorized bytes remain unchanged; partial candidate is not reported as complete.
3. Valid signature with wrong target, incompatible protocol, or failed freshness/rollback policy: reject the candidate.
4. Candidate startup/health failure with a permitted fallback: recover, obtain current evidence, and decide roles again.
5. No authorized healthy fallback: retain only a bounded authorized remediation channel; cooperative mission roles remain isolated.
6. Untrusted GNSS time without sufficient independent freshness evidence: defer the new update; no automatic full-role admission or blanket inference that the active application is unusable.

These are tests to implement, not tests already executed.

## Remaining work

- Evaluate a maintained signature/update-verification library or reference implementation and record its fit and limits for this MVP.
- Specify manifest encoding, time bounds, persistent-state behavior, compatibility contracts, health criteria, and evidence expiration under D01/D02.
- Obtain Ceren's or Halil's source cross-review required by R02. Samet's approval of these requirements is distinct from that independent review.
- Implement and validate the failure cases before claiming update safety or mission benefits.

R02 remains open while its remaining research acceptance items are incomplete. This decision does not claim advisor approval, select among all candidate thesis topics, or authorize a change to the GNSS/update/swarm research scope.
