# Roadmap and team

Authors: **Samet Ünsal, Ceren Tolunay, Halil Abacı**.

The team described a two-semester thesis of roughly nine academic months, with likely submission in **May 2027** and no mandated technology. This plan starts on **2026-10-24**; the remaining work window is about seven months. The official deadline and milestones still need confirmation.

## Proposed ownership

| Workstream | Lead | Required collaboration and tangible output |
| --- | --- | --- |
| Secure update and recovery | Samet Ünsal | Release/evidence model, trusted key assumptions, real signature verification, staged activation and authorized recovery; Halil reviews state transitions |
| Navigation evidence and faults | Ceren Tolunay | GNSS/IMU consistency model, uncertainty/age handling, benign and malicious fault traces, estimator calibration; Samet reviews freshness assumptions |
| Team decisions and evaluation | Halil Abacı | Hard constraints, baseline policies, controller, metrics and paired experiments; Ceren reviews independent safety labels |
| Literature, integration, and writing | All three | Each author reviews adjacent work, integrates one shared scenario, and owns thesis sections with cross-review |

Ownership is a working proposal. Agree on it as a team. Avoid three disconnected demos: all workstreams must share evidence contracts, scenario identifiers, and one end-to-end trace.

## Calendar

| Period | Outcome and exit criterion |
| --- | --- |
| **24 Oct–7 Nov 2026** | Topic gate: closest-work notes, structured searches, contribution assessment, and advisor discussion. Retain, narrow, or replace the question. |
| **Nov 2026** | Freeze initial threat model, role contracts, baseline definitions, and minimum experiment design. Produce a deterministic hand-checked transition trace. |
| **Dec 2026** | Build the small Python simulation and shared trace format. Implement secure update verification and crash/recovery cases; validate navigation evidence. No performance claim yet. |
| **Jan 2027** | Integrate all three workstreams, finish B0–B3 and a simple P, run pilots, refresh literature. Prepare first-semester material to match the actual university schedule. |
| **Feb 2027** | Revise models from pilots; run ablations and sensitivity checks. Freeze confirmatory configurations and analysis. Attempt PX4 integration if the core question is stable. |
| **Mar 2027** | Run the main comparative study; record negative outcomes and uncertainty. Complete the small SITL case study if feasible. |
| **Apr 2027** | Finish analysis, figures, related work, and thesis draft. Obtain cross-review and advisor feedback. Resolve reproducibility issues and scope limitations. |
| **May 2027** | Final checks, reproducibility package, presentation, and submission by the official deadline. Reserve time for administrative and formatting requirements. |

## Weekly rhythm

One 30–45 minute team review: each person brings evidence, an artifact, and one blocker. Review shared assumptions before adding features. Keep decisions and action items in dated notes, using the [meeting template](../research/templates/meeting-note.md).

For the first two weeks, read before coding the controller. Thereafter, keep writing continuously: update methods as they are implemented and log experiment limits as they are discovered.

## Stop rules and fallback

- If no precise contribution survives the November topic gate, pivot while most of the schedule remains.
- If adaptive control cannot beat a credible static policy, investigate why and report the empirical result; do not weaken the baseline.
- If PX4 integration delays the core study, keep it a bounded case study or remove it with advisor agreement. It is not a prerequisite for a valid abstract comparison.
- If GNSS does not influence the selected decisions meaningfully, revisit the question within the team's intended GNSS/update/swarm intersection before changing domain.
- Freeze new features during April unless they fix a validity problem.
