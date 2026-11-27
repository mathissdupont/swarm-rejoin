# Comparative reading note: Usman et al. (2026)

Source ID: `usman2026`. [Publisher page](https://link.springer.com/article/10.1007/s10207-026-01233-1).

Last checked: **2026-11-27**. Reading depth: comparative desk reading of the article's main text, sections 1-9 and Appendix A, using the [archived original and text capture](../../library/usman2026/README.md). The protocol figure on PDF page 7, evaluation figures/table on page 11 and limitations on page 14 were inspected in the original rendered PDF. This is an assisted author-stage paper review for Samet Ünsal; experiments, proofs and software were not reproduced, and no Ceren/Halil cross-review is claimed. Bibliographic entries are leads, not independently verified evidence about every cited scheme.

Inclusion: retain as a nearest update/attestation/recovery study for R01 and R10/T5. Reviewed version: published article, International Journal of Information Security 25:75, 18 PDF pages, DOI above; file identity/provenance is recorded in the archive.

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

## Question, method and evaluation quality

The paper's concrete question is how to connect software update processing and changed expected measurements to a RATS-style attestation/appraisal workflow. Section 4 and Figure 4 divide this into update, remote attestation and appraisal. Its trusted reference-value provider and verifier are not equivalent to trusting an arbitrary device's update self-report. The intact attestation environment and the IMA/kernel assumptions materially constrain the security interpretation.

Section 6.1 / PDF page 10 describes one Raspberry Pi attester and virtualized supporting entities, with a no-reboot update in the evaluated scenario. Figure 8 reports 20 iterations; Figure 9 / page 12 reports a separate comparison over 50 iterations. These are protocol-operation observations, not independent swarm missions. Section 6.2 explicitly reports added latency relative to CHARRA due to the extra measurement work. No paper latency is imported as our updater duration or as evidence of superiority under our mission assumptions.

Section 7 is a structured threat analysis based on the protocol sequence, not a completed formal security proof; section 8 identifies formal verification as future work. The appendix gives SWUpdate packaging/measurement examples and a hardware setup, but these were not executed here. Raw-data availability and prototype completeness must be checked before any numerical reproduction; the declarations say no datasets were generated or analysed, which does not by itself supply an experiment archive.

## Critical findings and our comparison boundary

1. A nonce establishes a session-related freshness property, not knowledge of the newest authorized software release. A before/after expected-state comparison is not a generic anti-downgrade policy.
2. The page-14 rollback limitation is explicit. Its accompanying discussion of A/B recovery must not be interpreted as proving protection against prohibited rollback.
3. Section 8 / page 14 identifies a check/use attack and proposes an integrity-key mechanism as future work. Broad atomicity language elsewhere in the paper must be read with that stated limit; our own design still needs to protect verified bytes and state until use.
4. The watchdog is part of the conceptual recovery flow, while section 5.4 states the particular prototype module does not implement it. Treat those as different evidence levels.
5. Authenticating the application state does not directly establish whether navigation uncertainty, evidence age or current mission requirements allow a swarm role. The reviewed protocol does not specify our proposed role/evidence contract; this observation is not a global claim that no related work addresses it.

The resulting candidate difference is a bounded empirical question about role service after authorized recovery under a shared security model. It is not a claim to invent updates plus attestation or hardware-backed recovery. A fair B3/P comparison must share software evidence assumptions and recovery options. The next acceptance step for this note is another author's source/claim review; no disagreement or approval has yet been recorded.
