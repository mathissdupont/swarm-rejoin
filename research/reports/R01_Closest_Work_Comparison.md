# R01: Claim-to-evidence comparison of the starting nearest work

- Initial comparison: 2026-11-27; evidence update: 2026-11-28
- Task: [#1](https://github.com/mathissdupont/swarm-rejoin/issues/1)
- Preparation: initial assisted author-stage comparison for Samet Ünsal, followed by Halil Abacı's assisted Dong/NeRTA evidence pass. Independent team review remains pending.

| Comparison property | Dong et al., 2026 | RASUES / Usman et al., 2026 | NeRTA / El Yaacoub et al., 2023 |
| --- | --- | --- | --- |
| Source access/review | [Contributor-supplied pre-proof](../literature/notes/dong2026.md); §§4, 6 and selected §8 evidence and publisher figures checked | [Comparative desk review](../literature/notes/usman2026.md), main text and Appendix A; selected original figures/pages inspected | [Published article](../literature/notes/yaacoub2023.md); §§3–8 method/evaluation evidence checked, including original idle-time plot |
| Identity and update authority | §6.2.1 verifies membership identity; cluster key updates are separate from software release authorization | §§3–4 distinguish trusted verifier/reference-value provider and software-update processing | §3.2 models update timing under assumed valid stages; release authorization is outside this timing evidence |
| Exact software bytes versus runtime evidence | §6.2.2 compares a reported program hash with a reference; equivalence to hardware-backed running-state evidence remains unestablished | §§4–5 and Figure 4 connect update processing, expected measurements and attestation under an intact measurement environment | §3.2 assumes valid update stages with known timing; byte verification is outside the studied scheduling result |
| Recovery and security rollback | §8 and Table 3 describe preserving task data on disconnection; authorized software fallback remains unestablished by the sections examined | §§5.2, 7 and 8 distinguish described A/B recovery and stated rollback/check-use limitations | §8 reports modeled update work in the evaluation; operational recovery remains outside that evidence |
| Navigation and swarm role contract | §6.3 checks a GPS-activation and camera command example. It establishes protocol compliance; quantitative navigation readiness for a role remains unestablished. | Reviewed protocol gives results to a relying party; our navigation-evidence/mission-role contract is a separate research proposal | §5.2 uses speed for Bounded Reactive Control and discusses GPS-based configuration selection; the checked method does not establish quantitative navigation integrity for role admission |
| Quantitative comparator fit | §6 provides a direct reconnection comparison; §8/Figure 8 evaluates stored task results. Match trust and cluster-disconnection assumptions before comparing role outcomes. | One trusted-hardware attester and protocol-operation measurements differ from the proposed swarm mission experiment | §7.1 timing observations and §8 update abstractions require matching release times, update-duration bounds and target system before a direct comparison |

## Consequence for the proposed question

No source supports claiming that signatures, attestation plus updates, A/B recovery, or scheduling robot updates are our new mechanisms. The precise candidate is an empirical comparison of software-transaction and navigation-evidence effects on role-eligible service under the same trust and operational constraints. Use B3 as the main static comparator with the same inputs and security/recovery options; identity-only policies remain contextual.

The additional [navigation reintegration overlap](../literature/notes/aljaafreh2026.md) further rules out treating generic GNSS quarantine/re-entry as a new contribution. Sensor-source reintegration, application recovery and swarm-member role admission must be modeled separately.

## Acceptance status

Samet's RASUES review remains the existing comparative desk artifact. The 28 November pass adds evidence from Dong's supplied pre-proof and expands NeRTA's checked method and evaluation. The Dong edition is available for reading outside Git; redistribution of a corresponding full-text capture remains unconfirmed. R01 remains open for additional assumption and neighboring-work checks and independent review of the source claims. No experiment or proof was reproduced.

## Additional swarm-specific overlap found on 2026-11-27

The comparison must also include [Varadharajan et al.](../literature/notes/varadharajan2018.md), [RobOTAP](../literature/notes/robotap2024.md) and the selected [OpenSwarm report](../literature/notes/openswarm-d24.md); general swarm updating/integrity admission cannot stand as our contribution. Their access/reading limits remain explicit. The [new gate](../../docs/12-contribution-and-decision-gate.md) narrows the comparison to application/producer evidence dependencies and role re-admission. A complete assumption-matched comparison and independent review remain pending.
