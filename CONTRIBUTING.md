# Contributing

## Team workflow

Samet Ünsal, Ceren Tolunay, and Halil Abacı are joint thesis contributors. Technical leads in the roadmap are proposals for team agreement, not statements about work already completed.

Use small branches such as `research/nearest-work`, `update/recovery-model`, or `gnss/innovation-monitor`. Open a pull request with the question, evidence or behavior changed, validation, and unresolved limits. At least one other author should review changes to the threat model, metrics, or security decisions.

Keep bibliography identifiers stable. Add each retained source to the source registry, bibliography, and matrix. Use a paper note to distinguish the authors' claims from your assessment. Search discoveries do not automatically count as included studies.

## Reproducibility

Keep generated output under a unique run directory. Record the commit, dirty-worktree status, environment, exact command, configuration digest, seed, and failure outcomes. Freeze thresholds on a development split before evaluating the held-out scenarios.

For future implementation, require tests for tampering, replay, obsolete security epochs, incompatible roles, interrupted updates, recovery failures, and timeout handling. A toy policy comparison is not evidence of a deployed security mechanism.

## Sharing and licensing

The repository owner has authorized public publication at [mathissdupont/swarm-rejoin](https://github.com/mathissdupont/swarm-rejoin). No open-source license is selected by this scaffold; agree on a code/documentation license separately. Do not add third-party PDFs unless redistribution is permitted. Keep private keys, credentials, identifying flight data, and machine-specific paths out of commits.

For subsequent contributions:

```powershell
git add .
git commit -m "Document the research question and supporting evidence"
```

Collaborator invitations use verified GitHub handles and write access so team members can push branches and open pull requests. Invitation acceptance is separate from sending the invitation. The automatically generated GitHub contributor list reflects qualifying contributions; adding a collaborator does not fabricate a contribution history.

Research issues name a proposed lead even while a GitHub assignment is pending. Confirm accounts before assigning tasks or sending invitations. Avoid separate copies in shared cloud folders once the team starts collaborating; use Git branches and pull requests as the source of truth.
