# Experiment specifications

Nothing in this directory is an executed experiment. [scenarios.json](scenarios.json) is a design-only catalog for a future simulator. Its scenarios are project proposals; supporting source identifiers refer to background mechanisms, not to proof that those sources used the same experiments.

Begin with the [evaluation plan](../docs/06-evaluation-plan.md). Every implemented scenario needs a ground-truth generator, observations visible to policies, precise fault timing/severity, role requirements, and an independently evaluated outcome.

## Scenario conventions

- The default six-agent mission is provisional. Evaluate five and eight agents after the model works.
- Baselines B0/B1 deliberately lack security checks; use them for context only. B3 is the main fair comparator for P.
- `required_invariants` applies to the intended secure implementation (B2/B3/P as relevant), not to intentionally insecure context baselines.
- `questions` lists outcomes to measure. It does not preassign a winning policy or guaranteed result.
- Do not infer spoofing from every GNSS outage or infer compromise from every update failure.
- Navigation fault magnitudes, thresholds, update sizes, and clock bounds remain unspecified until a justified model and pilots exist.

## Future run contract

Each run must record: run ID; source revision and dirty state; policy/configuration version; exact command; environment; seed set; scenario parameters; independent truth trace; observed evidence; decision/transition trace; metrics; failure/censoring status; and artifact hashes.

Raw run output belongs under `results/<unique-run-id>/` and is ignored by default. Retain large runs in agreed external storage with content hashes and a manifest committed separately. Publish only aggregate results that can be traced to retained runs. Do not commit downloaded papers or signing keys alongside results.
