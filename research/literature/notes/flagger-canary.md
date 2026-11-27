# Source note: Flagger canary analysis

- Source: `flagger-canary`, [pinned archive](../../library/flagger-canary/README.md)
- Checked: 2026-11-27; selected official guide sections; no software deployment or paper-review claim

The guide's **Canary analysis** section defines periodic metrics/webhook checks, promotion settings and rollback after a failed-check threshold. It is a Kubernetes workload mechanism. This establishes prior operational practice for staged promotion, not validation of a UAV navigation-specific test.

Use it as background for R08/T3's fixed-canary comparator. Our proposed configuration test needs representative vehicle maneuvers, independent navigation truth and role constraints; traffic success metrics are not navigation integrity. No cluster, Flagger integration or fleet rollout was created. Ordinary canary deployment must not be presented as our new mechanism.
