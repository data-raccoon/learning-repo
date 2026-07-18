#!/usr/bin/env python3
"""Split a Tana workspace JSON export into navigable, lossless categories."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "sEMlGR0Ne6_M@2026-07-17.json"
DEFAULT_OUTPUT = SCRIPT_DIR / "sEMlGR0Ne6_M@2026-07-17-split"

CATEGORY_ORDER = (
    "workspace-root",
    "main-content",
    "root-content",
    "library",
    "schema",
    "workspace-internals",
    "trash",
    "system",
    "unlinked",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split a Tana workspace export by its ownership tree."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Tana JSON export (default: {DEFAULT_INPUT.name})",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT.name})",
    )
    return parser.parse_args()


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def created_utc(milliseconds: Any) -> str:
    if milliseconds is None:
        return ""
    try:
        return datetime.fromtimestamp(
            int(milliseconds) / 1000, tz=timezone.utc
        ).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    except (TypeError, ValueError, OverflowError, OSError):
        return ""


def find_workspace_root(docs: list[dict[str, Any]]) -> str:
    for doc in docs:
        name = doc.get("props", {}).get("name", "")
        if name.startswith("Root node for file:"):
            return doc["id"]
    raise ValueError("Could not identify the Tana workspace root")


def classify_docs(
    docs: list[dict[str, Any]], workspace_root_id: str
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    by_id = {doc["id"]: doc for doc in docs}
    groups = {category: [] for category in CATEGORY_ORDER}
    category_by_id: dict[str, str] = {}

    special_categories = {
        f"{workspace_root_id}_SCHEMA": "schema",
        f"{workspace_root_id}_TRASH": "trash",
        f"{workspace_root_id}_STASH": "library",
    }
    workspace_internal_ids = {
        f"{workspace_root_id}_{suffix}"
        for suffix in (
            "CAPTURE_INBOX",
            "SEARCHES",
            "MOVETO",
            "WORKSPACE",
            "CHATDRAFTS",
            "SIDEBAR_AREAS",
            "QUICK_ADD",
            "AVATAR",
            "USERS",
        )
    }

    def find_category(start_doc: dict[str, Any]) -> str:
        start_id = start_doc["id"]
        if start_id in category_by_id:
            return category_by_id[start_id]
        if start_id == workspace_root_id:
            return "workspace-root"

        cursor = start_doc
        visited: set[str] = set()
        for _ in range(200):
            cursor_id = cursor["id"]
            if cursor_id in visited:
                return "unlinked"
            visited.add(cursor_id)

            owner_id = cursor.get("props", {}).get("_ownerId")
            if not owner_id:
                return "system" if cursor_id.startswith("SYS") else "unlinked"
            if owner_id not in by_id:
                return "unlinked"

            if owner_id == workspace_root_id:
                top_id = cursor_id
                if top_id in special_categories:
                    return special_categories[top_id]
                if top_id in workspace_internal_ids:
                    return "workspace-internals"
                if cursor.get("props", {}).get("_docType") == "home":
                    return "main-content"
                return "root-content"

            cursor = by_id[owner_id]

        return "unlinked"

    for doc in docs:
        category = find_category(doc)
        category_by_id[doc["id"]] = category
        groups[category].append(doc)

    return groups, category_by_id


def write_index(
    path: Path,
    docs: list[dict[str, Any]],
    category_by_id: dict[str, str],
) -> None:
    columns = (
        "id",
        "category",
        "name",
        "docType",
        "ownerId",
        "sourceId",
        "metaNodeId",
        "childCount",
        "createdUtc",
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for doc in docs:
            props = doc.get("props", {})
            writer.writerow(
                {
                    "id": doc["id"],
                    "category": category_by_id[doc["id"]],
                    "name": props.get("name", ""),
                    "docType": props.get("_docType", ""),
                    "ownerId": props.get("_ownerId", ""),
                    "sourceId": props.get("_sourceId", ""),
                    "metaNodeId": props.get("_metaNodeId", ""),
                    "childCount": len(doc.get("children", [])),
                    "createdUtc": created_utc(props.get("created")),
                }
            )


def build_readme(
    source_name: str,
    workspace_root_id: str,
    groups: dict[str, list[dict[str, Any]]],
    doc_count: int,
    supertag_count: int,
) -> str:
    descriptions = {
        "workspace-root": "The workspace root record",
        "main-content": "Content owned by the main Tana home/workspace",
        "root-content": "User-created records attached directly to the workspace root",
        "library": "Tana Library/Stash content",
        "schema": "User supertags, fields, and their supporting records",
        "workspace-internals": "Searches, layouts, sidebar, users, inbox, and workspace machinery",
        "trash": "Deleted nodes and everything owned beneath the Trash root",
        "system": "Built-in Tana system definitions and values",
        "unlinked": "Records with no resolvable ownership path to the workspace root",
    }
    rows = [
        "| `00-metadata.json` | - | Export-level metadata, editors, and version information |"
    ]
    for number, category in enumerate(CATEGORY_ORDER, start=1):
        rows.append(
            f"| `{number:02d}-{category}.json` | {len(groups[category])} | "
            f"{descriptions[category]} |"
        )
    rows.extend(
        (
            f"| `docs-index.csv` | {doc_count} | Flat searchable index of every record |",
            f"| `user-supertags.json` | {supertag_count} | Compact list of non-system supertag definitions |",
            "| `manifest.json` | - | Machine-readable file list and verification totals |",
        )
    )

    return f"""# Split Tana workspace export

Source: `{source_name}`  
Workspace root: `{workspace_root_id}`  
Records: {doc_count}

Every record from the original `docs` array appears exactly once in the numbered JSON files. IDs and all relationship fields are unchanged, so references can cross file boundaries.

## Files

| File | Records | Meaning |
|---|---:|---|
{chr(10).join(rows)}

## How relationships work

- `id` uniquely identifies a record.
- `children` contains ordered IDs displayed beneath a node.
- `props._ownerId` is the ownership/containment parent used for this split.
- `props._sourceId` points to a source/template record, often a supertag or system field.
- `props._metaNodeId` points to hidden metadata attached to a visible node.
- `tuple` records usually encode a field/value pair; `metanode` records hold metadata.

These split files are for analysis and navigation. Keep the original export as the authoritative backup and use it—not the split files—if you need to re-import into Tana.
"""


def split_export(input_path: Path, output_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as handle:
        export = json.load(handle)

    docs = export.get("docs")
    if not isinstance(docs, list):
        raise ValueError("Input JSON does not contain a 'docs' array")

    workspace_root_id = find_workspace_root(docs)
    groups, category_by_id = classify_docs(docs, workspace_root_id)
    output_path.mkdir(parents=True, exist_ok=True)

    metadata = {
        "source": input_path.name,
        "splitAt": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "workspaceRootId": workspace_root_id,
        "formatVersion": export.get("formatVersion"),
        "lastTxid": export.get("lastTxid"),
        "lastFbKey": export.get("lastFbKey"),
        "editors": export.get("editors", []),
        "optimisticTransIds": export.get("optimisticTransIds", []),
        "workspaces": export.get("workspaces", {}),
        "originalDocCount": len(docs),
    }
    write_json(output_path / "00-metadata.json", metadata)

    manifest_groups = []
    for number, category in enumerate(CATEGORY_ORDER, start=1):
        file_name = f"{number:02d}-{category}.json"
        category_docs = groups[category]
        write_json(
            output_path / file_name,
            {
                "source": input_path.name,
                "category": category,
                "docCount": len(category_docs),
                "docs": category_docs,
            },
        )
        manifest_groups.append(
            {"category": category, "file": file_name, "docCount": len(category_docs)}
        )

    write_index(output_path / "docs-index.csv", docs, category_by_id)

    user_supertags = sorted(
        (
            {
                "id": doc["id"],
                "name": doc.get("props", {}).get("name", ""),
                "category": category_by_id[doc["id"]],
                "ownerId": doc.get("props", {}).get("_ownerId", ""),
            }
            for doc in docs
            if doc.get("props", {}).get("_docType") == "tagDef"
            and not doc["id"].startswith("SYS")
        ),
        key=lambda item: item["name"].casefold(),
    )
    write_json(output_path / "user-supertags.json", user_supertags)

    split_ids = [doc["id"] for category in CATEGORY_ORDER for doc in groups[category]]
    input_ids = [doc["id"] for doc in docs]
    if len(split_ids) != len(input_ids):
        raise RuntimeError(
            f"Verification failed: input has {len(input_ids)} docs, split has {len(split_ids)}"
        )
    if len(set(split_ids)) != len(split_ids):
        raise RuntimeError("Verification failed: duplicate IDs exist in split output")
    if set(split_ids) != set(input_ids):
        raise RuntimeError("Verification failed: split and input ID sets differ")

    manifest = {
        "source": input_path.name,
        "workspaceRootId": workspace_root_id,
        "originalDocCount": len(docs),
        "splitDocCount": len(split_ids),
        "uniqueIdCount": len(set(split_ids)),
        "groups": manifest_groups,
    }
    write_json(output_path / "manifest.json", manifest)
    (output_path / "README.md").write_text(
        build_readme(
            input_path.name,
            workspace_root_id,
            groups,
            len(docs),
            len(user_supertags),
        ),
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    manifest = split_export(input_path, output_path)

    print(
        f"Split {manifest['originalDocCount']} Tana records into "
        f"{len(manifest['groups'])} categories at:\n{output_path}"
    )
    for group in manifest["groups"]:
        print(f"  {group['category']:<20} {group['docCount']:>5}")


if __name__ == "__main__":
    main()
