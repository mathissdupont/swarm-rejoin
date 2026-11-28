# Comparative reading note: El Yaacoub et al. (2023)

- Source ID: `yaacoub2023`. [Publisher DOI](https://doi.org/10.1145/3623676) · [Institutional record](https://epub.uni-regensburg.de/55328/)
- [Archived original and text capture](../../library/yaacoub2023/README.md)
- Edition checked on 2026-11-28: published 27-page ACM journal article. This assisted author-stage update extends the selected-section reading dated 2026-11-16.
- Reading depth: focused method and evaluation review of §§3–8, including the original idle-time plot. Full proof and neighboring-work checks and an independent team review remain pending.
- Inclusion: nearest robot-controller update timing reference for [R01](https://github.com/mathissdupont/swarm-rejoin/issues/1).

## Question, method and assumptions

NeRTA estimates when a low-level robot controller can execute update work while preserving its existing task schedule. The scheduler provides each upcoming job's earliest release time. Base NeRTA estimates the conservative idle interval from the earliest of those release times and the current time, then checks whether an update stage of known duration fits. The model assumes computable release times, known worst-case execution times and valid intermediate states for a segmented update. The base scheduler's timing property is conditional on this model.

## Claim-to-evidence table

| Authors' mechanism or result | Location | Evidence examined | Limit in this review |
| --- | --- | --- | --- |
| Update work fits into available processing time | §3.1–3.3, Figure 6; PDF pp. 6–10 | NeRTA queries the existing scheduler and rechecks after another completed job if no safe window is available. | The release-time and execution-bound assumptions do not carry over automatically to a Linux companion application. |
| Additional mechanisms enlarge the window | §5.1–5.2 and §7.2–7.3 | Mixed criticality can delay low-criticality jobs. Bounded Reactive Control changes control frequencies within trained limits and uses motion speed. GPS coordinates for selecting predefined settings are discussed as a possibility. | Distinguish the basic schedule-invariance property from these optional changes. Speed-dependent adaptation is prior work. The suggested GPS use is not evidence of quantitative navigation integrity appraisal. |
| Idle estimates are compared with actual observed idle time | §7.1, Figures 13–14; PDF pp. 19–20 | A stationary, armed drone is instrumented. The authors collected 4,881 paired observations and excluded 571 zero-idle cases. About three quarters of the remaining 4,310 observations had a difference below 15%. | The denominator is retained paired timing samples, not independent flights or missions. This is accuracy of idle-time estimation. |
| Hardware and simulation support different outcomes | §6, §7.3–7.4, Table 3 and §8 | The study uses a Hackflight-based prototype for timing and a simulator to assess the operational effect of controller changes. The validity section says that update execution in the evaluation is represented by a known-duration task rather than actual installation. | The results do not establish real artifact verification, as-flown update recovery, or end-to-end mission continuity. |

## Relevance and comparator fit

NeRTA establishes processor-aware update scheduling and reports its cost and validity boundaries. It helps separate any measured installer cost from synthetic downtime in SWARM-REJOIN. Our scope specifies a Linux companion application with ground-only activation. A direct timing comparison would first require matching update target, scheduler information and control objectives. Preserve identical timing inputs, security gates and recovery options across our competing policies. Existing motion-aware scheduling belongs in the prior-work comparison rather than a novelty claim.

The complete authorization, freshness and recovery properties of surrounding systems are outside the primary timing evidence in this note. The article's numerical results, scheduler guarantees and replication package have not been independently reproduced. An author other than the contributor should verify the section references and confirm the limits before R01 closure.
