"""Deterministic conversion of validated worker JSON into a target artifact."""

from __future__ import annotations

from pathlib import Path
from string import Formatter
from typing import Any

from .contracts import ContractError, Materialization


def render_materialization(value: Any, contract: Materialization) -> str:
    if not isinstance(value, dict):
        raise ContractError("materialization requires a JSON object output")
    scalar = (str, int, float, bool)
    formatter = Formatter()
    for _, field_name, format_spec, conversion in formatter.parse(contract.template):
        if field_name is None:
            continue
        if not field_name or "." in field_name or "[" in field_name or format_spec or conversion:
            raise ContractError("materialization template permits only direct fields without formatting")
        if field_name not in value:
            raise ContractError(f"materialization field is missing: {field_name}")
        if not isinstance(value[field_name], scalar):
            raise ContractError(f"materialization field must be scalar: {field_name}")
    try:
        return contract.template.format_map(value)
    except (KeyError, ValueError) as error:
        raise ContractError(f"cannot render materialization: {error}") from error


def materialize(path: Path, value: Any, contract: Materialization) -> dict[str, Any]:
    rendered = render_materialization(value, contract)
    if contract.operation == "append":
        if not path.is_file():
            raise ContractError(f"append target does not exist: {contract.path}")
        with path.open("a", encoding="utf-8", newline="") as stream:
            stream.write(rendered)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8", newline="")
    return {"ok": True, "path": contract.path, "operation": contract.operation, "bytes_written": len(rendered.encode("utf-8"))}
