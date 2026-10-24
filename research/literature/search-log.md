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
