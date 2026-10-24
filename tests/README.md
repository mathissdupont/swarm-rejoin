# Behavioral test plan

No simulator or security tests exist yet because those components are not implemented. The current workspace can be checked with `python tools/check_repo.py`.

When implementation begins, add meaningful tests for:

- Actual signature and digest verification, target mismatch, obsolete metadata, and prohibited epochs.
- Navigation false alarms/missed detections against independent truth and evidence expiration.
- Replayed evidence with the wrong session/challenge/mission binding.
- Interrupted downloads that preserve the active image.
- Activation/health-check failures and permitted versus prohibited fallback images.
- Crash/restart points around persistent security state.
- Hard security gates that cannot be overridden by utility or mission urgency.
- Role-specific compatibility, unachievable capacity requirements, and controller timeouts.
- Identical exogenous traces across policies, reproducible seeded runs, and correct treatment of failures/censored delays.

Do not replace cryptographic or behavioral validation with assertions that simply repeat a policy's implementation.
