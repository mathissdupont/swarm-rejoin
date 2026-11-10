"""Offline source-library indexing and validation (standard library only)."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit


MANIFEST = "research/library/manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_source_links(content: str, source_url: str) -> str:
    """Resolve relative links in a captured native Markdown document."""
    def resolve(target: str) -> str:
        if target.startswith("#") or urlsplit(target).scheme:
            return target
        return urljoin(source_url, target)

    content = re.sub(
        r"(\[[^\]\n]*\]\()([^\s)]+)(\))",
        lambda match: match[1] + resolve(match[2]) + match[3],
        content,
    )
    return re.sub(
        r"(?m)^(\[[^\]\n]+\]:\s*)([^\s]+)",
        lambda match: match[1] + resolve(match[2]),
        content,
    )


def artifact(root: Path, path: Path, kind: str, origin_url: str, **extra: object) -> dict:
    return {
        "kind": kind,
        "path": path.relative_to(root).as_posix(),
        "sha256": digest(path),
        "origin_url": origin_url,
        **extra,
    }


def write_catalog(root: Path, entries: list[dict]) -> None:
    """Write the manifest and linked index; file content is never a review count."""
    library = root / "research/library"
    library.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": "1.0", "sources": entries}
    (root / MANIFEST).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    full = sum(entry["status"] == "full_text" for entry in entries)
    pdfs = sum(entry["pdf_status"] == "archived" for entry in entries)
    lines = [
        "# Research source library", "",
        f"{len(entries)} source records; {full} full-text Markdown captures; "
        f"{pdfs} original PDFs. Counts describe stored material, not completed reviews.", "",
        "Every retained source has a local record. Full text is stored only when "
        "retrieval and redistribution are supported. A record-only item is explicitly "
        "incomplete; it is not a substitute for the full paper.", "",
        "Existing material in Ceren's literature folder is indexed in place to avoid duplicates.", "",
        "| Source | Capture | Original PDF | Status / limitation |",
        "| --- | --- | --- | --- |",
    ]
    for entry in entries:
        by_kind = {item["kind"]: item for item in entry["artifacts"]}
        record = entry["record_path"].removeprefix("research/library/")
        md = by_kind.get("markdown")
        pdf = by_kind.get("pdf")
        md_link = "[Full text](../../" + md["path"] + ")" if md else "Record only"
        pdf_link = "[PDF](../../" + pdf["path"] + ")" if pdf else entry["pdf_status"].replace("_", " ")
        note = entry.get("reason", "").replace("|", "/").replace("\n", " ")
        lines.append(f"| [{entry['source_id']}]({record}) | {md_link} | {pdf_link} | {note} |")
    lines += [
        "", "## Add or update a source", "",
        "1. Register the citation in `research/literature/sources.json`, BibTeX, and the matrix.",
        "2. Capture original Markdown or a complete PDF transcription and an unchanged PDF "
        "when one is available. Follow the [archive workflow](../../docs/10-source-archive.md).",
        "3. Record source URL, version/retrieval date, rights evidence, transformation, "
        "file hashes, and the exact reason for any missing format.",
        "4. Run `python tools/check_repo.py` before committing.", "",
        "The [manifest](manifest.json) is the machine-readable file inventory. "
        "Paper notes, interpretations, and empirical findings remain separate artifacts.", "",
    ]
    (library / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def validate_library(root: Path) -> tuple[list[str], set[str]]:
    """Validate coverage, permission/status claims, paths, signatures, and hashes."""
    errors: list[str] = []
    content_paths: set[str] = set()
    try:
        registry = json.loads((root / "research/literature/sources.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        if manifest.get("schema_version") != "1.0":
            raise ValueError("unsupported source-library schema")
        entries = manifest["sources"]
        if not isinstance(entries, list):
            raise ValueError("source-library entries must be a list")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"Source library: {exc}"], content_paths
    expected = {source["id"] for source in registry}
    seen: set[str] = set()

    def check_file(relative: object, checksum: object, label: str, suffix: str) -> Path | None:
        if not isinstance(relative, str):
            errors.append(f"{label}: missing file path")
            return None
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            errors.append(f"{label}: file leaves workspace")
            return None
        if path.suffix.lower() != suffix or not path.is_file():
            errors.append(f"{label}: missing or incorrectly typed file: {relative}")
            return None
        if digest(path) != checksum:
            errors.append(f"{label}: SHA-256 mismatch: {relative}")
        return path

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("Source library: expected an object")
            continue
        source_id = entry.get("source_id")
        if not isinstance(source_id, str) or source_id not in expected:
            errors.append(f"Source library: unknown source {source_id!r}")
            continue
        if source_id in seen:
            errors.append(f"Source library: duplicate source {source_id}")
        seen.add(source_id)
        check_file(entry.get("record_path"), entry.get("record_sha256"), source_id, ".md")
        try:
            dt.date.fromisoformat(entry.get("retrieved_on", ""))
        except (ValueError, TypeError):
            errors.append(f"{source_id}: invalid archive date")
        if not isinstance(entry.get("canonical_url"), str) or not entry["canonical_url"].startswith("https://"):
            errors.append(f"{source_id}: missing canonical URL")
        status = entry.get("status")
        if status not in {"full_text", "record_only"}:
            errors.append(f"{source_id}: invalid capture status")
        rights = entry.get("rights", {})
        if status == "full_text" and (
            not isinstance(rights, dict)
            or rights.get("redistribution") != "permitted"
            or not rights.get("license_id")
            or not rights.get("evidence_url")
        ):
            errors.append(f"{source_id}: full text requires recorded redistribution evidence")
        items = entry.get("artifacts")
        if not isinstance(items, list):
            errors.append(f"{source_id}: invalid artifacts list")
            continue
        kinds: set[str] = set()
        for item in items:
            if not isinstance(item, dict) or item.get("kind") not in {"markdown", "pdf", "license"}:
                errors.append(f"{source_id}: invalid artifact")
                continue
            kind = item["kind"]
            if kind in kinds:
                errors.append(f"{source_id}: duplicate artifact kind {kind}")
            kinds.add(kind)
            path = check_file(item.get("path"), item.get("sha256"), f"{source_id}/{kind}", ".pdf" if kind == "pdf" else ".md" if kind == "markdown" else ".txt")
            if kind == "markdown" and isinstance(item.get("path"), str):
                content_paths.add(item["path"])
            if kind == "pdf" and path and not path.read_bytes().startswith(b"%PDF-"):
                errors.append(f"{source_id}: PDF artifact is not a PDF")
        if status == "full_text" and "markdown" not in kinds:
            errors.append(f"{source_id}: full text requires a Markdown capture")
        if status == "record_only" and kinds & {"markdown", "pdf"}:
            errors.append(f"{source_id}: record-only status conflicts with full-text artifacts")
        pdf_status = entry.get("pdf_status")
        if pdf_status not in {"archived", "not_located", "access_blocked", "redistribution_unconfirmed"}:
            errors.append(f"{source_id}: invalid PDF status")
        if (pdf_status == "archived") != ("pdf" in kinds):
            errors.append(f"{source_id}: PDF status and artifacts disagree")
        if (status == "record_only" or pdf_status != "archived") and not entry.get("reason"):
            errors.append(f"{source_id}: missing explanation for incomplete formats")
    if seen != expected:
        errors.append(f"Source-library coverage mismatch: {sorted(seen ^ expected)}")
    return errors, content_paths
