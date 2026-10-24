# SWARM-REJOIN

**An undergraduate thesis workspace connecting GNSS integrity, secure software updates, and UAV swarm rejoining.**

**Team:** Samet Ünsal · Ceren Tolunay · Halil Abacı

**Status:** Research scoping. The final thesis topic and novelty claim are not yet established.

**Planning target:** May 2027, subject to the university's official deadline.

The team's research direction is to combine **GNSS reliability, secure software updates, and UAV swarms**, using safe rejoining and mission continuity as the starting scenario. The first literature pass found relevant overlapping mechanisms, but it does not establish whether this specific joint problem has already been solved. This repository starts with a **research question and scope assessment**, rather than a claim of proven novelty.

The working title is **GNSS-Aware Secure Updates and Rejoining in UAV Swarms**. The candidate question is whether navigation integrity evidence can inform secure update/recovery and re-admission decisions while preserving mission service. The mechanism, scientific contribution, and benefit remain to be investigated. GNSS is a central research input, not an optional feature.

## Start here

1. Read the [topic assessment and alternatives](docs/01-topic-decision.md).
   Compare the [six candidate thesis topics](docs/09-topic-shortlist.md) before committing to a final question.
2. Follow the [literature review protocol](docs/03-literature-review-protocol.md) and inspect the [source matrix](research/literature/matrix.md).
3. Use the [research brief](docs/02-research-brief.md), [system design](docs/04-system-design.md), and [threat model](docs/05-threat-model.md) to challenge the candidate.
4. Agree on the [evaluation plan](docs/06-evaluation-plan.md), then work from the [team roadmap](docs/07-roadmap-and-team.md) and [backlog](docs/08-backlog.md).

## What exists today

- An evidence-based topic assessment, six candidate thesis topics, and a keep/pivot gate.
- Sixteen seed references with access and reading status, BibTeX, search records, and review templates.
- A proposed architecture, explicit trust assumptions, baseline comparisons, and a fault scenario catalog.
- A two-semester plan and proposed responsibilities for all three authors.
- A dependency-free repository checker and a GitHub Actions workflow.

**There is no UAV simulator, signature verifier, updater, GNSS estimator, PX4 adapter, or experimental result yet.** Proposed designs and scenario parameters are not validated findings. A signed release manifest cannot by itself prove what software is running on a remote UAV.

## Repository layout

```text
docs/                    Research questions, architecture, evaluation, and decisions
research/literature/     Source registry, bibliography, matrix, searches, initial notes
research/templates/      Paper reviews, experiment reports, meetings, decisions
experiments/             Planned fault scenarios and result recording conventions
src/swarm_rejoin/        Implementation boundary map; development starts after topic selection
tests/                   Future behavioral tests and their acceptance criteria
tools/check_repo.py      Offline checks for references, links, and scenario metadata
.github/                 Review templates and repository checks
```

## Check the workspace

Python 3.12 or newer is sufficient; no third-party package is required for these checks.

```powershell
python tools/check_repo.py
```

The checker validates repository consistency. It does not verify scientific claims, live URLs, cryptographic signatures, or flight safety.

## Research principles

- Keep all repository documentation, code, issues, and commit messages in English.
- Separate observed evidence, proposed mechanisms, assumptions, and unresolved questions.
- Compare against a credible secure-update baseline as well as simple identity baselines.
- Determine unsafe admissions from independent simulation truth, never from the policy's own score.
- Treat negative results and failed recovery attempts as data.
- Record the conditions under which a claim holds; do not claim that simulation establishes hardware security.

The public repository is [mathissdupont/swarm-rejoin](https://github.com/mathissdupont/swarm-rejoin). Use [GitHub issues](https://github.com/mathissdupont/swarm-rejoin/issues) for research tasks. See [CONTRIBUTING.md](CONTRIBUTING.md) for collaboration and licensing. Public visibility does not by itself grant an open-source license; a redistribution license has not been selected.
