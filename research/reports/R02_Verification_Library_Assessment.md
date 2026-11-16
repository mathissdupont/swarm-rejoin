# R02: Verification-library assessment and research recommendation

- Date: **2026-11-16**
- Preparation: assisted source-based assessment for Samet Ünsal's R02 work
- Status: desk assessment completed for the stated prototype boundary; Ceren/Halil cross-review pending
- Scope: [accepted update requirements](../../docs/decisions/0002-update-mvp-requirements.md), [companion/ground-activation boundary](../../docs/decisions/0003-companion-deployment-and-ground-activation.md)
- Reading depth: the source/API passages and package metadata listed below were checked; this is not a complete conformance audit or measured feasibility study

## Recommendation

Use **Python-TUF as the first reference implementation to evaluate for update metadata and artifact verification**. For this desk assessment the examined release is **7.0.1**, pinned to upstream commit `49eb1da48c58cf0cbb0f2e490f7ad39fbd8c1f15`. This is a research recommendation, not a final product-language decision, adopted repository dependency, or claim of a working updater.

The reason is responsibility coverage: a primitive-only signature library would still leave us designing metadata roles, freshness/version handling and a client workflow. Reusing a reference client makes those established mechanisms a clearer shared baseline for the later GNSS/swarm comparison. Our lifecycle, compatibility and evidence requirements remain outside that library's automatic interpretation.

## Compare the right levels

| Option | What it provides | What this project would still need | Assessment |
| --- | --- | --- | --- |
| Ed25519 through `cryptography` | A maintained signature primitive API; signing and verification of supplied bytes | Update authorization policy, envelope/serialization, metadata sequencing/expiration, trusted-time integration, compatibility, persistence, staging, health and recovery | Suitable as a primitive under a defined protocol; not a complete update baseline by itself |
| Python-TUF `ngclient` | A reference TUF client with trusted-root bootstrap, metadata refresh and verified target download | Project-specific target/custom semantics, trusted host-time assumptions, installer/recovery, protected local state and runtime/mission evidence | Recommended first verification reference for the accepted Linux companion boundary |
| Uptane 2.1.0 | A vehicle-update standard with Image/Director repositories, device version reports and deployment guidance | Select and assess an implementation plus inventory, keys, time, target-specific installation and conformance choices | An important threat/architecture reference; the standard is not one interchangeable Python package |

These are not mutually exclusive competitors: an update framework uses cryptographic primitives, and an Uptane implementation can build on TUF concepts. The table does not establish that one implementation is fastest or smallest.

## Requirement-to-API fit

| Requirement | Checked evidence | Fit and limit |
| --- | --- | --- |
| Provisioned trust anchor | Versioned `Updater` constructor and documentation accept explicit `bootstrap` bytes; `bootstrap=None` opts into cached root metadata | Bootstrap must come from trusted provisioning. Never discover the initial trusted key by trusting the same untrusted release being checked |
| Metadata and artifact verification | `refresh()` follows root/timestamp/snapshot/targets verification; `get_targetinfo()` and `download_target()` expose and verify target information | Reuse the client workflow instead of calling a signature primitive and describing it as TUF |
| Component/protocol compatibility | TUF target entries can contain `custom` data; the pinned `TargetFile.custom` documentation states that Python-TUF does not validate that data | Our application must parse and enforce the exact project contract after metadata authentication |
| Bounded resource use | `UpdaterConfig` exposes metadata length limits, root-rotation/delegation limits and fetcher configuration | Defaults are not measured UAV budgets. Bound the project target/package size and extraction/installation behavior separately |
| Persistent metadata and concurrent access | `metadata_dir` is a writable local cache; documented client use is single-instance per shared cache | File storage is not proof of tamper resistance or crash-safe application-floor commits. Define exclusive access and protected state for a later deployment |
| Network/transport adapter | A `FetcherInterface` can provide controlled I/O | A future offline/local repository can exercise verification without public network availability; no such adapter was implemented here |

Official API: [Python-TUF 7.0.1 Updater](https://theupdateframework.readthedocs.io/en/v7.0.1/api/tuf.ngclient.updater.html). Source snapshot: [updater.py](https://github.com/theupdateframework/python-tuf/blob/49eb1da48c58cf0cbb0f2e490f7ad39fbd8c1f15/tuf/ngclient/updater.py), [config.py](https://github.com/theupdateframework/python-tuf/blob/49eb1da48c58cf0cbb0f2e490f7ad39fbd8c1f15/tuf/ngclient/config.py), and [metadata.py](https://github.com/theupdateframework/python-tuf/blob/49eb1da48c58cf0cbb0f2e490f7ad39fbd8c1f15/tuf/api/metadata.py). Accessed **2026-11-16**, selected declarations/documented behavior only.

## The unresolved time interface is material

The public 7.0.1 constructor inspected here accepts directories/URLs, fetcher, configuration and bootstrap; it does **not** expose a reference-clock argument. The TUF specification fixes a reference time at the beginning of its verification workflow. Therefore, do not assume that injecting a chosen GNSS clock fault into the public client is a solved integration step.

For a later baseline, either explicitly assume and justify a trusted host clock independent of the modeled GNSS input, or design and test a controlled clock adapter/harness before claiming to evaluate actual TUF verification under clock faults. Do not disable expiration checks to obtain an accepted candidate. A candidate held in staging also needs an explicit authorization/freshness revalidation policy before later activation.

Uptane Deployment Best Practices 2.1.0, sections 3.1-3.1.1, already identify ahead/behind clock failures and civilian GPS time risks. This is an established limitation to model, not a new vulnerability discovered by this thesis. Insufficient independent freshness evidence follows ADR 0002's update-deferral rule; continued service from an active release is appraised separately.

## Working research scope to carry into design

Recommend one full mission/coordination package, exact platform/protocol compatibility, a staged candidate separate from the active application, recognized health/recovery profiles, and no incompatible persistent-data migration in the first experiment. These are proposals for a bounded study; only the requirements actually accepted in ADR 0002/0003 are treated as accepted decisions.

Defer delta patching, arbitrary installer hooks, simultaneous fleet transactions and hardware attestation unless they are required by the chosen research question. Versioned schema fields, numerical resource budgets, health timeouts, sensor parameters and physical arming/takeoff enforcement are follow-up design/validation work, not missing proof that a signature algorithm exists.

## Assessment evidence and limits

- The official [PyPI release metadata](https://pypi.org/pypi/tuf/7.0.1/json) identifies release 7.0.1 and Python `>=3.10`; its declared dependencies include `securesystemslib~=1.0` and `urllib3~=2.0`. The [pinned upstream project metadata](https://github.com/theupdateframework/python-tuf/blob/49eb1da48c58cf0cbb0f2e490f7ad39fbd8c1f15/pyproject.toml) was checked on 2026-11-16. Release availability is not an audit of maintainability, vulnerabilities or suitability for a target board.
- A local ignored environment was installed and public API declarations were inspected while assessing fit. No project verifier, signing/recovery experiment, latency benchmark, simulator, hardware trial or conformance test was created or executed. Installation success does not establish functional/security suitability.
- The [Python-TUF source record](../library/python-tuf/README.md) preserves the complete pinned README and MIT license. It does not claim to archive the entire API manual. The [cryptography record](../library/cryptography-ed25519/README.md) preserves complete upstream RST source; generated API docstrings are not expanded. Existing [TUF](../library/tuf-spec/README.md), [Uptane](../library/uptane-standard/README.md) and [deployment guidance](../library/uptane-deployment/README.md) captures remain the mechanism references.
- `cryptography` sign/verify observations use the [official Ed25519 API](https://cryptography.io/en/stable/hazmat/primitives/asymmetric/ed25519/) and matching 50.0.2 page source, accessed 2026-11-16. Uptane's [deployment introduction](https://uptane.org/docs/2.1.0/deployment/best-practices) distinguishes its standard from available implementations.

## R02 cross-review handoff

Another author should check four specific points against the cited passages: (1) signature/authorization/running-state distinctions, (2) metadata sequencing versus application versions and permitted fallback, (3) insufficient-time behavior without GNSS-only trust, and (4) whether the Python-TUF recommendation preserves rather than bypasses the required checks. Link disagreements and resolutions. No independent review has been recorded by this assessment, so issue #2 remains open pending that acceptance step.
