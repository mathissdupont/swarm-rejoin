# ADR 0003: Companion deployment and ground-only activation

- Date: 2026-11-10
- Status: Accepted prototype boundary; implementation, hardware feasibility, and final thesis question remain open
- Decision owner: Samet Ünsal, through explicit approval of the deployment recommendation
- Related decisions: [ADR 0002](0002-update-mvp-requirements.md), [system design](../04-system-design.md), [evaluation plan](../06-evaluation-plan.md)

## Decision and rationale

Target the mission/coordination application on an onboard Linux companion computer. Keep flight-control firmware outside the first update target. This matches the proposed problem: a returning vehicle may need a compatible coordination application before it can resume a swarm role. It is a project scope choice, not evidence that this architecture is best for every UAV or that its performance has been demonstrated.

Separate downloading and verifying a candidate from activating it. In the first prototype, activate a candidate only while the vehicle is confirmed landed and disarmed. Recovery that replaces or restarts the target application uses the same ground-only boundary. Other vehicles may continue their mission under the modeled capability constraints; continuity is an outcome to measure, not a guarantee.

Python-TUF remains an evaluation candidate. This decision does not select a language, dependency version, update framework, hardware board, or production installer.

## Operational boundaries

| Operation | Required boundary |
| --- | --- |
| Download and stage | Preserve the authorized active application; validate metadata and complete bytes under ADR 0002; airborne resource budgets and permission to transfer remain to be specified |
| Activate or restart into a fallback | Require current trusted operational evidence of landed and disarmed state, all mandatory update checks, and withdrawal of cooperative mission permissions during the transition |
| Maintain the activation boundary | Define an interlock that prevents arming/takeoff during activation, health checks, and application recovery; a one-time status check is insufficient |
| Finish activation or recovery | Check application health, obtain current software/navigation evidence, and appraise roles again before restoring mission permissions |
| Rejoin without application replacement | Ground-only activation does not itself prohibit an airborne reconnect; admission still requires current software, navigation, and role evidence |

Unknown, stale, or conflicting landed/arming evidence defers activation. GNSS position confidence alone does not establish landed/disarmed state. A landed, disarmed vehicle may still have untrustworthy navigation; successful installation does not authorize its takeoff or full-role admission.

The exact status source, evidence age bound, interlock, response to unexpected state changes, and flight-controller behavior when the coordination application disappears must be specified under D01/D02 before integration. Policies cannot read simulator ground truth to establish these conditions; the independent evaluator uses truth to detect violations. Modeling a trusted interlock is not proof that a physical device enforces it.

## Trust and deployment boundaries

Model the updater/recovery manager and its trust/persistent security state separately from the application being replaced. A process boundary alone is not a demonstrated security boundary. A production deployment needs a concrete privilege, storage, and trust-protection design; this decision makes no secure-boot, hardware-root-of-trust, or remote-attestation claim.

A companion computer also creates hardware integration obligations. Select a representative target and measure update verification time, peak memory, service interruption, and effects on other workloads. Record hardware, environment, artifact size, and revision. Weight, power, storage, and cost constraints remain to be assessed; laptop simulation and SITL cannot establish them for an unspecified device.

Existing background on authorization and recovery is recorded in the [R02 source note](../../research/reports/R02_Secure_Update_Foundations.md), especially sections 3-5. Those sources do not prescribe the project-specific Linux target or ground-only activation rule above.

## Acceptance cases to implement

1. A valid candidate is staged while the vehicle is airborne: activation is deferred and the active application is preserved.
2. The vehicle reports disarmed but landed evidence is unknown or stale: activation is deferred.
3. Current operational evidence confirms landed/disarmed state, the interlock is established, and every required check passes: activation may begin while cooperative mission permissions remain withdrawn.
4. Candidate health fails: attempt only a permitted fallback under the same operational boundary; report failure and retain isolation if recovery is unavailable.
5. Activation succeeds but navigation evidence is inadequate: do not grant a role requiring trustworthy navigation.
6. An arming/takeoff request arrives during activation or recovery: the modeled interlock prevents it; later integration must verify actual enforcement.

These are planned behavioral cases, not implemented tests or measured results. Apply the same activation boundary to the main B3/P comparison. Final contract fields and a verification-library evaluation are the next design work; R02 and the final topic decision remain open.
