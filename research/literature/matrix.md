# Literature matrix

Updated on 2026-11-16. The registry contains **22 references**: the initial 16, four sources from the R03 follow-up, and two official library references for R02. Reading depth differs by source; this count is not a completed-review count or a systematic-review inclusion count. `Unknown` means unexamined, not absent.

Metadata, access details, and proposed leads are in [sources.json](sources.json); citation records are in [references.bib](references.bib).

Full-text/PDF storage and acquisition gaps are indexed separately in the [source library](../library/README.md), established 2026-11-10. A later capture does not retroactively change the reading depth recorded in this matrix.

| ID | Type / reviewed material | Directly supported relevance | Still to check |
| --- | --- | --- | --- |
| `dong2026` | Journal; abstract and retrieved reconnection sections | Reconnection includes identity, program integrity, and task-behavior checks | GNSS confidence, update lifecycle/recovery, version dependencies, role decisions, exact trust assumptions |
| `usman2026` | Journal; selected full-text architecture, implementation and limitation passages | Attestation/update integration, A/B recovery and an explicit rollback-attack limitation | Full protocol/experiment review; exact navigation/team coverage and matched assurance assumptions |
| `yaacoub2023` | Journal; selected full-text target/update-model/limitation passages | Scheduler-dependent idle-time scheduling; evaluation models update duration rather than applying an actual update | Full algorithm/proof/experiment review and matched comparison to ground-only companion updates |
| `kuppusamy2018` | Journal; publisher abstract/metadata | Compromise-resilient vehicle update framework | Mechanisms and experiments in the full article; distinguish article from normative specification |
| `tuf-spec` | Official specification; version and overview | Secure update reference, observed version 1.0.37 | Exact expiration, metadata consistency, rollback, and key-rotation requirements for any reused implementation |
| `uptane-standard` | Official versioned specification; selected passages | Vehicle update procedures and secure time requirements | Target/role compatibility mapping, offline behavior, recovery details, and full conformance obligations |
| `rfc9019` | Informational RFC; selected architecture passages | Update architecture and actors; transport-independent manifest concept | Detailed deployment constraints and how to adapt without claiming conformance |
| `rfc9124` | Informational RFC; abstract/element outline | Manifest information model includes sequence, targeting, digests, dependencies and expiration | Exact semantics relevant to the MVP, including safe recovery authorizations |
| `rfc9334` | Informational RFC; vocabulary passages | Separates attester, verifier, relying party and appraisal | What trust anchor could support running-state evidence in this project |
| `nist193` | Technical guideline; official abstract | Firmware resiliency framed around protection, detection and recovery | Requirements applicable beyond the abstract; hardware/platform limitations |
| `tanil2016` | Conference paper; publisher abstract | INS/GNSS innovation-based spoofing monitoring | Full access, estimator assumptions, false-alarm behavior, and transfer limits from aircraft approaches to small UAV scenarios |
| `px4-multi` | Official guide; selected passages | Multi-vehicle simulation starting point | Tested environment, pinned revision, resource use, and chosen integration interfaces |
| `mavlink-signing` | Official guide; selected passages | Message authentication mechanism to inspect during integration | Actual support/configuration in the chosen stack; it does not replace artifact or runtime checks |
| `uptane-deployment` | Official versioned guide; section 3.1 | Discusses secure-time requirements, ahead/behind clocks, and risks of civilian GPS time | Applicability to bounded swarm disconnections and exact policy comparison |
| `yan2020` | Journal; institutional indexed abstract | Cooperative-localization measurement scheduling under resource constraints | Full algorithm, estimator assumptions, and relevance to software-update scheduling; direct open was rate-limited |
| `galileo-faq` | Official FAQ; selected passages | Distinguishes OSNMA navigation-data authentication from full PVT authentication | Receiver requirements and feasibility; no receiver implementation is implied |
| `maharmeh2025` | Survey; selected supplied-PDF passages and metadata | Supports R03's error taxonomy and separation of monitoring from error bounds | Full review and original-method follow-up remain pending |
| `boguspayev2023` | Survey; selected supplied-PDF integration passages | Supports loose/tight measurement-interface background; detailed deep-coupling treatment is excluded | No demonstrated optimality of the proposed UAV estimator |
| `alipour2026` | Survey; selected publisher/PDF passages | Supports the estimator/map/sensor taxonomy | No validation of a secure-update or swarm-rejoining policy |
| `tanil2018` | Original journal method; metadata and indexed abstract | Tightly coupled innovation monitoring in an aircraft example | Exact detector/window parameters and original equations remain unverified; candidate PDF fetch failed |

| `python-tuf` | Official v7.0.1 README/API and selected source | Native TUF client workflow, bootstrap trust, metadata verification and verified target download | GNSS-independent time integration, installer/recovery behavior and target-board feasibility remain untested |
| `cryptography-ed25519` | Official 50.0.2 sign/verify passages and upstream RST | Signature primitive API, not a complete updater | Authorization/freshness/persistence/installation policies would still need a separate design |

The [R03 review](../reviews/2026-11-01-r03-review.md) records what was checked and what still blocks scientific acceptance. Survey availability and automatic transcription do not complete the primary-method reading requirement.

## Current interpretation

Reconnection with integrity checks, secure software updating, and robot update scheduling all have prior work. That observation does not settle whether **GNSS-aware secure update and rejoining decisions in a swarm** can support a useful contribution. Compare exact assumptions and operations before making the claim.

The evidence base is currently uneven: navigation/swarm-specific secure-update studies need further targeted search. Do not treat the larger number of update references as evidence that GNSS is secondary. Every retained candidate must preserve the team's three-area scope.

## Feature comparison to complete

For the nearest studies, add section-level evidence for: navigation integrity/age, GNSS time, update authenticity, running-state assurance, release compatibility, interrupted activation, permitted recovery, mission role restrictions, team capacity, and reproducibility. Do not fill this table with binary "no" entries based only on abstracts.
