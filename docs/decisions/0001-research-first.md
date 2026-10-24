# ADR 0001: Research-first workspace

- Date: 2026-10-24
- Status: Adopted for repository scaffolding; final topic remains provisional

## Context

The original thesis combines identity, location confidence, and software state during UAV rejoining. Initial source inspection found overlapping reconnection and update mechanisms. The team is willing to change topic if a useful contribution cannot be supported. Submission is likely in May 2027 and technology is flexible.

## Decision

Keep SWARM-REJOIN as the workspace name and preserve the team's intended intersection: GNSS systems, secure updates, and UAV swarms. Investigate GNSS-aware update/recovery and rejoining decisions as candidate A, compare alternatives B/C within this intersection, and defer final scientific claims and implementation architecture until a two-week literature/topic gate. The initial search does not justify a conclusion that the whole topic lacks contribution.

Use English throughout the repository. Start with a small Python model if the candidate survives. Scope PX4 to a later integration case study. Separate proposed design from implemented capability and measured evidence.

## Consequences

No simulator or security component is represented as complete. Existing mechanisms are credited to their sources. The repository can support a pivot without losing the bibliography, review process, and reproducibility conventions. The final thesis title can differ from the repository name.
