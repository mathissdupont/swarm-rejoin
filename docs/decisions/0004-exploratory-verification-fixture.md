# ADR 0004: Exploratory verification and lifecycle fixture

- Date: 2026-11-27
- Status: Implemented exploratory choice under Samet's instruction to begin the work; final research acceptance remains open
- Scope: reversible infrastructure, not a production platform or completed contribution gate

## Decision

Use Python and the previously assessed Python-TUF **7.0.1** client to build the first verification/lifecycle integration fixture. Use actual Ed25519-signed TUF metadata and payload checks via its client workflow, with a controlled in-memory transport, provisioned bootstrap and host UTC assumption. Generate signing keys in memory only. Pin the direct dependencies and constrain runtime transitive packages for repeatable installation.

Authenticate a narrow fixed v1 custom-field profile: component/platform, protocol/data-schema, release/security epoch and fixed modeled activation/health profiles. Opaque payload bytes are never executed or extracted. Stage, activate, observe health, attempt authorized recovery and appraise role evidence through explicit in-process transitions. Keep Windows portability for this layer; Linux remains the intended companion-process target from ADR 0003.

## Consequences and limits

This partially supersedes the historical no-code staging language of ADR 0001 for reusable infrastructure, following Samet's explicit instruction to proceed. It does not select or prove the final thesis contribution, satisfy independent review, or move the accepted application target to flight-control firmware.

The fixture has no GNSS estimator, motion model, B3/P controller, process installer, hardware trust anchor or distributed authentication protocol. Evidence, health, operational state and local policy protection are modeled assumptions. Recovery conservatively requires fresh current metadata; offline available recovery remains unimplemented. Security-floor state is in memory, not a protected persistent transaction. See the [quickstart and exact capability limits](../16-prototype-quickstart.md).

Behavioral tests must accompany any changes to release gates, transition ordering, recovery or role admission. The [research model gate](../12-contribution-and-decision-gate.md) still determines the navigation model, mission and defensible comparison; this fixture cannot establish originality.
