# Literature review protocol

Version: 0.1, established 2026-10-24. This is a protocol for a structured review, not a claim that a systematic review has already been completed.

## Review objective

Determine which parts of secure update, attestation, reconnection, navigation integrity, and mission-aware recovery are already established. Find the closest answer to the candidate question, its assumptions, and an experimentally testable difference.

## Search streams

| Stream | Starting query | Lead |
| --- | --- | --- |
| Secure update | `("UAV" OR "robot" OR "embedded") AND ("secure update" OR "firmware update" OR "OTA") AND (rollback OR recovery OR compatibility)` | Samet |
| Reconnection | `("UAV swarm" OR "multi-robot") AND (rejoin OR rejoining OR reconnection OR "re-admission") AND (integrity OR attestation OR trust)` | Halil |
| Scheduling | `("robot fleet" OR "UAV team" OR "multi-robot") AND ("software update" OR "rolling update") AND (mission OR scheduling OR continuity)` | Halil + Samet |
| Navigation | `("GNSS" OR "GPS") AND ("IMU" OR "INS") AND (spoofing OR integrity OR consistency) AND (monitor OR innovations)` | Ceren |
| Time/freshness alternative | `("secure update" OR "firmware update") AND ("untrusted time" OR "offline" OR "clock uncertainty" OR "freeze attack")` | Ceren + Samet |
| Benchmark alternative | `("robot" OR "UAV" OR "IoT") AND ("update recovery" OR "OTA") AND ("fault injection" OR benchmark OR reproducibility)` | All |

Expand terminology when results are sparse. Search software adaptation, fleet maintenance, rolling upgrades, heterogeneous versions, secure recovery, and disconnected attestation separately. Exact keyword matches alone will miss relevant work.

## Where and when

Use IEEE Xplore, ACM Digital Library, SpringerLink, ScienceDirect, USENIX/NDSS proceedings, author/institutional repositories, and arXiv. Google Scholar can help discovery and citation chasing but is not the evidence source for a technical claim. Standards and official implementation documentation form a separate evidence category.

Initially prioritize 2020–2026 and retain older foundational work such as TUF, Uptane, and GNSS/INS monitoring. Search through the actual date of each review. Refresh the search before the topic decision, at the end of January, and before final writing. Do not treat a preprint as peer reviewed or a draft as a published standard.

## Search and screening procedure

1. Copy the exact query, platform, search date, filter settings, and result ordering into the [search log](../research/literature/search-log.md). Record result counts only when measured.
2. Export or manually capture the candidates with persistent identifiers. Deduplicate by DOI, then normalized title and authors. Treat preprint and published versions as one study family unless materially different.
3. Screen title and abstract for relevance; record `include`, `exclude`, or `uncertain`, with a reason.
4. Retrieve full text through legitimate access. Mark inaccessible or unexamined features `unknown`.
5. Complete the [paper note](../research/templates/paper-note.md). Record the exact section, figure, or table supporting each important comparison.
6. Have another author review inclusion decisions and the claims about the three nearest studies. Resolve disagreements in a short note.
7. Chase references backward and citing works forward for the nearest studies. Repeat until new results stop changing the feature comparison; report this as a practical stopping rule, not proof of completeness.

The current registry contains **seed sources**, not the final included-study set. No formal database result counts or PRISMA flow counts have been collected yet.

## Inclusion and exclusion

Include sources that define relevant mechanisms, expose comparable assumptions, evaluate update/recovery behavior, or provide a directly reusable benchmark. Include credible conflicting or negative findings. Separate research papers, informational RFCs, standards/specifications, and implementation guides in the matrix.

Exclude marketing-only claims, exact duplicates, unverifiable references, and unrelated work such as UAV delivery of updates to ground IoT sensors unless its mechanism transfers to the candidate problem. Retain excluded nearest-looking results in the screening record with a reason. A low citation count or an inconvenient result is not an exclusion criterion.

## Extract these fields

- Exact bibliographic identity, persistent URL, publication type, and reviewed version.
- Research question, system assumptions, adversary, coordinator trust, and key compromise model.
- Artifact authentication versus installed/running-state evidence and their trust anchors.
- Version dependencies, security floors, freshness/time assumptions, update interruptions, and recovery behavior.
- Reconnection, role allocation, navigation uncertainty, mission constraints, and decision timing.
- Baselines, sample counts, independent ground truth, distributions, confidence intervals, code/data availability, and measured resource costs.
- Direct overlap, an unresolved limitation, and the smallest fair comparison we could implement.

## How to assess contribution

Use a claim-to-evidence table: `proposed difference → closest source section → shared assumptions → unresolved feature → falsifiable experiment`. A blank or unknown feature is not evidence that the source lacks it.

Do not write "no prior work combines X and Y" based on this initial pass. Prefer: "Under assumptions A and B, we evaluate whether mechanism M improves outcome O compared with policy P." If a similar method exists, reproduce/adapt it and change the contribution claim or pivot.

## Reading rhythm

For the first two weeks, each author owns two deep reading notes and cross-reviews one other note. Start with Dong 2026, RASUES 2026, NeRTA 2023, and the update specifications; use Ceren's GNSS seed to define what location evidence can and cannot establish. The team reviews the resulting matrix together before selecting the final question.
