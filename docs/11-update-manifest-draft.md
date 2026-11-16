# Update manifest: information model for discussion

- Date: 2026-11-10
- Status: Proposed information model; no final schema, signing format, verifier, or team approval
- Scope: The mission/coordination application under [ADR 0002](decisions/0002-update-mvp-requirements.md) and the Linux companion/ground-only activation boundary in [ADR 0003](decisions/0003-companion-deployment-and-ground-activation.md)
- Reading depth: Selected RFC 9124, TUF specification and Uptane Standard passages listed below; no complete conformance review or implementation test

## 1. What this manifest describes

The update manifest binds an authorized release description to the exact application artifact and its applicability conditions. It is separate from [research/library/manifest.json](../research/library/manifest.json), which catalogs archived research sources and is not an update authorization object.

The release authority publishes protected metadata. An artifact repository transports bytes. The onboard updater checks both metadata and the complete artifact; the evidence appraiser and mission controller separately assess running state and role eligibility. A release label, a download URL, or an unprotected checksum does not establish update authorization.

## 2. Proposed information groups

These are project requirements to discuss, not RFC field names or a committed wire format. All release-specific values affecting acceptance must be authenticated, either directly in signed metadata or through an authenticated digest binding to another object.

| Information | Proposed representation | Consumer and purpose |
| --- | --- | --- |
| Format/profile | A recognized profile identifier/version | Parser: determine supported semantics; unknown required semantics cannot silently pass |
| Authority and signatures | Framework signature envelope plus provisioned authorization policy | Verifier: establish whether a trusted key has authority for this component/target; a claimed signer ID alone grants nothing |
| Component and target | Component ID, device/platform class and required OS/architecture profile | Updater: compare against trusted local inventory; a valid release for another class is not applicable |
| Artifact binding | Artifact identifier/path, format, full byte length, cryptographic digest and algorithm | Downloader/verifier: obtain and bound the exact complete bytes before activation |
| Application release | Release identifier such as a version label | Inventory/reporting: identify the application release; not a freshness or anti-rollback proof |
| Metadata freshness | Framework-defined metadata versions/sequences and expiration | Metadata verifier: check against trusted time and persisted metadata state; details depend on the selected framework |
| Persistent security restrictions | Proposed release security epoch plus separately protected local floor and current authorization | Updater/recovery manager: block prohibited images; commit/recovery rules remain to be specified under D02 |
| Compatibility | Exact supported swarm-protocol IDs and required platform/dependency profile | Appraiser: compare declared requirements with the current mission and installed dependencies; do not infer compatibility from a higher version label |
| Activation, health and recovery profiles | References to recognized, versioned or digest-bound profiles | Lifecycle manager: select defined checks and permitted recovery; references cannot weaken local mandatory constraints |

Profile definitions must be available and trusted before use. Unknown mandatory profiles defer/reject the candidate as specified by the eventual contract. A signed arbitrary shell command or installation path is not part of this proposal; the local installer maps allowed components and formats to controlled operations.

The target class identifies eligible deployments; it need not be a unique UAV ID. Per-device rollout permission, if needed, belongs in a separately defined authenticated assignment bound to the artifact/device. That assignment is not defined here.

### 2.1. Operational details to resolve beyond the basic fields

The following expands the proposed information model. Field names are illustrative, and the priorities are recommendations, not accepted schema decisions or implemented features. A profile may group several requirements if its exact trusted definition is available; every detail need not become a top-level field.

| Detail and illustrative fields | Proposed priority | Semantics to define |
| --- | --- | --- |
| Runtime and dependencies: `platform_profile_id`, `dependencies`, `conflicts` | Define for v1 | Identify OS/architecture/runtime ABI and required component combinations. Bind dependency artifacts or their trusted immutable profiles; a display version or an unpinned online dependency install is insufficient. In the initial full-package proposal, carry application dependencies in the verified package where feasible and declare remaining platform requirements |
| Allowed starting state: `precondition_profile_id`, optional `accepted_base_digests` | Define applicability for v1; exact base digest conditional | State which installed application/configuration states permit this transition. A full replacement does not automatically require one base image. If a transition requires a specific base, authenticate that requirement and compare it with trusted local measurements |
| Package and installer: `artifact.format`, `installer_profile_id` | Define for v1 | Select a recognized package format and locally controlled staging/activation procedure. Bind the component to its allowed installation area; a publisher-supplied filesystem path or shell string cannot choose arbitrary privileged operations |
| Unpacking and space: `max_unpacked_bytes`, resource/profile reference | Define for v1 if extraction is used | Distinguish transferred bytes from the extraction bound. The updater enforces its own limits and checks space for staging, temporary data, retained fallback and any application-data snapshot. Actual free space is live device state, not a release claim |
| Configuration and application data: `data_profile_id`, conditional `migration_profile_id` | Define the v1 data contract; migration conditional | Specify accepted input/output data schemas and fallback readability. A working old binary is not a usable fallback if a migration made its configuration unreadable. Proposed v1 default: no incompatible persistent-data migration; unsupported transitions are deferred |
| Startup/health: `health_profile_id` | Define for v1 | Specify expected application identity, protocol handshake/self-test, observation window, timeout, success/commit condition and failure action. Profile parameters need justified bounds; the application merely sending a heartbeat is not the complete mission-health criterion |
| Recovery: `recovery_profile_id` and authenticated recovery-image references | Define for v1 | Bind eligible fallback bytes and their authorization; require compatible application data and the existing ground-only boundary. A Boolean `rollback_allowed` cannot override authorization or the local security floor |
| Updater capabilities: required feature/profile identifiers | Define for v1 | The updater must understand every mandatory feature before any state-changing operation. An old updater must not silently ignore a new mandatory dependency, migration, or security rule |

Dependency requirements and their verification are distinct: signed declarations do not prove that a runtime or a particular dependency is actually installed. Define the inventory/measurement source and check dependency/conflict consistency. Reject unsupported dependency cycles or transition combinations under the selected installer contract rather than guessing an order.

Delta patches are a possible later extension, not a v1 recommendation. If introduced, separately authenticate the base-image digest, patch format/bytes and reconstructed-result digest, with verification before activation. Hashing only the downloaded patch does not identify the resulting installed application.

### 2.2. Release metadata, rollout assignment and local state

| Object | Information that belongs there | Boundary |
| --- | --- | --- |
| Immutable release description | Artifact binding, target/component, applicability, compatibility and lifecycle-profile references | Shared description of the same release; signed directly or authenticated through a signed digest |
| Authenticated rollout assignment, if needed | Exact release binding, authorized target devices/cohort, mission/configuration binding, rollout window and coordinator-policy version | Separate deployment authorization; its authority must be provisioned and cannot broaden release or device-local permissions. A new assignment cannot make expired release metadata or a prohibited image acceptable |
| Trusted device policy/state and transaction journal | Trust anchors, highest trusted metadata state, security floor, active/fallback artifact identities, pending operation, last durable step, attempt limits and actual health results | Persist and recover under D02; downloading signed metadata does not replace the local trust store or reset the security floor |
| Runtime mission/navigation evidence | Current observations, source/session binding, age and appraised role eligibility | Evaluated separately under D01; an assignment cannot assert a truthful current GNSS score or landed state |

A single-device transaction journal and any application-data snapshot serve different purposes. Restoring application data must never restore old security counters, revoked keys or prohibited authorization state. Define crash recovery at each durable write; placing a `transaction_id` in metadata does not make installation atomic.

Fleet rollout rules such as limiting simultaneous unavailable vehicles belong in the coordinator policy/assignment, not a universal property of the release package. Mission capability, transfer budgets and safe activation conditions are still enforced locally and by the controller under the same hard constraints.

### 2.3. A usable schema also needs processing rules

- Specify required, conditional and optional fields, their exact types and units. For example, byte counts are bounded integers; timeout units must be explicit; numeric security counters cannot wrap. Version labels are identifiers unless an explicit comparator is selected.
- Choose the signature envelope/serialization with the verification framework. Do not independently invent canonical JSON rules or guess which whitespace/encoding is signed.
- Define bounds on metadata size, nesting, arrays and strings before expensive processing. Reject ambiguous duplicate keys and malformed values using the selected parser/format contract.
- Distinguish an absent optional value from an unknown required value. A required digest, target, compatibility or trusted profile cannot default to permissive behavior; the teaching example's `null` values are not acceptable production values.
- Separate harmless extension data from required semantics. Preserve and authenticate framework extensions as its specification requires; unknown mandatory project features cannot be ignored. Do not impose a blanket rule that contradicts TUF's handling of additional authenticated fields.
- Recheck that the bytes/profile/state used for activation are the ones verified. Define protection against replacement between checking and use, along with activation-time freshness revalidation after staging.
- Return explicit outcomes/reasons such as invalid metadata, unsupported profile, incompatible transition, insufficient evidence, deferred activation, failed health and no authorized recovery. An update status is not a mission-admission decision.

An SBOM/provenance reference, operator release notes, encrypted payloads and staged fleet cohorts can be useful extensions. They are not all mandatory for this MVP, and no such field proves that the code is benign or the device uncompromised. Add them when a stated threat, deployment need or experiment uses them.

## 3. Three version concepts that must stay separate

1. **Application release ID:** identifies application bytes. String ordering is not a security policy.
2. **Metadata version/sequence:** orders authenticated metadata within its defined scope; persist the relevant framework state. It is not one universal counter shared by every component and signing role.
3. **Security epoch/floor:** a proposed project rule for which releases remain eligible. A lower release label can be a permitted fallback only if current authorization, the persistent floor, compatibility, and health all allow it.

An authority may reauthorize older application bytes using newer metadata, subject to current security restrictions. A counter cannot prove that no newer metadata has been withheld. Advancing a security floor also needs a crash-safe, authorized recovery strategy; a field in the manifest cannot provide that strategy by itself.

Metadata expiration governs using that metadata for the defined update operation. It does not automatically terminate an already running application or authorize indefinite continued service. Active-service eligibility and any offline authorization limits need their own explicit policy.

## 4. What comes from live evidence instead

| Information | Why it is separate from the release description |
| --- | --- |
| Landed/disarmed state and activation interlock | Must be current and maintained throughout the transition; a publisher cannot certify a vehicle's future operational state |
| GNSS/IMU consistency, uncertainty, sample age and time-source trust | Produced at runtime with provenance and limits; position confidence is not trusted time |
| Active artifact and application health | Observed after startup under stated measurement-agent assumptions; a signature on a package does not prove its execution |
| Current mission roles and membership | Set by the authenticated mission contract and controller, subject to software/navigation prerequisites |

The manifest may reference an activation requirement or declare a supported protocol. It cannot supply a trusted `is_landed`, `gnss_score`, `healthy`, or `admission_allowed` observation. Runtime evidence needs session/source/age binding under D01; the independent evaluator alone can see simulation truth.

## 5. If TUF is selected

Keep TUF's native signed metadata and client workflow instead of replacing them with a single custom JSON signature:

- Artifact paths, length and hashes map to target entries.
- Metadata versions, expiration and signing roles stay in native metadata; the TUF workflow uses root, timestamp, snapshot and targets roles.
- Project release/component/compatibility/profile information can be carried in authenticated target `custom` data or an authenticated referenced description. The application must interpret and enforce its semantics; TUF does not do so automatically.
- Installation, ground-state enforcement, health checks, protected application security state and recovery still require application/platform mechanisms.

If a different framework is chosen, document an equivalent responsibility mapping rather than calling a home-grown envelope TUF. Serialization, canonicalization, signature algorithms, key/role handling, metadata size limits and persistent-state behavior remain unresolved.

TUF fixes a reference time at the start of its update workflow. A candidate waiting for a later ground activation raises a separate authorization question: define when metadata must be refreshed/revalidated before activation, with what trusted time evidence. Do not claim that an earlier successful download authorizes activation indefinitely. With insufficient freshness evidence, follow ADR 0002's deferral rule.

## 6. Illustrative release description

This is an **unsigned, incomplete teaching example**, not a valid update manifest, TUF metadata, existing release, or schema fixture. Identifiers are hypothetical; `null` means unresolved. There is no artifact, hash, signature, or profile implementation behind this example. It must never be accepted for activation.

```json
{
  "profile": "swarm-rejoin-release-demo",
  "component_id": "mission-coordinator",
  "release_id": "demo-0.2.0",
  "target_class": "companion-demo",
  "artifact": {
    "path": "mission-coordinator-demo.bundle",
    "format": null,
    "length": null,
    "sha256": null
  },
  "compatibility": {
    "swarm_protocol_ids": ["coordination-demo-v1"],
    "platform_profile_id": null
  },
  "security_epoch": 1,
  "activation_profile_id": "ground-disarmed-demo",
  "health_profile_id": null,
  "recovery_profile_id": null
}
```

Metadata version, expiration and signatures are intentionally not invented in this release-body example. They must be supplied by the chosen authenticated metadata/envelope design. If TUF is selected, use native target length/hash fields rather than independent contradictory copies. Profile references in a final implementation require exact trusted definitions; the demo names above define no operational behavior.

This compact example does not enumerate every proposed detail in section 2.1. In particular, installer, data-transition, dependency and extraction rules still need exact profile definitions before a schema can be frozen.

## 7. Designed walkthroughs, not executed tests

| Case | Required interpretation |
| --- | --- |
| Authentic metadata, complete matching bytes, correct target, incompatible swarm protocol | No role requiring that protocol; activation into an incompatible mission configuration is blocked or deferred according to the explicit compatibility contract |
| Same candidate becomes applicable, but the vehicle is airborne | It may remain staged; no activation under ADR 0003 |
| Candidate is staged, then metadata becomes unusable under the activation freshness policy | Revalidate/refresh as required; defer if authorization/freshness cannot be established |
| Ground activation succeeds, but navigation evidence is inadequate | Application success does not grant a navigation-dependent role |
| Candidate health fails and the old application is below the security floor | Do not reset the floor or treat an old signature as sufficient; use another authorized recovery image or retain mission isolation |
| Candidate startup changes application data so the old version cannot read it | Do not report fallback success just because the old binary starts; require a compatible data restoration path or block the transition before activation |
| Transferred package matches its signed digest but exceeds extraction/local resource limits | Do not unpack beyond the bound or begin activation; report the resource/format failure |
| Candidate or a referenced profile is replaced after verification | Do not activate the replacement; use protected verified objects or reverify under the specified installer contract |

## 8. Decisions to resolve next

Start with component/target inventory and an exact swarm-protocol compatibility contract. Then specify artifact packaging and metadata/framework mapping, trusted-time/activation revalidation, persistent-state commit points, and health/recovery profiles. Proposed initial limits are a full application package, explicit dependencies, and no incompatible persistent-data migration; delta patching and fleet rollout assignments remain later options unless justified. These are recommendations for discussion, not additional accepted ADR decisions. Freeze a machine-readable schema only once these semantics are agreed; use real cryptographic and recovery tests when executable logic is added. This draft does not close R02 or D01/D02.

## Evidence and scope of interpretation

Sources were accessed on **2026-11-10**. Full captures already exist in the source library; selected-section checking here does not change their full-review status.

| Source and exact passages | Evidence used here | Boundary |
| --- | --- | --- |
| [RFC 9124](https://www.rfc-editor.org/rfc/rfc9124.html), sections 3.1-3.9, 3.11-3.16, 3.19, 4.3.1 and 4.3.21; [archive](../research/library/rfc9124/README.md) | Format, applicability/base conditions, payload/signature information, dependencies and protection between check/use; sequence numbers differ from firmware versions | An information model for firmware updates; our companion-app fields and policy profiles are project proposals |
| [TUF Specification](https://theupdateframework.github.io/specification/latest/), sections 2.1, 4.1-4.2, 4.5, 5.1 and 5.3-5.7; [pinned archive](../research/library/tuf-spec/README.md) | Signed roles, target length/hashes/custom data, reference time and client verification | `custom` data is opaque to TUF; our application must implement its meaning; no conformance or deployment result claimed |
| [Uptane Standard 2.1.0](https://uptane.org/docs/2.1.0/standard/uptane-standard), sections 5.3.2 and 5.4.3.3-5.4.3.6; [archive](../research/library/uptane-standard/README.md) | Dependency/conflict consideration, backup, verification, installation preconditions and error handling | Vehicle-update guidance; the companion data-migration, installer/profile and rollout split above is our proposed design, not an Uptane conformance claim |

Ground-only activation, security-epoch abstraction, role appraisal and the proposed teaching example are project design choices, not novel mechanisms established by these sources.
