# Search log

## Initial discovery pass — 2026-10-24

Method: general web discovery with follow-up opening of primary publisher, institutional, specification, and official documentation pages. This was not a direct exported IEEE/ACM/Scopus database search. Counts and rankings were not recorded, so none are reported. The seed registry is not an inclusion count.

The user's supplied DOI and PX4 guide were investigated first. The DOI's direct browser open failed, but publisher-indexed text and Crossref metadata were retrievable. Record this limitation instead of claiming a full paper review.

Representative exact discovery queries issued in this pass:

```text
"10.1016/j.bcra.2026.100439"
Uptane secure software updates vehicles 2016 paper rollback freeze mix and match attack
IETF SUIT RFC 9019 RFC 9124 firmware update manifest architecture
secure swarm UAV rejoining software update GNSS authentication rejoin
UAV swarm secure firmware update rejoining version compatibility interrupted update
robot fleet software update scheduling mission continuity rolling update research
UAV secure over the air update rollback recovery firmware research
"Scheduling Dynamic Software Updates in Mobile Robots" "10.1145"
site.ietf.org RFC 9334 remote attestation procedures architecture
site.nist.gov SP 800-193 platform firmware resiliency guidelines
site.ion.org "An INS Monitor" spoofers
"rejoining" "software update" swarm
"UAV" "re-admission" "update"
"UAV" "firmware" "recovery" "swarm"
```

Follow-ups included the official TUF specification, Uptane 2.1.0, RFCs 9019/9124/9334, the RASUES publisher page, the NeRTA institutional record, the ION abstract, and MAVLink documentation. Crossref bibliographic metadata was checked for Dong 2026, RASUES, NeRTA, the 2018 Uptane article, and a SEDA discovery candidate. SEDA was not retained in the initial registry because a directly useful full-text comparison was not performed.

The official Datatracker BibTeX exports for RFCs 9019, 9124, and 9334 were also retrieved to check citation metadata. This does not constitute reading their full technical content.

Some discoveries concerned UAVs delivering updates to other IoT devices, rather than updates to swarm members. These require transferability screening before inclusion. Search hits and unverified preprints were not promoted to supporting evidence merely because their titles appeared close.

## Next search round — not yet performed

Prioritize GNSS-aware update/rejoining interactions and swarms, not generic OTA security alone. Run the six streams in the [protocol](../../docs/03-literature-review-protocol.md), capture actual result exports/counts where available, deduplicate, and record inclusion/exclusion decisions.

## Alternative-topic discovery pass — 2026-10-24

Additional exact general-web queries:

```text
UAV swarm GNSS secure software update attestation rejoining navigation integrity firmware
robot fleet rolling software updates localization uncertainty mission scheduling
GNSS spoofing secure time firmware update freshness Uptane
site.gsc-europa.eu OSNMA service navigation message authentication position spoofing limitations
site.gsc-europa.eu OSNMA receiver software updates firmware
```

Retained three additional seed references: Uptane Deployment Best Practices 2.1.0 (selected secure-time passages), Yan et al. 2020 (institutional indexed abstract; direct opening returned HTTP 429), and the European GNSS Service Centre FAQ (selected OSNMA passages). The six-topic shortlist is a set of proposals informed by this discovery pass, not a completed gap analysis.

Crossref title, author, and publication metadata was additionally checked for Yan et al. 2020.

No database exports, full review counts, or novelty scores were produced in this pass.

## R03 verification pass - 2026-11-01

Purpose: inspect the research added in PR #14 and commit `5b63595`, rather than infer completion from issue closure. This was a targeted verification pass, not a new systematic search or completed full-text review.

Sources: three supplied PDFs, their provenance records, primary publisher/author pages, the ION 2016 abstract, and Crossref records for `10.3390/s25020358`, `10.3390/app13084819`, `10.1007/s41315-026-00528-9`, and `10.1109/TAES.2017.2739924`.

Representative exact queries:

```text
"A Comprehensive Survey on the Integrity of Localization Systems" 358
"An INS Monitor to Detect GNSS Spoofers" pdf
"A Comprehensive Review of GNSS/INS Integration Techniques" loosely coupled
"Tanil" "2739924" filetype:pdf
"An INS Monitor to Detect GNSS" site:illinoistech.edu
"An INS Monitor to Detect GNSS" site:vt.edu
```

Selected local-PDF passages and publisher material were checked; recorded file hashes and page counts were confirmed. MDPI browsing was rate-limited. The inherited Tanil 2018 author-PDF fetch returned 404 while indexed abstract text remained discoverable. Access limitations were retained rather than upgraded to a full review.

Four records and reading notes were added. No source was marked as a completed full-text review. See the [review record](../reviews/2026-11-01-r03-review.md) for source locations, independent arithmetic checks, and follow-up requirements. No database export or screened-study count was produced.

## Source-library capture and R02 foundations - 2026-11-10

Purpose: centralize all retained source records and capture permitted full text/PDFs, then prepare a source-based answer to the first R02 reading questions. This was not a new systematic review or a transcription of private handwritten notes.

All 20 retained sources now have local records. Fourteen have complete textual captures and eleven have original PDFs; Ceren's three supplied PDF/Markdown pairs are indexed in place. The [library manifest](../library/manifest.json) records exact paths, retrieval dates/versions, rights evidence, transformations, and hashes. Six record-only items retain observed access or redistribution gaps instead of claiming missing full text.

Checked official RFC Editor PDFs, NIST SP 800-series rights guidance, Uptane's official 2.1.0 PDFs and website license, permissive publisher/institutional article copies, and pinned upstream TUF/PX4/MAVLink Markdown/licenses. Ordinary HTTP retrieval produced access failures for some sources; no paywall or access-control bypass was used. Downloaded PDF bytes and page counts were verified. Conversion uses every PDF page and preserves original PDFs for layout-sensitive reading.

R02 re-examined selected RFC 9019, RFC 9124, Uptane Standard 2.1.0, and Uptane Deployment 2.1.0 passages. Its [starting note](../reports/R02_Secure_Update_Foundations.md) distinguishes established mechanisms, project choices, and two designed failure traces. Uptane section 7.10 already covers location-based updates, so no broad novelty claim about location-aware updating is introduced. No source was promoted to a completed full-text review by the archive operation.

## Entry template

Use this entry format:

```text
Date and reviewer:
Platform and exact query:
Filters, time range, and ordering:
Recorded results / export location:
Candidate identifier and duplicate family:
Screening decision and reason:
Full-text access and reviewed version:
Claims or table cells changed:
Next citation-chasing step:
```
