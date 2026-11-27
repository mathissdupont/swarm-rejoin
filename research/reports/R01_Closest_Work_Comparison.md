# R01: Claim-to-evidence comparison of the starting nearest work

- Date: 2026-11-27
- Task: [#1](https://github.com/mathissdupont/swarm-rejoin/issues/1)
- Preparation: assisted author-stage comparison for Samet Ünsal; no collective review or absence/novelty finding

| Comparison property | Dong et al., 2026 | RASUES / Usman et al., 2026 | NeRTA / El Yaacoub et al., 2023 |
| --- | --- | --- | --- |
| Source access/review | [Retrieved passages only](../literature/notes/dong2026.md); complete-text acquisition unresolved | [Comparative desk review](../literature/notes/usman2026.md), main text and Appendix A; selected original figures/pages inspected | [Selected method/limitation passages](../literature/notes/yaacoub2023.md); full algorithm/evaluation review pending |
| Identity and update authority | Reconnection passages include identity and program checks; exact update authority unresolved | Sections 3-4 distinguish trusted verifier/reference-value provider and software-update processing | Related work discusses secure OTA; the exact authorization mechanism is not established by our reviewed subset |
| Exact software bytes versus runtime evidence | Retrieved program integrity/test-task overlap is material, but full protocol details remain unknown | Sections 4-5 / Figure 4 connect update processing, expected measurements and attestation/appraisal under an intact measurement-environment assumption | Section 3.2 assumes valid update stages with known timing; actual byte verification is not the studied timing result |
| Recovery and security rollback | Unknown from the limited source access | Sections 5.2/7/8 distinguish described A/B recovery and stated rollback/check-use limitations | Complete recovery coverage is unknown; section 8 states the evaluated update is a modeled-duration task |
| Navigation and swarm role contract | Unknown; do not claim prior rejoining is identity-only | The reviewed protocol does not specify our proposed navigation-evidence/mission-role contract; no global absence claim follows | Target/update assumptions differ from ground-only companion recovery; navigation/team coverage outside the checked passages remains unknown |
| Quantitative comparator fit | Unresolved until full assumptions can be matched | One trusted-hardware attester and protocol-operation measurements are not the same as our swarm mission experiment | Low-level scheduler properties require release-time/update-duration assumptions that an arbitrary Linux process does not inherit |

## Consequence for the proposed question

No source supports claiming that signatures, attestation plus updates, A/B recovery, or scheduling robot updates are our new mechanisms. The precise candidate is an empirical comparison of software-transaction and navigation-evidence effects on role-eligible service under the same trust and operational constraints. Use B3 as the main static comparator with the same inputs and security/recovery options; identity-only policies remain contextual.

The additional [navigation reintegration overlap](../literature/notes/aljaafreh2026.md) further rules out treating generic GNSS quarantine/re-entry as a new contribution. Sensor-source reintegration, application recovery and swarm-member role admission must be modeled separately.

## Acceptance status

Samet's RASUES reading artifact is delivered at comparative desk-review depth, with no replicated security/performance result. R01 as a whole remains incomplete: Dong access, NeRTA's full review, backward/forward checking of relevant neighboring work and another-author source review remain explicit. This comparison does not complete three independent primary readings or mark absent features on the basis of abstract silence.

## Additional swarm-specific overlap found on 2026-11-27

The comparison must also include [Varadharajan et al.](../literature/notes/varadharajan2018.md), [RobOTAP](../literature/notes/robotap2024.md) and the selected [OpenSwarm report](../literature/notes/openswarm-d24.md); general swarm updating/integrity admission cannot stand as our contribution. Their access/reading limits remain explicit. The [new gate](../../docs/12-contribution-and-decision-gate.md) narrows the comparison to application/producer evidence dependencies and role re-admission. A complete assumption-matched comparison and independent review remain pending.
