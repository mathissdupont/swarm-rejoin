# Threat model and claim boundaries

Status: proposed MVP model; validate assumptions before selecting the final topic.

## Assets and trusted components

Protect update authorization, release artifact integrity, persisted security state, current role permissions, and the evidence used for re-admission. Measure mission service as an objective subject to these constraints.

The initial model trusts the release authority, coordinator, provisioning process, and evidence measurement agent. Signer keys and the appraiser are not compromised. Persistent security state is assumed protected in simulation. These are explicit assumptions; Python objects on a laptop do not establish hardware protection.

RATS distinguishes evidence production, verification, and relying-party decisions; use that distinction to avoid confusing an authenticated message with a trustworthy measurement. [RFC 9334](https://datatracker.ietf.org/doc/html/rfc9334) supplies the architectural vocabulary, not a ready-made hardware attestation implementation.

## Adversary and fault capabilities

| Capability/fault | Required experiment | Expected behavior |
| --- | --- | --- |
| Disconnect, delay, reorder, or drop messages | Bounded outage and timeout traces | No unlimited wait or stale permission reuse; report lost availability |
| Replay an old valid update manifest | Obsolete metadata/epoch scenario | Reject under applicable persistent-state and freshness rules |
| Modify an update or its signed metadata | Artifact/metadata tamper scenario | Verification fails before activation |
| Return with a valid but incompatible release | Role/protocol mismatch | Deny incompatible roles; consider only independently permitted alternatives |
| Interrupt update transfer | Partial transfer | Active image remains usable if it was usable before |
| Fail during activation or health checking | Candidate failure | Attempt only an authorized recovery image; otherwise remain isolated |
| Corrupt or remove fallback image | Recovery failure | No false recovery success or mission admission |
| Replay stale navigation/software evidence | Session/age mismatch | Reject or limit permissions according to explicit evidence policy |
| Bias GNSS observations; grow IMU drift | Navigation fault traces | Evaluate detector misses and false alarms; no universal spoofing resistance claim |
| Manipulate GNSS-derived time | Time-source fault | No unsupported freshness claim; use independent time or conservative refusal |

Random outages and malicious suppression are different causes even when the packet trace looks similar. An experiment must state which cause it models. Do not infer the cause solely from a timeout.

## Hard invariants to implement and test

- **I1:** Unauthenticated identities receive no mission role.
- **I2:** An unverified, unauthorized, or incompatible artifact never becomes eligible for a role that requires it.
- **I3:** Effective security state does not regress below the applicable persistent floor after failure or restart.
- **I4:** Update completion requires activation and health confirmation; partial download is not success.
- **I5:** Recovery preserves authorization and triggers a new admission decision.
- **I6:** Role permission expires or is withdrawn when required evidence becomes stale or invalid.
- **I7:** Mission utility cannot override a failed mandatory security condition.
- **I8:** Unknown evidence and infeasible capability requirements have explicit failure outcomes.

Finite tests can find violations but cannot establish universal security. Any formal guarantee must name a formal model, assumptions, property, and proof/checking procedure.

## Explicitly outside the MVP claim

Compromised release-authority keys, Byzantine coordinators, invasive physical attacks, side channels, a compromised root of trust, and arbitrary lies by a fully compromised measurement agent are not solved. An optional weaker-trust experiment may model false self-reports to show this limitation.

A signed artifact demonstrates authorization of bytes under the configured key policy. It does not prove those bytes are running, that the code is benign, that sensor inputs are truthful, or that the vehicle has not been captured. Stronger runtime claims require additional trustworthy measurement and boot mechanisms.

Treat update recovery as an obligation separate from update authenticity; the protect/detect/recover framing in [NIST SP 800-193](https://csrc.nist.gov/pubs/sp/800/193/final) is useful background. The MVP does not claim compliance with that guidance.
