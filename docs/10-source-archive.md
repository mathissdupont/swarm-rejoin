# Source archive workflow

Effective 2026-11-10: all research notes and source records belong in this repository. Archive full source Markdown and the original PDF where available and redistributable. This replaces the initial rule to keep downloaded papers outside Git.

## Layout and meaning

The [library index](../research/library/README.md) is the entry point. Each registered source has `research/library/<source-id>/README.md` with attribution, source URL, date/version, rights evidence, acquisition limitations, and file checksums. The [manifest](../research/library/manifest.json) indexes the actual files.

- `full_text`: a complete textual capture, not an abstract or research summary. It may be original upstream Markdown or an automatic full-PDF transcription.
- `record_only`: citation and acquisition status only. Full text is still missing; do not describe the source as downloaded or reviewed.
- `pdf_status=archived`: unchanged original PDF is stored and hashed.
- `not_located`: no standalone original PDF was located at the inspected source; this is not proof that none exists.
- `access_blocked`: retrieval failed or returned a non-document response.
- `redistribution_unconfirmed`: a public-republication license has not been established.

Existing PDFs and Markdown in Ceren's folder are indexed in place. Do not make duplicate copies solely to satisfy a folder layout. Keep notes, personal answers, reports, reviews, and experiment records in the existing research directories and link them to source IDs.

## Import a registered source

First add or verify its registry, BibTeX, and matrix entries. The importer downloads only explicitly provided HTTPS locations and requires rights evidence for full-text publication. Preserve the original license; a public website or repository does not by itself establish permission to republish an article.

For a permitted original PDF:

```powershell
python tools/archive_source.py SOURCE_ID --retrieved-on YYYY-MM-DD --pdf-url ORIGINAL_PDF_URL --license-id LICENSE_ID --license-url LICENSE_URL --evidence-url RIGHTS_EVIDENCE_URL --version SOURCE_VERSION
```

Install the optional import tools with `python -m pip install -r tools/requirements-archive.txt` when needed. The PDF command uses `pypdf`; the importer prefers the ordinary `requests` HTTP client when installed and otherwise uses `urllib`. Some publishers return different representations to different HTTP clients, so every downloaded PDF is checked for actual PDF bytes. The importer retains original bytes, extracts every page into Markdown, records page count and transformations, and updates the index/manifest. Offline checking needs neither dependency.

For original Markdown, prefer a source URL pinned to an upstream commit:

```powershell
python tools/archive_source.py SOURCE_ID --retrieved-on YYYY-MM-DD --markdown-url PINNED_RAW_URL --license-id LICENSE_ID --license-url LICENSE_URL --evidence-url RIGHTS_EVIDENCE_URL --license-file-url ORIGINAL_LICENSE_URL --version COMMIT_OR_VERSION
```

Relative links are resolved against the captured upstream URL. Upstream images remain references unless separately archived; PDF captures retain the original figures. An automatic transcription may distort columns, tables, equations, or reading order; use its original PDF for those details.

For files already supplied in this repository, use `--existing-pdf PATH --existing-markdown PATH` with the same provenance and rights arguments. Their files are retained at their current paths.

For an inaccessible or restricted source, create an honest acquisition record:

```powershell
python tools/archive_source.py SOURCE_ID --retrieved-on YYYY-MM-DD --record-only --pdf-status access_blocked --reason "Exact observed access limitation"
```

Use `--pdf-status redistribution_unconfirmed` when rights have not been established. A known permissive license with failed retrieval can be recorded using its rights fields and `--redistribution-permitted`; this does not claim that a document was obtained.

## Updating captures

The importer refuses accidental replacement; inspect changes and use `--replace` deliberately. A source update changes its hash and potentially the interpretation of earlier notes. Preserve the exact version or commit referenced by previous research where needed. Do not change `full_text_review_complete` merely because a file was downloaded or converted.

Use UTF-8 and LF line endings for captured text and record files so Git normalization on Windows does not change their recorded hashes. PDF hashes always cover the original binary bytes.

Run:

```powershell
python tools/check_repo.py
python -m unittest discover -s tests -p "test_source_library.py"
```

The checker requires an entry for every retained source, verifies file paths and SHA-256 values, checks status/rights consistency, and rejects an HTML error response mislabeled as PDF. It does not determine legal permissions or scientific validity for you; rights evidence and review claims still require source inspection.

## Current gaps

Consult the live library index for exact missing items and observed errors. Never replace an unavailable paper with an invented full-text Markdown file or a PDF containing only a summary. Keep its citation, existing notes, and acquisition gap together until a permitted original is obtained.
