# Comparative reading note: El Yaacoub et al. (2023)

Source ID: `yaacoub2023`. [Institutional record](https://epub.uni-regensburg.de/55328/).

Last checked: **2026-11-16**. Reading depth: selected full-text introduction, related-work, sections 3.1-3.2 and 8-9, using the [archived original and text capture](../../library/yaacoub2023/README.md). This is an assisted comparative note, not a completed full-method/experiment review or independent team cross-review. Equations, figures and reported numerical results have not been independently validated.

## Observed overlap

NeRTA schedules dynamic updates of low-level mobile robot software using processor idle time. Generic claims about nondisruptive robot update scheduling would overlap.

## Section-specific comparison

| Topic | Observed evidence | Consequence for SWARM-REJOIN |
| --- | --- | --- |
| Operational target | Introduction / PDF pages 3-4 and section 3.1 / PDF page 6 target updates on existing low-level controllers while retaining the scheduler | This differs from our companion application and ground-only activation boundary; generic nondisruptive update scheduling is already studied |
| Timing assumptions | Section 3.1 / PDF page 6 needs job release-time information and identifies unsuitable scheduling cases without guaranteed inter-arrival timing | We cannot claim NeRTA's scheduling property for an arbitrary Linux process or our event simulation |
| Update correctness | Section 3.2 / PDF page 7 requires known worst-case durations, non-preemptive update stages and a valid system between stages | A package/installer must define valid transition boundaries; separate code and state updates may leave an invalid combination |
| Evaluated update model | Section 8 / PDF page 25 states that no actual update is performed during evaluation: an update is modeled as a task with known worst-case duration, and evaluated updates are single-stage | Distinguish real artifact verification, simulated downtime and measured deployment behavior in our own study |
| Fidelity and generality | Section 8 / PDF pages 24-25 separates simulator dynamics from onboard computing and discusses scheduler/utilization limits | Laptop/SITL timing must not be presented as target-microcontroller performance |

## Comparator fit and remaining questions

NeRTA is relevant to timing assumptions and the limits of update models. It is not automatically a fair drop-in controller for our ground-only application updates and swarm role allocation. A direct implementation comparison would first require matching update granularity, scheduler information and operational objectives. Our B3/P comparison should share the same measured or explicitly synthetic update costs.

The related-work discussion on PDF pages 5-6 recognizes security concerns and complementary secure OTA work. Therefore, do not describe the paper as simply ignoring update security. The complete security/freshness/recovery coverage and any navigation/team-level treatment remain **unknown** until the rest of the method, evaluation and references are checked.

No paper performance number or scheduling guarantee has been reproduced by this repository. A full comparative review still needs the algorithm, assumptions/proofs, experiments and neighboring-work checks, followed by another author's review.
