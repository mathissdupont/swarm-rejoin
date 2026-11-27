# D01 draft: recovery, navigation and role eligibility

Version: **0.1, 2026-11-27**. Proposed semantic contract for [issue #12](https://github.com/mathissdupont/swarm-rejoin/issues/12), not an accepted wire schema, implementation or verified safety argument. The selected sensor model and another-author review remain pending.

## Concrete research question

> Can pre-activation planning that accounts for navigation eligibility after authorized recovery reduce mission-capability shortfalls compared with nominal update planning, and what does it add over a generic contingency-aware role planner?

This refines the T1/T5 question. Evidence revalidation is a shared prerequisite for every credible policy. The candidate decision is whether to start an otherwise authorized update now, update another eligible member, or defer, given the roles that would remain feasible after success or failure/recovery.

The [accepted companion/ground boundary](decisions/0003-companion-deployment-and-ground-activation.md) is unchanged. The contract does not introduce flight-controller updating or authorize airborne activation. See the [originality assessment and worked example](../research/reports/Originality_Assessment_2026-11-27.md).

## Objects and required semantics

| Object | Minimum semantic contents | Failure or unknown handling |
| --- | --- | --- |
| Release appraisal | Authority/policy revision; exact artifact identity/size; target and compatibility; release/security epoch; applicable floor and authorization; metadata freshness evidence | Reference real verification when implemented. Model inputs are not cryptographic verification. Reject affected actions if mandatory appraisal fails |
| Recovery option | Exact retained image; current authorization, integrity and bootability evidence; data/configuration compatibility; required operational state; health and navigation revalidation obligations | Keep no-fallback and unusable-fallback outcomes explicit. A stored image is not automatically a usable recovery option |
| Application context | Vehicle, application session, active release identity, lifecycle phase and health context | An old session's mission grants cannot survive replacement/recovery automatically |
| Navigation context | Producer identity/boot context; configuration, frame and reset generation; original measurement time/clock domain; receipt-age bound; validity/uncertainty; relevant monitor-history continuity | Unknown context cannot establish continuity. A challenge binds a response, not the age of an embedded observation |
| Recovery-readiness prediction | For each declared branch, earliest/latest justified time to fresh appraised evidence and supported roles; assumptions, provenance and validity of prediction | No prediction based on hidden future truth. Unsupported branches receive conservative unknown capability, not optimistic readiness |
| Role/mission contract | Mission revision, role capabilities, release/protocol combinations, navigation/age limits, operational/location requirements, demand over time, role concurrency rules | Current role requirements remain mandatory; unachievable team demand is a reported mission shortfall |
| Operational context | Confirmed landed/disarmed state and freshness, arming/takeoff interlock, available activation/storage resources | Unknown interlock/state blocks activation/restart recovery. Later takeoff needs its own checks |
| Grant/decision record | Input-context revisions, policy revision, chosen action, rejected alternatives/reasons, bounded permission expiry and dependencies | Expire/reappraise on relevant changes; keep decisions separate from independent outcome labels |

No numeric sensor threshold, recovery duration, confidence calibration or hardware guarantee is asserted by this draft. Ceren's selected model must justify those inputs. A predicted qualifying role still requires fresh appraisal before an actual grant.

## Dependency and invalidation table

| Event | Invalidate / recheck | What is not implied |
| --- | --- | --- |
| Application replacement or fallback restart | Old application/session grants, release/health binding, application-owned history whose continuity is unproven | The flight-controller estimator did not necessarily restart |
| Producer boot or unknown producer continuity | Producer-clock mapping, continuity-dependent history and claims; obtain current evidence under justified initialization rules | A matching small reset counter is not boot identity |
| Navigation configuration/schema change | Dependent calibration/history interpretation and consumer compatibility | A signature does not validate navigation quality |
| Reference-frame/reset generation change | Frame-dependent claims and role/location interpretation | Transport authentication does not establish frame consistency |
| Original sample ages or its time bound becomes unknown | Roles requiring the affected age/uncertainty bound | A fresh response timestamp does not refresh the original sample |
| Release revocation/floor change | Current action and fallback authorization at commit/grant boundaries | A previously approved recovery plan remains conditional, not permanently authorized |
| Link loss or delayed invalidation event | Finite permission validity and supported age bounds | Permission withdrawal cannot be instantaneous across an unbounded partition |
| Candidate failure but successful image recovery | New software health and navigation/role appraisal | Healthy recovered software does not establish timely role recovery |

## Branch-aware planning rule

Let `o` be appraised observations and `a` a candidate action: defer or activate one eligible vehicle's staged application. Begin with one activation at a time. A future batch extension is optional.

For each action, explicitly specify a finite branch set `B(a)`: successful activation, activation/health failure followed by an authorized available fallback, and relevant no-usable-recovery outcomes. State the failure/time/navigation envelope; the branch set is not all possible real faults. Unbounded recovery delay or arbitrary producer loss may make every action infeasible.

For a projected state `s(a,b,t)`, define `Q(i,r,s)` as model-appraised eligibility of vehicle `i` for role `r`. It includes software authorization/compatibility, health, original evidence age/uncertainty, operational state and relevant continuity. Predictions use justified bounds or conservative uncertainty sets. They are not the evaluator's actual future fault labels.

An assignment `x(i,r)` must satisfy:

```text
x(i,r) in {0,1}
x(i,r) <= Q(i,r,s)
sum_r x(i,r) <= 1                 # initial mutually exclusive role model
sum_i x(i,r) >= demand(r,t)       # where that mission phase requires the role
joint_compatibility(x,s)          # when roles depend on pairwise protocols
```

Activation remains behind its own authorization and ground-interlock gates. A grounded vehicle does not count toward an airborne search demand. If launch/landing is part of a future dispatch plan, include its time, energy and operational checks equally for all policies. Graph connectivity alone never establishes localization observability.

1. Reject actions violating mandatory update/security/operational conditions.
2. Project the declared branches, including required post-recovery navigation revalidation and current authorization assumptions.
3. Check whether mission-role demand can be met over the declared horizon in those branches, not merely whether enough processes can boot.
4. Choose among feasible actions by a frozen useful-service/update-progress criterion; otherwise defer or record infeasibility/mission curtailment under explicit priorities.
5. After observing the actual transition, reappraise and issue bounded role permissions from current evidence. Predicted eligibility is never a grant.

Recourse assignments may depend on branch outcomes only after those outcomes are observable. Choices made before identical observation histories must be identical. Do not obtain an apparent planning benefit through knowledge of future faults or cost-free instantaneous reassignment.

Mandatory security/role gates cannot be relaxed to meet team demand. Urgent security deadlines and mission demand may conflict; report that conflict and curtail the mission where required. A continuity objective does not grant an unauthorized role.

## Comparator contract

Use identical release verification, fallback options, navigation predictions, role constraints, operational opportunities and resource budgets. Evaluate variants of B3 rather than adding misleading published-protocol labels:

- **Count-limited static order:** a contextual rollout rule using the same mandatory gates, with a fixed update order and concurrency limit.
- **Nominal role-aware B3:** assesses role readiness and chooses updates under a successful-transition projection, with the same current evidence and available failure descriptions.
- **Contingency-aware B3 variant:** a generic small exhaustive assignment/action search using the same branches, navigation readiness and constraints as P. This is the critical stronger comparator; it may equal P.

These are proposed project baselines, not implemented Swarmada, NeRTA or MRTA reproductions. A count-only or nominal-only win does not establish a new algorithm. If P equals the generic branch-aware search, retain the domain model/characterization claim only if justified and accepted; do not relabel generic robust planning as an invention.

## Immediate acceptance artifacts

This draft supplies an initial dependency table and decision rule. Cross-review it rather than asking the authors to recreate the same research notes.

| Owner | Remaining validation |
| --- | --- |
| Samet Ünsal | Match retained-image and active-image recovery paths to an actual installer design; include schema rollback and authorization changes. Ensure healthy-image recovery is not assumed to restore navigation automatically |
| Ceren Tolunay | Show whether the worked example's differing recovery-readiness branches can arise in one defensible GNSS/IMU/monitor model. Check retained-state and buffered-evidence alternatives that could remove the difference |
| Halil Abacı | Check assignments, demand timing, nonanticipative recourse, launch costs and generic contingency-aware B3; document equivalence as readily as advantage |

The [2 December gate and eight-week roadmap](07-roadmap-and-team.md) remain working targets. This contract is a research handoff, not completion of calibration, independent review or an implemented updater.
