# Comparative reading note: Usman et al. (2026)

Source ID: `usman2026`. [Publisher page](https://link.springer.com/article/10.1007/s10207-026-01233-1).

Last checked: **2026-11-16**. Reading depth: selected complete-text passages in sections 3/3.1, 5.1-5.5, 6.1, 7 and 8-9, using the [archived original and text capture](../../library/usman2026/README.md). This is an assisted source-based note, not a complete paper review or a Ceren/Halil cross-review. Figures and equations have not been independently validated.

## Observed overlap

RASUES integrates remote attestation and updates, accounting for expected states before and after updating, with a TPM-based prototype described in the abstract.

## Section-specific comparison

| Topic | Observed evidence | Consequence for SWARM-REJOIN |
| --- | --- | --- |
| Trust boundary | Section 3.1 / PDF page 5 assumes an intact secure attestation environment while allowing attacks on other device software | Our simulated trusted measurement agent is a different assurance level; signatures cannot substitute for their measurement environment |
| Update and measurement integration | Section 5 / PDF pages 7-8 combines CHARRA, SWUpdate and Linux IMA; section 5.3 discusses changed reference measurements | Combining updates and before/after software-state evidence is established work, not our novelty claim |
| Recovery | Section 5.2 / PDF page 8 describes dual-copy A/B updating and its storage requirement | Permitted fallback is a reused mechanism; we must separately model authorization and mission-role effects |
| Prototype context | Sections 5.5-6.1 / PDF pages 9-10 use a Raspberry Pi/TPM attester; section 6.1's evaluated update does not require rebooting the attester | This supports investigating an embedded Linux application target, but their reported timing cannot be transferred to our unspecified board or update |
| Rollback boundary | Section 7 / PDF page 14 explicitly states that rollback attacks are not prevented and also discusses dual-copy recovery | Treat security rollback restrictions and working-image recovery as separate obligations; A/B alone does not establish our anti-downgrade requirement |
| Measurement limitation | Section 7 / PDF page 14 notes that compromising kernel-level IMA would break the approach | Do not claim that any reported application hash establishes uncompromised runtime state |

Section 5.4 / PDF page 9 states that the current prototype does not support the proposed authenticated watchdog functionality because of the TPM module. A later platform paragraph discusses the watchdog in general terms. Keep the conceptual mechanism and demonstrated prototype support distinct; the exact extent of watchdog validation needs clarification before using it as a comparator.

## Comparator fit and remaining questions

RASUES is a close architectural/security reference, not yet a runnable baseline for our GNSS-aware swarm policy. Matching its trusted attestation environment, update target, reference-state management and fault assumptions would be required for a quantitative security comparison. We should compare against the same secure update/measurement assumptions in B3 and P rather than give only P stronger evidence.

The checked passages do not settle whether the entire work covers navigation-integrity-based role eligibility or swarm mission capacity. Those properties remain **unknown**, not absent. Complete the protocol/analysis reading and inspect the paper's own referenced neighboring schemes before asserting a narrow gap. No numerical result from this paper has been reproduced here.
