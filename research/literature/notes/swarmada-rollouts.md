# Selected-source note: Swarmada rollouts

- Source: `swarmada-rollouts`, [project](https://github.com/swarmada/swarmada), [pinned source/license archive](../../library/swarmada-rollouts/README.md).
- Checked: 2026-11-27. Commit `8415495eff904b5d03c47ffdb263d895c0ed752a`.
- Retained: complete `api/v1/rollout_types.go` and firmware/model rollout controller files, wrapped as Markdown with per-file URLs. Three-file capture, not the whole project.
- Reading depth: selected API/batch/recovery sections; no build, test execution, full code audit, deployed-robot validation or peer-review claim.

| Original location at the pinned revision | Checked mechanism | Comparison limit |
| --- | --- | --- |
| `api/v1/rollout_types.go`, lines 104-113 | Maximum simultaneous updating count/percentage and pause-on-error policy | Count-limited rollout is an existing mechanism |
| Same file, lines 353-357 | Comment explicitly says firmware `RollbackPolicy` is not read by a controller at this version | API vocabulary is not evidence of implemented automatic firmware recovery |
| Same file, rollback comments at lines 435-439 and ModelRollout declaration around lines 735-745 | Capability suspension during model update and retained-version reactivation semantics | Distinguish model and firmware behavior; do not generalize to all update targets |
| `firmwarerollout_controller.go`, around lines 247-279 | Failure pause, remaining slots and sorted eligible-robot selection | Actual qualification of every eligible robot requires broader code review |
| `modelrollout_controller.go`, around lines 259-330 | Auto-revert handling and pause decisions after reversion | Restoring a model version is not by itself navigation qualification for a mission role |

This source materially overlaps robot-update/capability/recovery integration. No global assertion that GNSS-aware recovery planning is absent follows from the selected files or from not finding a keyword. Verify adjacent eligibility, adapter and capability code before proposing a runnable comparison. The generic contingency-aware comparator in the [contract](../../../docs/14-recovery-and-role-contract.md) remains mandatory even if this particular project uses simpler batching.

Apache-2.0 license bytes are archived from the same commit. No standalone official PDF was located for these source files. File capture does not demonstrate correctness or a completed project review.
