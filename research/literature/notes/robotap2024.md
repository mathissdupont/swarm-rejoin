# Selected-source note: Abadie et al. / RobOTAP (2024)

- Source: `robotap2024`, [HAL v1](https://inria.hal.science/hal-04581750v1), [archived PDF/Markdown and provenance](../../library/robotap2024/README.md).
- Access: 2026-11-27; HAL seven-page file including archive cover. Selected sections III-IV and VI read; original cover and PDF page 4 visually checked. No full-review flag or replicated measurements.

| Evidence | Supported observation | Implication |
| --- | --- | --- |
| III.B-C, Figures 2-4, PDF pages 4-5 | Inactive-partition transfer, signed metadata, chunk acknowledgments, final hash check and controlled reboot | Authenticated swarm updates are existing work; release bytes and application role fitness remain separate properties |
| IV, PDF page 6 | SHA-256 and Ed25519; verification key provisioned into firmware | Do not claim the signature mechanism as our contribution |
| V, PDF pages 6-7, inspected setup only | MCU/controller update timing context | Neither measurements nor hardware acceleration results calibrate a Linux companion app |
| VI, PDF page 7 | Watchdog/trusted-backup recovery described as planned extension | Do not present that extension as demonstrated recovery |

The examined protocol does not establish our proposed application/producer/frame/role contract. That statement describes the checked material, not proof of a gap across related work. Check later DotBot/OpenSwarm developments before asserting a missing recovery capability. Source code and security properties have not been independently audited or reproduced.

HAL cover explicitly states CC BY 4.0. Full capture is an archive fact, not completion of the paper review.
