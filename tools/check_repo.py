"""Check the research scaffold offline; this is not scientific validation."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from source_library import validate_library


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_KINDS = {
    "journal_article",
    "conference_paper",
    "specification",
    "informational_rfc",
    "technical_guideline",
    "official_documentation",
}
ALLOWED_REVIEWS = {
    "seed_abstract",
    "seed_partial_text",
    "seed_selected_sections",
    "full_review",
}
POLICIES = {"B0", "B1", "B2", "B3", "P"}


def read_json(relative_path: str, errors: list[str]) -> object:
    try:
        return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"{relative_path}: {exc}")
        return None


def check_sources(errors: list[str]) -> set[str]:
    sources = read_json("research/literature/sources.json", errors)
    if not isinstance(sources, list):
        errors.append("Source registry must be a list.")
        return set()
    ids: set[str] = set()
    dois: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"Source {index}: expected an object.")
            continue
        source_id = source.get("id", "")
        if not isinstance(source_id, str) or not re.fullmatch(r"[a-z0-9-]+", source_id):
            errors.append(f"Source {index}: invalid identifier.")
            continue
        if source_id in ids:
            errors.append(f"Duplicate source: {source_id}")
        ids.add(source_id)
        for field in ("title", "url", "accessed_material", "proposed_lead"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                errors.append(f"{source_id}: missing or invalid {field}.")
        url = source.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"{source_id}: expected an HTTPS source URL.")
        year = source.get("year")
        if "year" not in source or (year is not None and (type(year) is not int or year < 1900)):
            errors.append(f"{source_id}: year must be an integer or explicit null.")
        try:
            dt.date.fromisoformat(source.get("verified_on", ""))
        except (TypeError, ValueError):
            errors.append(f"{source_id}: invalid verification date.")
        if source.get("kind") not in ALLOWED_KINDS:
            errors.append(f"{source_id}: unknown source kind.")
        review = source.get("review_status")
        if review not in ALLOWED_REVIEWS:
            errors.append(f"{source_id}: unknown review status.")
        completed = source.get("full_text_review_complete")
        if type(completed) is not bool:
            errors.append(f"{source_id}: full review flag must be Boolean.")
        elif completed != (review == "full_review"):
            errors.append(f"{source_id}: review status and full review flag disagree.")
        doi = source.get("doi")
        if doi is not None:
            if not isinstance(doi, str) or not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
                errors.append(f"{source_id}: invalid DOI syntax.")
            elif doi.lower() in dois:
                errors.append(f"{source_id}: duplicate DOI.")
            else:
                dois.add(doi.lower())

    bib = (ROOT / "research/literature/references.bib").read_text(encoding="utf-8")
    bib_entries = re.findall(r"^@\w+\s*\{\s*([^,\s]+)\s*,", bib, re.MULTILINE)
    if len(bib_entries) != len(set(bib_entries)):
        errors.append("Duplicate bibliography identifiers.")
    if set(bib_entries) != ids:
        errors.append(f"Registry/BibTeX mismatch: {sorted(set(bib_entries) ^ ids)}")
    matrix = (ROOT / "research/literature/matrix.md").read_text(encoding="utf-8")
    for source_id in ids:
        if f"`{source_id}`" not in matrix:
            errors.append(f"Matrix missing source: {source_id}")
    return ids


def check_scenarios(source_ids: set[str], errors: list[str]) -> int:
    catalog = read_json("experiments/scenarios.json", errors)
    if not isinstance(catalog, dict):
        errors.append("Scenario catalog must be an object.")
        return 0
    if catalog.get("status") != "design_only":
        errors.append("Scenario catalog status changed; revise this checker for implemented experiments.")
    if catalog.get("schema_version") != "0.1":
        errors.append("Unknown scenario catalog version.")
    agent_count = catalog.get("default_agent_count")
    if type(agent_count) is not int or not 5 <= agent_count <= 8:
        errors.append("Default agent count must match the proposed 5–8 agent scope.")
    policy_ids = catalog.get("policy_ids", [])
    if not isinstance(policy_ids, list) or any(not isinstance(item, str) for item in policy_ids):
        errors.append("Policy identifiers must be a list of strings.")
    elif set(policy_ids) != POLICIES or len(policy_ids) != len(POLICIES):
        errors.append("Policy catalog disagrees with the evaluation plan.")
    threat_model = (ROOT / "docs/05-threat-model.md").read_text(encoding="utf-8")
    invariants = set(re.findall(r"\*\*(I\d+):\*\*", threat_model))
    scenarios = catalog.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("Expected a nonempty scenario list.")
        return 0
    seen: set[str] = set()
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"Scenario {index}: expected an object.")
            continue
        scenario_id = scenario.get("id", "")
        if not isinstance(scenario_id, str) or not re.fullmatch(r"S\d{2,}", scenario_id):
            errors.append(f"Scenario {index}: invalid identifier.")
            continue
        if scenario_id in seen:
            errors.append(f"Duplicate scenario: {scenario_id}")
        seen.add(scenario_id)
        for field in ("name", "family"):
            if not isinstance(scenario.get(field), str) or not scenario[field].strip():
                errors.append(f"{scenario_id}: invalid {field}.")
        for field in ("faults", "questions", "required_invariants", "supporting_sources"):
            items = scenario.get(field)
            if not isinstance(items, list) or any(not isinstance(item, str) or not item.strip() for item in items):
                errors.append(f"{scenario_id}: {field} must be a string list.")
                continue
            if field in {"questions", "required_invariants"} and not items:
                errors.append(f"{scenario_id}: {field} cannot be empty.")
            if field == "required_invariants" and not set(items) <= invariants:
                errors.append(f"{scenario_id}: unknown invariant reference.")
            if field == "supporting_sources" and not set(items) <= source_ids:
                errors.append(f"{scenario_id}: unknown source reference.")
    return len(scenarios)


def check_local_links(errors: list[str], captured_paths: set[str]) -> int:
    checked = 0
    for path in ROOT.rglob("*.md"):
        if any(part.startswith(".") and part != ".github" for part in path.relative_to(ROOT).parts):
            continue
        # Captured upstream documents are not repository-authored links. Their file
        # identity and provenance are checked by the source-library validator.
        if path.relative_to(ROOT).as_posix() in captured_paths:
            continue
        content = path.read_text(encoding="utf-8")
        content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
            target = target.strip().strip("<>")
            if target.startswith("#") or urlsplit(target).scheme:
                continue
            local = unquote(target.split("#", 1)[0])
            if not local:
                continue
            destination = (path.parent / local).resolve()
            if not destination.is_relative_to(ROOT):
                errors.append(f"{path.relative_to(ROOT)}: link leaves the workspace: {target}")
            elif not destination.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken local link: {target}")
            checked += 1
    return checked


def main() -> int:
    errors: list[str] = []
    source_ids = check_sources(errors)
    scenario_count = check_scenarios(source_ids, errors)
    library_errors, captured_paths = validate_library(ROOT)
    errors.extend(library_errors)
    link_count = check_local_links(errors, captured_paths)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(source_ids)} sources and library records, {scenario_count} planned scenarios, {link_count} local links.")
    print("Offline consistency only; no live source, scientific, cryptographic, or flight validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
