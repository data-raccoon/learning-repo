#!/usr/bin/env python3
"""Read-only semantic validator for EU AI Act dossier-state.json files."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCHEMA_VERSIONS = {"1.0.0", "1.1.0"}
STATES = {"intake", "classification_pending", "drafting", "evidence_pending", "audit_pending", "validation_failed", "dossier_freigabereit", "nicht_freigabefaehig"}
ROLES = {"provider", "deployer", "authorized_representative", "importer", "distributor"}
RISK_ROUTES = {"open", "no_ai_system", "prohibited", "not_high_risk", "annex_iii_exception", "annex_iii_high_risk", "annex_i_high_risk"}
REQUIREMENT_STATUSES = {"open", "requested", "drafted", "evidenced", "verified", "not_applicable"}
DOCUMENT_STATUSES = {"draft", "reviewed", "approved", "external"}
EVIDENCE_STATUSES = {"submitted", "accepted", "rejected"}
SOURCE_TYPES = {"original_document", "system_record", "test_record", "signed_statement", "external_decision", "official_register", "ai_draft"}
CHECKLIST_ANSWERS = {"offen", "ja", "nein", "nicht_anwendbar", "eskalieren"}
CHECKLIST_STATUSES = {"nicht_begonnen", "in_pruefung", "nachweis_fehlt", "erledigt", "eskaliert"}
CHECKLIST_IDS = {
    "BAS-01", "BAS-02", "BAS-03", "BAS-04", "ROL-01",
    "CLS-01", "CLS-02", "CLS-03", "CLS-04", "TRN-01",
    "PRO-01", "PRO-02", "PRO-03", "PRO-04", "PRO-05",
    "DEP-01", "DEP-02", "DEP-03", "CNF-01", "CNF-02",
    "LIF-01", "LIF-02", "LIF-03", "LIF-04", "GAT-01",
}
REQUIRED_TOP_LEVEL = {
    "schemaVersion", "assessmentId", "applicationId", "systemName", "systemVersion",
    "state", "updatedAt", "legalStatus", "useCases", "requirements", "documents",
    "evidence", "review", "release", "remediationPlanPath",
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def check_enum(report: Report, value: Any, allowed: set[str], field: str) -> None:
    if value not in allowed:
        report.error(f"{field} hat den unbekannten Wert {value!r}.")


def check_unique_ids(report: Report, items: list[Any], collection: str) -> set[str]:
    ids = [item.get("id") for item in items if isinstance(item, dict)]
    if len(ids) != len(items) or any(not isinstance(item_id, str) or not item_id for item_id in ids):
        report.error(f"{collection} enthält eine fehlende oder leere ID.")
    duplicates = [item_id for item_id, count in Counter(ids).items() if count > 1]
    for item_id in duplicates:
        report.error(f"{collection} enthält die doppelte ID {item_id!r}.")
    return {item_id for item_id in ids if isinstance(item_id, str) and item_id}


def check_required_keys(report: Report, item: Any, required: set[str], field: str) -> None:
    if not isinstance(item, dict):
        report.error(f"{field} muss ein Objekt sein.")
        return
    for key in sorted(required - item.keys()):
        report.error(f"Pflichtfeld {field}.{key} fehlt.")


def safe_relative_path(report: Report, root: Path, value: Any, field: str, must_exist: bool) -> None:
    if value in (None, ""):
        return
    if not isinstance(value, str):
        report.error(f"{field} muss ein String sein.")
        return
    normalized = value.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
        report.error(f"{field} muss ein normalisierter relativer Pfad sein: {value!r}.")
        return
    if must_exist and not (root / Path(*pure.parts)).is_file():
        report.error(f"{field} verweist auf eine fehlende Datei: {value!r}.")


def validate(data: dict[str, Any], state_path: Path) -> Report:
    report = Report()
    missing = sorted(REQUIRED_TOP_LEVEL - data.keys())
    for field in missing:
        report.error(f"Pflichtfeld {field!r} fehlt.")
    if missing:
        return report

    version = data.get("schemaVersion")
    check_enum(report, version, SCHEMA_VERSIONS, "schemaVersion")
    check_enum(report, data.get("state"), STATES, "state")

    use_cases = as_list(data.get("useCases"))
    requirements = as_list(data.get("requirements"))
    documents = as_list(data.get("documents"))
    evidence = as_list(data.get("evidence"))
    if len(use_cases) != 1:
        report.error("useCases muss genau einen Eintrag enthalten.")

    use_case_ids = check_unique_ids(report, use_cases, "useCases")
    requirement_ids = check_unique_ids(report, requirements, "requirements")
    document_ids = check_unique_ids(report, documents, "documents")
    evidence_ids = check_unique_ids(report, evidence, "evidence")
    all_ids = list(use_case_ids) + list(requirement_ids) + list(document_ids) + list(evidence_ids)
    for item_id, count in Counter(all_ids).items():
        if count > 1:
            report.error(f"ID {item_id!r} wird in mehreren Dossier-Sammlungen verwendet.")

    for use_case in use_cases:
        if not isinstance(use_case, dict):
            report.error("useCases enthält einen Nicht-Objekt-Eintrag.")
            continue
        check_enum(report, use_case.get("riskRoute"), RISK_ROUTES, f"useCases[{use_case.get('id')}].riskRoute")
        for role in as_list(use_case.get("roles")):
            check_enum(report, role, ROLES, f"useCases[{use_case.get('id')}].roles")

    for item in requirements:
        if not isinstance(item, dict):
            report.error("requirements enthält einen Nicht-Objekt-Eintrag.")
            continue
        item_id = item.get("id")
        check_enum(report, item.get("status"), REQUIREMENT_STATUSES, f"requirements[{item_id}].status")
        for ref in as_list(item.get("documentIds")):
            if ref not in document_ids:
                report.error(f"Anforderung {item_id!r} referenziert unbekanntes Dokument {ref!r}.")
        for ref in as_list(item.get("evidenceIds")):
            if ref not in evidence_ids:
                report.error(f"Anforderung {item_id!r} referenziert unbekannte Evidenz {ref!r}.")

    root = state_path.parent
    for item in documents:
        if not isinstance(item, dict):
            report.error("documents enthält einen Nicht-Objekt-Eintrag.")
            continue
        item_id = item.get("id")
        check_enum(report, item.get("status"), DOCUMENT_STATUSES, f"documents[{item_id}].status")
        safe_relative_path(report, root, item.get("path"), f"documents[{item_id}].path", True)
    for item in evidence:
        if not isinstance(item, dict):
            report.error("evidence enthält einen Nicht-Objekt-Eintrag.")
            continue
        item_id = item.get("id")
        check_enum(report, item.get("status"), EVIDENCE_STATUSES, f"evidence[{item_id}].status")
        check_enum(report, item.get("sourceType"), SOURCE_TYPES, f"evidence[{item_id}].sourceType")
        safe_relative_path(report, root, item.get("path"), f"evidence[{item_id}].path", True)

    review = data.get("review") if isinstance(data.get("review"), dict) else {}
    release = data.get("release") if isinstance(data.get("release"), dict) else {}
    safe_relative_path(report, root, review.get("reportPath"), "review.reportPath", False)
    safe_relative_path(report, root, release.get("protocolPath"), "release.protocolPath", False)
    safe_relative_path(report, root, data.get("remediationPlanPath"), "remediationPlanPath", False)

    if version == "1.1.0":
        checklist = as_list(data.get("checklistItems"))
        checklist_ids = check_unique_ids(report, checklist, "checklistItems")
        for item_id in checklist_ids & set(all_ids):
            report.error(f"ID {item_id!r} wird zugleich als Stamm- und Dossier-ID verwendet.")
        if len(checklist) != 25:
            report.error(f"checklistItems muss 25 Einträge enthalten, gefunden: {len(checklist)}.")
        for item_id in sorted(CHECKLIST_IDS - checklist_ids):
            report.error(f"Stamm-ID {item_id!r} fehlt.")
        mapped: set[str] = set()
        for item in checklist:
            if not isinstance(item, dict):
                report.error("checklistItems enthält einen Nicht-Objekt-Eintrag.")
                continue
            item_id = item.get("id")
            check_required_keys(report, item, {"id", "answer", "status", "rationale", "evidenceLinks", "owner", "dueAt", "legalReferences", "requirementIds"}, f"checklistItems[{item_id}]")
            check_enum(report, item.get("answer"), CHECKLIST_ANSWERS, f"checklistItems[{item_id}].answer")
            check_enum(report, item.get("status"), CHECKLIST_STATUSES, f"checklistItems[{item_id}].status")
            for ref in as_list(item.get("requirementIds")):
                mapped.add(ref)
                if ref not in requirement_ids:
                    report.error(f"Stamm-ID {item_id!r} referenziert unbekannte Anforderung {ref!r}.")
        for item_id in sorted(requirement_ids - mapped):
            report.error(f"Anforderung {item_id!r} ist keiner Stamm-ID zugeordnet.")
    elif version == "1.0.0":
        report.warning("Schema 1.0.0 ist kompatibel lesbar; checklistItems und audit_pending stehen erst ab 1.1.0 zur Verfügung.")

    state = data.get("state")
    closed_requirements = {"verified", "not_applicable"}
    if state in {"audit_pending", "dossier_freigabereit"}:
        if any(item.get("status") not in closed_requirements for item in requirements if isinstance(item, dict)):
            report.error(f"{state} verlangt geschlossene Anforderungen.")
        if any(item.get("status") == "draft" for item in documents if isinstance(item, dict)):
            report.error(f"{state} erlaubt keine Dokumente im Status draft.")
    if state == "dossier_freigabereit":
        use_case = use_cases[0] if len(use_cases) == 1 and isinstance(use_cases[0], dict) else {}
        if not use_case.get("classificationFinal") or use_case.get("riskRoute") == "open" or not as_list(use_case.get("roles")):
            report.error("Freigabereife verlangt endgültige Klassifizierung, geschlossenen Risikopfad und mindestens eine Rolle.")
        if review.get("result") != "passed" or review.get("consistencyCheck") != "passed" or review.get("criticalFindings") != 0 or not review.get("reviewer") or not review.get("completedAt"):
            report.error("Freigabereife verlangt einen bestandenen, namentlichen Review ohne kritische Befunde.")
        if release.get("status") != "pending":
            report.error("release.status muss bis zur menschlichen Entscheidung pending bleiben.")
        accepted_evidence = {item.get("id") for item in evidence if isinstance(item, dict) and item.get("status") == "accepted" and item.get("sourceType") != "ai_draft"}
        for item in requirements:
            if not isinstance(item, dict):
                continue
            if item.get("status") == "not_applicable" and not str(item.get("rationale", "")).strip():
                report.error(f"Nichtanwendbarkeit von {item.get('id')!r} benötigt eine substanzielle Begründung.")
            if item.get("status") == "verified" and not (set(as_list(item.get("evidenceIds"))) & accepted_evidence):
                report.error(f"Verifizierte Anforderung {item.get('id')!r} benötigt mindestens einen akzeptierten Tatsachennachweis.")
        for item in documents:
            if isinstance(item, dict) and (not str(item.get("version", "")).strip() or not str(item.get("owner", "")).strip()):
                report.error(f"Dokument {item.get('id')!r} benötigt Version und Owner.")
        legal_date = str(data.get("legalStatus", {}).get("checkedAt", ""))[:10]
        review_date = str(review.get("completedAt", ""))[:10]
        if not legal_date or not review_date or legal_date != review_date:
            report.error("Der Rechtsstand muss am Tag des Abschlussaudits geprüft sein.")
        safe_relative_path(report, root, review.get("reportPath"), "review.reportPath", True)
        safe_relative_path(report, root, release.get("protocolPath"), "release.protocolPath", True)
    if state == "nicht_freigabefaehig":
        safe_relative_path(report, root, review.get("reportPath"), "review.reportPath", True)
        remediation = data.get("remediationPlanPath")
        if not remediation:
            report.error("Nicht-Freigabefähigkeit verlangt remediationPlanPath.")
        else:
            safe_relative_path(report, root, remediation, "remediationPlanPath", True)
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Pfad zu dossier-state.json")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: Zustandsdatei konnte nicht gelesen werden: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("ERROR: Die JSON-Wurzel muss ein Objekt sein.", file=sys.stderr)
        return 2
    report = validate(data, args.path.resolve())
    for warning in report.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in report.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if report.errors:
        return 1
    print(f"VALID: {data.get('assessmentId')} (Schema {data.get('schemaVersion')}, Zustand {data.get('state')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
