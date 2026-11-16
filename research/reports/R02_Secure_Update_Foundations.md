# R02 - Secure update foundations and worked failure traces

- Task: [R02 / #2](https://github.com/mathissdupont/swarm-rejoin/issues/2)
- Date: 2026-11-10
- Follow-up: 2026-11-16, adding a mechanism/threat synthesis, explicit fallback/downgrade examples and the [verification-library assessment](R02_Verification_Library_Assessment.md)
- Preparation: source-based assisted draft for Samet Ünsal's research work. Handwritten notes were not supplied for transcription.
- Reading depth: the cited architecture, manifest, verification, recovery, and time passages were checked. This is not a claim of complete standards conformance, completed independent cross-review, or experimental validation.
- Prototype requirements: Samet approved the six choices recorded in [ADR 0002](../../docs/decisions/0002-update-mvp-requirements.md) on 2026-11-10. The target is the mission/coordination application, with staged verification, permitted fallback, and deferral when freshness evidence is insufficient.

## 1. Who prepares, authorizes, delivers, and verifies an update?

RFC 9019 separates several roles. The **author** creates the image. The **device operator** manages deployed devices and participates in deployment decisions. The **Trust Provisioning Authority** supplies trust anchors and authorization policies. The **firmware server** distributes artifacts, the **firmware consumer** obtains/processes them, and the **firmware verifier** checks an image before execution. Implementations can combine roles, but their responsibilities should remain explicit.

Authenticating a signer is an input to authorization: the device must also determine whether that signer is allowed to authorize this update for this target. A repository server delivering bytes does not automatically gain permission to authorize arbitrary software.

Evidence: [RFC 9019 archive](../library/rfc9019/README.md), sections 2-4 and 7; PDF pages 6-12 and 16. The specific division between our ground station, swarm coordinator, and onboard service remains a project decision.

## 2. What is a manifest and what does it contain?

A manifest is machine-readable metadata describing the update and how it applies. RFC 9019 section 6, Table 1, connects decisions to such information as trusted authorization, target identity, sequence state, dependencies, payload location, storage location, and installation instructions. [RFC 9124](../library/rfc9124/README.md) defines a richer information model, including monotonic sequence numbers, vendor/class identifiers, expiration, payload digests, size, signatures, and dependencies.

For our proposed companion-service update, a minimum candidate model would cover:

| Field | Why it is needed | Status |
| --- | --- | --- |
| Target/component identity | Prevent installation on the wrong device or component | Established mechanism; choose our encoding |
| Payload digest and size | Bind the authorized metadata to the exact complete bytes | Established mechanism |
| Signer and authorization policy | Determine which authority may approve the update | Established mechanism; provisioning is an assumption |
| Metadata sequence/freshness | Detect prohibited replay/regression under stated time/persistence assumptions | Established mechanism; select a concrete strategy |
| Protocol/role compatibility | Determine whether a software combination can perform a swarm role | Project contract requiring explicit definitions |
| Installation/recovery conditions | Define activation, failure, and permitted fallback behavior | Project lifecycle model informed by existing guidance |

This table is a proposed project model, not a claim that a JSON file with these fields implements SUIT or Uptane. See RFC 9019 section 6 / PDF page 15 and RFC 9124 sections 3.2-3.19 for source definitions.

The [2026-11-10 manifest discussion draft](../../docs/11-update-manifest-draft.md) develops the information groups, separates live evidence from release metadata, and records a possible TUF mapping and remaining decisions. It is not an approved schema or implemented verifier.

## 3. How do a digest, signature, and compatibility check differ?

A digest checks bytes against an expected value. If an attacker can replace both the image and an unauthenticated expected digest, that comparison alone does not establish authorization. A validated signature or another authorized integrity mechanism must protect the metadata that binds the digest to the intended target and policy.

A valid signature still does not establish correct parameters, absence of software defects, protocol compatibility, or the software currently running on a remote vehicle. [Uptane Standard 2.1.0](../library/uptane-standard/README.md) treats image verification and version reports separately. Its section 5.3.2 requires dependency/conflict consideration, while section 5.4.3.4 checks image targeting and consistency with metadata.

For our thesis, separate **artifact authorization**, **artifact-byte verification**, **running-state evidence**, and **mission-role eligibility**. Their assumptions and failure outcomes belong in the shared evidence contract.

## 4. Is an older signed release automatically acceptable or automatically forbidden?

Neither conclusion follows from its signature or display version alone. RFC 9124 section 3.2 describes a monotonic manifest sequence for enforcing the relevant authority's rollback policy. Uptane section 5.4.3.4 also checks image release-counter state. These mechanisms are not interchangeable with an arbitrary semantic version string.

Our model must distinguish the release identifier, authenticated metadata state, persistent security restrictions, and explicitly permitted recovery images. We have not yet selected an exact interoperable implementation. Recovery must not reset persistent security state merely to make a prohibited image acceptable.

Evidence: [RFC 9124](../library/rfc9124/README.md), section 3.2 / PDF page 8; [Uptane Standard](../library/uptane-standard/README.md), section 5.4.3.4 / PDF page 27. The proposed security-floor abstraction in our design is a project choice, not a new cryptographic primitive.

## 5. What should happen when an update fails?

RFC 9019 section 4 discusses recovery strategies such as multiple images or a recovery image. Uptane sections 5.4.3.3-5.4.3.6 discuss backup, installation preconditions, errors, and reporting. A failed operation must be reported accurately; downloading bytes is not equivalent to verified activation.

For the proposed staged updater, we intend to retain a usable authorized image while downloading a candidate, verify the complete candidate before activation, check its startup/health, and re-appraise role permissions after activation or fallback. This is a design requirement to implement and test. Actual atomicity and crash recovery depend on storage and boot mechanisms; documentation alone cannot guarantee them.

Evidence: [RFC 9019](../library/rfc9019/README.md), section 4 / PDF page 12; [Uptane Standard](../library/uptane-standard/README.md), sections 5.4.3.3-5.4.4 / PDF pages 26-28.

## 6. Why does GNSS time matter?

[Uptane Deployment Best Practices 2.1.0](../library/uptane-deployment/README.md), sections 3.1-3.1.1 / PDF pages 7-8, explains that an ahead clock can make current metadata appear expired, while a behind clock can enable stale metadata to appear current. It cautions against unsecured civilian GPS as the secure time source.

Thus GNSS position consistency and update-time trust must be evaluated separately. A fresh challenge helps bind a response to a session; it does not prove that a suppressed newer release does not exist. Under disconnection, the available trusted time, last accepted metadata, and offline bounds limit what we can conclude.

This interaction is an established concern, not our novelty claim. In addition, the same deployment guide already describes **location-based updates** in section 7.10 / PDF page 43, including checking a device's position before installation. Merely using location to influence an update is therefore too broad a contribution claim. Our candidate question still needs a precise swarm/navigation-integrity/recovery distinction and fair evaluation.

## 7. Worked trace A - interruption during candidate download

Designed example, not an executed experiment. Assumptions: the active release remains authorized and healthy, the inactive staging area is separate, and navigation-role evidence is initially current.

| Step | Event / evidence | Proposed required behavior |
| --- | --- | --- |
| 1 | UAV authenticates and reports the active release | Appraise software and navigation evidence separately |
| 2 | A new authorized, compatible update is offered | Verify metadata before using it to drive download/installation |
| 3 | Transfer stops before the authenticated full size/digest can be verified | Do not mark the candidate complete or activate it |
| 4 | The active image is still usable, but navigation evidence may have aged | Preserve only roles whose current prerequisites still hold |
| 5 | Transfer resumes or restarts | Recheck full bytes and metadata freshness before activation |
| 6 | Candidate activation and health checks finish | Collect new software/navigation evidence and issue a new role decision |

The implementation must test interruptions and persistent-state crash points. An authorized active image may still be ineligible for a role if navigation or compatibility conditions fail.

## 8. Worked trace B - valid signature with unreliable GNSS time

Designed example. Assumptions: an older metadata object has a valid authority signature, GNSS-derived time is biased backward, and its actual expiration is known to the independent evaluator.

| Step | Event / evidence | Proposed required behavior |
| --- | --- | --- |
| 1 | The old metadata is replayed | Signature verification alone must not finish acceptance |
| 2 | Position residuals look nominal, but clock trust is unresolved | Do not infer a trustworthy update clock from position consistency |
| 3 | An independent authenticated/bounded time reference shows expiration | Reject the candidate under the selected freshness policy |
| 4 | Alternatively, no sufficient time/reference evidence is available | Report an unknown freshness outcome and follow the explicit conservative update policy |
| 5 | A last authorized working image exists | Consider continued limited service only if its independent role prerequisites hold |

A nonce does not resolve release freshness during indefinite isolation. The exact offline policy and resulting service loss are research/modeling decisions, not fixed results supplied by the standards.

## 9. Mechanism/threat synthesis

This table is the section-cited R02 mechanism/threat deliverable. Standard mechanisms and project-specific conditions are distinguished; it is not experimental evidence.

| Threat or failure | Mechanism and evidence | Project consequence / remaining boundary |
| --- | --- | --- |
| Unauthorized update | RFC 9019 sections 2-3; TUF sections 2.1 and 4.3 define authority/trust-role responsibilities | Provision trusted keys and component/target authority; an authenticated device identity is not release authorization |
| Changed or incomplete payload | RFC 9124 sections 3.13-3.15; TUF sections 4.5 and 5.7 bind target size/hashes to authenticated metadata | Never activate partial or mismatching bytes; protect them between verification and use |
| Wrong device or incompatible component | RFC 9124 sections 3.3-3.6/3.11; Uptane section 5.3.2 considers dependencies/conflicts | Target matching and the exact swarm-role/protocol contract are separate checks |
| Replay or metadata regression | RFC 9124 sections 3.2 and 4.3.1; TUF sections 5.4-5.6 check trusted metadata state and expiration | Persist applicable metadata state; do not sort application labels as an anti-rollback policy |
| Faulty clock or freeze during isolation | Uptane Deployment sections 3.1-3.1.1 | Use sufficient independent freshness evidence or defer; counters/nonces do not prove that no newer release is withheld |
| Interrupted transfer or failed installation | RFC 9019 section 4; Uptane sections 5.4.3.3-5.4.3.6 | Separate staging, activation and reported outcome; retain only an authorized usable fallback |
| Recovery reintroduces prohibited bytes | Uptane section 5.4.3.4 checks release counters; the project's security floor is a separate abstraction | Recovery cannot reset security state or override current authorization; application-data compatibility must also hold |
| Old evidence after restart | RFC 9334 sections 7.4, 10 and 12 distinguish trustworthy evidence and its freshness context | Session/boot/age binding and fresh software/navigation appraisal remain D01 design obligations |
| Mission pressure overrides security | Project threat-model invariant I7 and ADR 0002 | Utility is optimized only among admissible actions; report a service shortfall when none is feasible |

Full source records: [RFC 9019](../library/rfc9019/README.md), [RFC 9124](../library/rfc9124/README.md), [RFC 9334](../library/rfc9334/README.md), [TUF](../library/tuf-spec/README.md), [Uptane Standard](../library/uptane-standard/README.md), [Uptane Deployment](../library/uptane-deployment/README.md). Selected cited passages were checked; these are not full-conformance reviews.

## 10. Authorized fallback versus prohibited downgrade

These are designed examples with hypothetical labels and counters, not observed runs. Assume landed/disarmed activation, protected persistent state and current authenticated authorization.

| State/event | Authorized fallback example | Prohibited downgrade example |
| --- | --- | --- |
| Persistent restriction | Security floor is 2 | Security floor is 3 |
| Candidate failure | Release B, epoch 2, fails health | Release B, epoch 3, fails health |
| Available old image | Release A, epoch 2, exact bytes verified; still authorized as a recovery image; its application data remains usable | Release A, epoch 2, has a valid old signature but is below the current floor |
| Decision | A can be attempted under the recovery/operational contract; metadata state and the security floor are preserved | A cannot be used; another authorized recovery image meeting floor 3 is needed |
| Mission outcome | Reappraise health and current navigation/role evidence before any mission permission | If no permitted usable image exists, keep mission isolation; do not lower the floor to regain service |

In the first case, use current authorization that permits A, not an arbitrary old metadata object merely because it was signed once. Application-data restoration must not restore old security counters or trust state. These examples complete the conceptual distinction; exact crash-safe commit behavior is later D02 work.

## 11. Research disposition and follow-up

- The mission/coordination application target and six prototype behaviors are accepted in ADR 0002. The [2026-11-16 desk assessment](R02_Verification_Library_Assessment.md) recommends Python-TUF as the first verification reference and records fit/limits. No project signature-verification code exists.
- [ADR 0003](../../docs/decisions/0003-companion-deployment-and-ground-activation.md) accepts an onboard Linux companion target with ground-only activation/application-restart recovery. Python-TUF remains an evaluation candidate; hardware suitability and implementation timing are unmeasured.
- R02's source-based requirements, mechanism/threat table, failure traces, fallback/downgrade distinction, time limitations and reference-library assessment are available for cross-review. Numerical budgets, an executable schema and behavioral tests are D01/D02 or later implementation work; they are not claimed complete here.
- Specify provisioning, persistence, freshness/time bounds, role compatibility, and permitted recovery in the subsequent contract.
- Match the navigation evidence described in [R03](R03_GNSS_IMU_Integrity_Research_Report.md) to activation and re-admission events.
- Cross-review the source interpretations and both traces with Ceren/Halil.
- Validate failures in code and simulation before making security, timing, or mission-performance claims.

This artifact answers the first reading questions and starts the mechanism/failure-trace deliverable. It does not close R02, establish an original contribution, or assert that Samet's independent handwritten work was reproduced.
