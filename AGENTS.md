# Repository instructions

- Use English for every repository artifact. Preserve contributors' names and source titles accurately.
- Read `README.md` and `docs/01-topic-decision.md` before changing research scope.
- This is a research-scoping repository. Do not represent planned components or scenarios as implemented experiments.
- Never invent citations, paper findings, review counts, measurements, or completed meetings.
- Record source URLs, access dates, reading depth, and claim-specific evidence. Mark an inaccessible detail as unknown.
- Do not infer novelty from a search returning no results. Check the nearest work and document remaining uncertainty.
- Authentication, update authorization, artifact integrity, running-state evidence, and mission fitness are separate properties.
- Hard security failures must not be offset by a mission utility score.
- Keep all research notes and source records in this repository. Archive redistributable full source text as Markdown and the original PDF when available, indexed under `research/library/` with provenance, license evidence, and checksums. Preserve existing source locations rather than duplicating files. For inaccessible or non-redistributable material, keep an explicit local source record and acquisition status; do not label it as archived full text. Keep signing keys and credentials outside version control.
- Keep runs reproducible with configuration, seed, revision, environment, and independent ground truth.
- Run `python tools/check_repo.py` after changing documentation, references, or scenarios.
- Add behavioral tests when implementing security or recovery logic. Do not add fake security primitives or fabricate benchmark results.
