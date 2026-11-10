"""Capture a registered, redistributable source or record an acquisition gap.

PDF conversion requires pypdf. The optional requests transport is preferred when
installed; otherwise downloads use urllib. Offline checks need neither package.
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

from source_library import MANIFEST, artifact, digest, resolve_source_links, write_catalog


ROOT = Path(__file__).resolve().parents[1]


def download(url: str) -> tuple[bytes, str]:
    if not url.startswith("https://"):
        raise ValueError("Use an HTTPS source URL")
    try:
        import requests
    except ImportError:
        requests = None
    if requests is not None:
        response = requests.get(url, timeout=40)
        response.raise_for_status()
        return response.content, response.url
    request = Request(url, headers={"User-Agent": "Swarm-Rejoin-Research-Archive/1.0"})
    with urlopen(request, timeout=40) as response:
        return response.read(), response.url


def pdf_markdown(data: bytes, title: str) -> tuple[str, int]:
    from pypdf import PdfReader

    if not data.startswith(b"%PDF-"):
        raise ValueError("The response is not a PDF; no HTML error page was archived")
    reader = PdfReader(io.BytesIO(data))
    parts = [f"# {title}", "", "Automatic full-document text transcription. "
             "All source pages are represented below. Page text is preformatted to retain "
             "extracted line breaks; equations, columns, tables, and figures must be checked "
             "against the unchanged original PDF. This is not a paper review.", ""]
    nonempty = 0
    for number, page in enumerate(reader.pages, 1):
        # Plain extraction includes rotated text; layout mode may silently omit it.
        text = (page.extract_text() or "").strip()
        nonempty += bool(text)
        fence = "`" * max(4, max((len(m[0]) + 1 for m in re.finditer(r"`{3,}", text)), default=4))
        parts.extend([f"## PDF page {number}", "", fence + "text", text or "[No extractable text on this page; consult the PDF.]", fence, ""])
    if not nonempty:
        raise ValueError("PDF has no extractable text; OCR is required before claiming Markdown full text")
    return "\n".join(parts), len(reader.pages)


def within_root(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("File path leaves the repository")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_id")
    parser.add_argument("--retrieved-on", required=True)
    parser.add_argument("--pdf-url")
    parser.add_argument("--markdown-url")
    parser.add_argument("--existing-pdf")
    parser.add_argument("--existing-markdown")
    parser.add_argument("--license-id", default="unconfirmed")
    parser.add_argument("--license-url", default="")
    parser.add_argument("--evidence-url", default="")
    parser.add_argument("--license-file-url")
    parser.add_argument("--version", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--pdf-status", choices=["not_located", "access_blocked", "redistribution_unconfirmed"], default="not_located")
    parser.add_argument("--record-only", action="store_true")
    parser.add_argument("--redistribution-permitted", action="store_true", help="For a record-only item whose license is confirmed but retrieval failed")
    parser.add_argument("--replace", action="store_true", help="Explicitly replace this source's current capture")
    args = parser.parse_args()
    dt.date.fromisoformat(args.retrieved_on)
    registry = json.loads((ROOT / "research/literature/sources.json").read_text(encoding="utf-8"))
    source = next((item for item in registry if item["id"] == args.source_id), None)
    if source is None:
        parser.error("Register the source before archiving it")
    if not re.fullmatch(r"[a-z0-9-]+", args.source_id):
        parser.error("Use the registered safe source identifier")
    manifest_path = ROOT / MANIFEST
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))["sources"] if manifest_path.exists() else []
    if any(entry["source_id"] == args.source_id for entry in entries) and not args.replace:
        parser.error("Source already captured; inspect it and use --replace explicitly if needed")
    if (not args.record_only or args.redistribution_permitted) and (args.license_id == "unconfirmed" or not args.evidence_url):
        parser.error("Full text needs an explicit license and rights-evidence URL")
    if args.record_only and any([args.pdf_url, args.markdown_url, args.existing_pdf, args.existing_markdown]):
        parser.error("A record-only entry cannot claim full-text files")
    if not args.record_only and not any([args.pdf_url, args.markdown_url, args.existing_markdown]):
        parser.error("Provide a full-text source or use --record-only")
    if args.record_only and not args.reason:
        parser.error("Explain why full text is not archived")
    if args.pdf_url and any([args.markdown_url, args.existing_markdown, args.existing_pdf]):
        parser.error("A downloaded PDF already provides both formats; choose one capture method")
    if args.existing_pdf and not args.existing_markdown:
        parser.error("An existing PDF must be accompanied by its Markdown transcription")

    # Complete downloads/conversion before changing the existing inventory.
    payloads: list[tuple[str, bytes, str, dict]] = []
    existing: list[dict] = []
    if args.existing_pdf:
        path = within_root(args.existing_pdf)
        data = path.read_bytes()
        if not data.startswith(b"%PDF-"):
            parser.error("Existing PDF is not a PDF")
        from pypdf import PdfReader
        existing.append(artifact(ROOT, path, "pdf", source["url"], pages=len(PdfReader(io.BytesIO(data)).pages), transformation="Unchanged supplied PDF"))
    if args.existing_markdown:
        path = within_root(args.existing_markdown)
        path.read_text(encoding="utf-8")
        existing.append(artifact(ROOT, path, "markdown", source["url"], transformation="Existing supplied automatic transcription; retained in place"))
    if args.pdf_url:
        from importlib.metadata import version
        data, final_url = download(args.pdf_url)
        md, pages = pdf_markdown(data, source["title"])
        payloads.extend([
            ("source.pdf", data, "pdf", {"origin_url": final_url, "pages": pages, "transformation": "Unchanged original PDF"}),
            ("full-text.md", md.encode("utf-8"), "markdown", {"origin_url": final_url, "pages": pages, "converter": "pypdf", "converter_version": version("pypdf"), "transformation": "pypdf plain-mode text extraction including rotated text; page headings and preformatted text; no scientific review"}),
        ])
    if args.markdown_url:
        data, final_url = download(args.markdown_url)
        text = data.decode("utf-8")
        if text.lstrip().lower().startswith(("<!doctype html", "<html")):
            parser.error("Expected original Markdown, received an HTML response")
        text = resolve_source_links(text, final_url).replace("\r\n", "\n").replace("\r", "\n")
        payloads.append(("full-text.md", text.encode("utf-8"), "markdown", {"origin_url": final_url, "transformation": "Original Markdown snapshot with relative links resolved to source URLs"}))
    if args.license_file_url:
        data, final_url = download(args.license_file_url)
        payloads.append(("LICENSE.txt", data, "license", {"origin_url": final_url, "transformation": "Unchanged upstream license"}))

    folder = ROOT / "research/library" / args.source_id
    folder.mkdir(parents=True, exist_ok=True)
    artifacts = existing
    for name, data, kind, metadata in payloads:
        path = folder / name
        path.write_bytes(data)
        origin_url = metadata.pop("origin_url")
        artifacts.append(artifact(ROOT, path, kind, origin_url, **metadata))
    pdf_present = any(item["kind"] == "pdf" for item in artifacts)
    reason = args.reason or ("Complete PDF and automatic text capture; reading status is unchanged." if pdf_present else "Original Markdown captured. No separate official PDF was located on the inspected source.")
    entry = {
        "source_id": args.source_id,
        "canonical_url": source["url"],
        "retrieved_on": args.retrieved_on,
        "version": args.version,
        "status": "record_only" if args.record_only else "full_text",
        "pdf_status": "archived" if pdf_present else args.pdf_status,
        "rights": {"license_id": args.license_id, "license_url": args.license_url,
                   "evidence_url": args.evidence_url,
                   "redistribution": "permitted" if not args.record_only or args.redistribution_permitted else "unconfirmed"},
        "reason": reason,
        "artifacts": artifacts,
        "record_path": (folder / "README.md").relative_to(ROOT).as_posix(),
    }
    bib = (ROOT / "research/literature/references.bib").read_text(encoding="utf-8")
    bib_match = re.search(r"(?ms)^@\w+\{" + re.escape(args.source_id) + r",\s*\n(.*?)(?=^@|\Z)", bib)
    author_match = re.search(r"author\s*=\s*\{([^}]+)\}", bib_match[1]) if bib_match else None
    attribution = author_match[1] if author_match else "Original project/document contributors; see original authorship and copyright notices."
    lines = [f"# {source['title']}", "", f"- Source ID: `{args.source_id}`",
             f"- Original authors/contributors: {attribution}",
             f"- Canonical source: {source['url']}", f"- Retrieved/checked: {args.retrieved_on}",
             f"- Version: {args.version or 'See source publication / snapshot'}",
             f"- Capture status: `{entry['status']}`; PDF: `{entry['pdf_status']}`",
             f"- Rights/license: {args.license_id}", f"- Rights evidence: {args.evidence_url or 'Not established'}",
             f"- License link: {args.license_url or 'Not established'}", "", reason, "",
             "## Stored files", ""]
    from os.path import relpath
    for item in artifacts:
        relative = relpath(ROOT / item["path"], folder).replace("\\", "/")
        lines.extend([f"- [{item['kind']}]({relative}) — {item['transformation']}",
                      f"  - Source URL: {item['origin_url']}", f"  - SHA-256: `{item['sha256']}`"])
    if not artifacts:
        lines.append("No full-text file is claimed. Retain this acquisition record until a permitted copy is obtained.")
    lines.extend(["", "Archiving/conversion does not establish a completed reading, validate a scientific claim, "
                  "or change the source's original license. Preserve original author and third-party notices.", ""])
    record = folder / "README.md"
    record.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    entry["record_sha256"] = digest(record)
    entries = [old for old in entries if old["source_id"] != args.source_id] + [entry]
    order = {item["id"]: i for i, item in enumerate(registry)}
    entries.sort(key=lambda item: order.get(item["source_id"], len(order)))
    write_catalog(ROOT, entries)
    print(f"Archived {args.source_id}: {entry['status']}, PDF {entry['pdf_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
