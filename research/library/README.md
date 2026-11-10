# Research source library

20 source records; 14 full-text Markdown captures; 11 original PDFs. Counts describe stored material, not completed reviews.

Every retained source has a local record. Full text is stored only when retrieval and redistribution are supported. A record-only item is explicitly incomplete; it is not a substitute for the full paper.

Existing material in Ceren's literature folder is indexed in place to avoid duplicates.

| Source | Capture | Original PDF | Status / limitation |
| --- | --- | --- | --- |
| [dong2026](dong2026/README.md) | Record only | access blocked | Crossref records CC BY 4.0 for the version of record. Publisher article requests returned HTTP 403; the official API supplied metadata rather than complete article text, and its PDF request returned 406. No full text is claimed. |
| [usman2026](usman2026/README.md) | [Full text](../../research/library/usman2026/full-text.md) | [PDF](../../research/library/usman2026/source.pdf) | Complete PDF and automatic text capture; reading status is unchanged. |
| [yaacoub2023](yaacoub2023/README.md) | [Full text](../../research/library/yaacoub2023/full-text.md) | [PDF](../../research/library/yaacoub2023/source.pdf) | Complete PDF and automatic text capture; reading status is unchanged. |
| [kuppusamy2018](kuppusamy2018/README.md) | Record only | redistribution unconfirmed | Publisher metadata carries IEEE terms; a license permitting republication of the complete article has not been established. A public-access link alone is not a redistribution grant. |
| [tuf-spec](tuf-spec/README.md) | [Full text](../../research/library/tuf-spec/full-text.md) | not located | Original Markdown captured. No separate official PDF was located on the inspected source. |
| [uptane-standard](uptane-standard/README.md) | [Full text](../../research/library/uptane-standard/full-text.md) | [PDF](../../research/library/uptane-standard/source.pdf) | Complete PDF and automatic text capture; reading status is unchanged. |
| [rfc9019](rfc9019/README.md) | [Full text](../../research/library/rfc9019/full-text.md) | [PDF](../../research/library/rfc9019/source.pdf) | Complete PDF and automatic text capture; reading status is unchanged. |
| [rfc9124](rfc9124/README.md) | [Full text](../../research/library/rfc9124/full-text.md) | [PDF](../../research/library/rfc9124/source.pdf) | Complete PDF and automatic text capture; reading status is unchanged. |
| [rfc9334](rfc9334/README.md) | [Full text](../../research/library/rfc9334/full-text.md) | [PDF](../../research/library/rfc9334/source.pdf) | Complete PDF and automatic text capture; reading status is unchanged. |
| [nist193](nist193/README.md) | [Full text](../../research/library/nist193/full-text.md) | [PDF](../../research/library/nist193/source.pdf) | Complete PDF and automatic text capture; reading status is unchanged. |
| [tanil2016](tanil2016/README.md) | Record only | redistribution unconfirmed | Publisher full text requires download access; no redistributable full-text copy is recorded. Publisher abstract and bibliographic notes remain available in this repository. |
| [px4-multi](px4-multi/README.md) | [Full text](../../research/library/px4-multi/full-text.md) | not located | Original Markdown captured. No separate official PDF was located on the inspected source. |
| [mavlink-signing](mavlink-signing/README.md) | [Full text](../../research/library/mavlink-signing/full-text.md) | not located | Original Markdown captured. No separate official PDF was located on the inspected source. |
| [uptane-deployment](uptane-deployment/README.md) | [Full text](../../research/library/uptane-deployment/full-text.md) | [PDF](../../research/library/uptane-deployment/source.pdf) | Complete PDF and automatic text capture; reading status is unchanged. |
| [yan2020](yan2020/README.md) | Record only | redistribution unconfirmed | Institutional page/PDF requests returned HTTP 202 without article content. Crossref lists IEEE terms rather than an established public-republication license. |
| [galileo-faq](galileo-faq/README.md) | Record only | access blocked | Official page retrieval returned HTTP 403. No complete local capture or source-specific redistribution evidence was obtained. |
| [maharmeh2025](maharmeh2025/README.md) | [Full text](../../research/literature/cerentolunay/sensors-25-00358-v2.md) | [PDF](../../research/literature/cerentolunay/sensors-25-00358-v2.pdf) | Existing full PDF/Markdown indexed in place; original author, license, and conversion notices retained. |
| [boguspayev2023](boguspayev2023/README.md) | [Full text](../../research/literature/cerentolunay/applsci-13-04819.md) | [PDF](../../research/literature/cerentolunay/applsci-13-04819.pdf) | Existing full PDF/Markdown indexed in place; original author, license, and conversion notices retained. |
| [alipour2026](alipour2026/README.md) | [Full text](../../research/literature/cerentolunay/s41315-026-00528-9.md) | [PDF](../../research/literature/cerentolunay/s41315-026-00528-9.pdf) | Existing full PDF/Markdown indexed in place; original author, license, and conversion notices retained. |
| [tanil2018](tanil2018/README.md) | Record only | redistribution unconfirmed | Inherited author-hosted PDF URL returned 404 during the review. Full-text redistribution permission is not established; indexed abstract and original-method access limits are recorded. |

## Add or update a source

1. Register the citation in `research/literature/sources.json`, BibTeX, and the matrix.
2. Capture original Markdown or a complete PDF transcription and an unchanged PDF when one is available. Follow the [archive workflow](../../docs/10-source-archive.md).
3. Record source URL, version/retrieval date, rights evidence, transformation, file hashes, and the exact reason for any missing format.
4. Run `python tools/check_repo.py` before committing.

The [manifest](manifest.json) is the machine-readable file inventory. Paper notes, interpretations, and empirical findings remain separate artifacts.
