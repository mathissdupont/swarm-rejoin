# R02 - Secure update foundations and worked failure traces

- Task: [R02 / #2](https://github.com/mathissdupont/swarm-rejoin/issues/2)
- Date: 2026-11-10
- Preparation: source-based assisted draft for Samet Ünsal's research work. Handwritten notes were not supplied for transcription.
- Reading depth: the cited architecture, manifest, verification, recovery, and time passages were checked. This is not a claim of complete standards conformance, completed independent cross-review, or experimental validation.

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

## 9. What remains open for R02?

- Choose the exact update target and maintained verification implementation; no signature-verification code exists yet.
- Specify provisioning, persistence, freshness/time bounds, role compatibility, and permitted recovery in an executable contract.
- Match the navigation evidence described in [R03](R03_GNSS_IMU_Integrity_Research_Report.md) to activation and re-admission events.
- Cross-review the source interpretations and both traces with Ceren/Halil.
- Validate failures in code and simulation before making security, timing, or mission-performance claims.

This artifact answers the first reading questions and starts the mechanism/failure-trace deliverable. It does not close R02, establish an original contribution, or assert that Samet's independent handwritten work was reproduced.
