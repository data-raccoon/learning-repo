"""Small dependency-free JSON Schema validator for orchestrator contracts."""

from __future__ import annotations

import re
import json
from typing import Any


def strict_json_loads(text: str) -> Any:
    """Parse standards-compliant JSON while rejecting ambiguous object keys."""
    def object_from_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON property: {key}")
            value[key] = item
        return value

    def reject_constant(value: str) -> Any:
        raise ValueError(f"non-standard JSON constant: {value}")

    return json.loads(text, object_pairs_hook=object_from_pairs, parse_constant=reject_constant)


def validate_json_schema(value: Any, schema: dict[str, Any], location: str = "$") -> str:
    """Return the first validation error, or an empty string when valid.

    This intentionally implements the bounded Draft 2020-12 vocabulary used by
    orchestrator schemas rather than silently accepting constraints we cannot
    enforce.
    """
    supported = {
        "$schema", "$id", "title", "description", "type", "const", "enum",
        "properties", "required", "additionalProperties", "items", "minItems",
        "maxItems", "uniqueItems", "minLength", "maxLength", "pattern",
        "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
        "allOf", "anyOf", "oneOf", "not",
    }
    unknown = sorted(set(schema) - supported)
    if unknown:
        return f"{location}: unsupported schema keywords: {', '.join(unknown)}"

    if "const" in schema and value != schema["const"]:
        return f"{location}: value does not equal const"
    if "enum" in schema and value not in schema["enum"]:
        return f"{location}: value is not one of the allowed values"

    for keyword in ("allOf", "anyOf", "oneOf"):
        if keyword not in schema:
            continue
        branches = schema[keyword]
        if not isinstance(branches, list) or not branches or any(not isinstance(item, dict) for item in branches):
            return f"{location}: {keyword} must be a non-empty array of schemas"
        results = [validate_json_schema(value, item, location) for item in branches]
        matched = sum(not result for result in results)
        if keyword == "allOf" and matched != len(branches):
            return next(result for result in results if result)
        if keyword == "anyOf" and matched == 0:
            return f"{location}: value does not match anyOf"
        if keyword == "oneOf" and matched != 1:
            return f"{location}: value must match exactly one oneOf branch"
    if "not" in schema:
        if not isinstance(schema["not"], dict):
            return f"{location}: not must be a schema"
        if not validate_json_schema(value, schema["not"], location):
            return f"{location}: value matches forbidden schema"

    declared = schema.get("type")
    types = (declared,) if isinstance(declared, str) else tuple(declared or ())
    if declared is not None and (not types or any(item not in {"object", "array", "string", "integer", "number", "boolean", "null"} for item in types)):
        return f"{location}: unsupported type declaration"
    matches = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if types and not any(matches[item](value) for item in types):
        return f"{location}: value has the wrong type"

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if not isinstance(properties, dict) or any(not isinstance(item, dict) for item in properties.values()):
            return f"{location}: properties must contain schemas"
        if not isinstance(required, list) or any(not isinstance(item, str) for item in required):
            return f"{location}: required must be an array of strings"
        missing = [name for name in required if name not in value]
        if missing:
            return f"{location}: missing required properties: {', '.join(missing)}"
        extra_schema = schema.get("additionalProperties", {})
        extras = sorted(set(value) - set(properties))
        if extra_schema is False and extras:
            return f"{location}: unexpected properties: {', '.join(extras)}"
        if extra_schema is not False and not isinstance(extra_schema, dict):
            return f"{location}: additionalProperties must be false or a schema"
        for name, item in value.items():
            definition = properties.get(name, extra_schema)
            if definition is False:
                continue
            error = validate_json_schema(item, definition, f"{location}.{name}")
            if error:
                return error

    if isinstance(value, list):
        for keyword, comparison in (("minItems", lambda size, bound: size < bound), ("maxItems", lambda size, bound: size > bound)):
            if keyword in schema and comparison(len(value), schema[keyword]):
                return f"{location}: {keyword} constraint failed"
        if schema.get("uniqueItems") is True and any(value[index] in value[:index] for index in range(len(value))):
            return f"{location}: array items are not unique"
        if "items" in schema:
            if not isinstance(schema["items"], dict):
                return f"{location}: items must be a schema"
            for index, item in enumerate(value):
                error = validate_json_schema(item, schema["items"], f"{location}[{index}]")
                if error:
                    return error

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            return f"{location}: string is shorter than minLength"
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            return f"{location}: string is longer than maxLength"
        if "pattern" in schema:
            try:
                if re.search(schema["pattern"], value) is None:
                    return f"{location}: string does not match pattern"
            except (re.error, TypeError) as error:
                return f"{location}: invalid pattern: {error}"

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        checks = (
            ("minimum", lambda item, bound: item < bound),
            ("maximum", lambda item, bound: item > bound),
            ("exclusiveMinimum", lambda item, bound: item <= bound),
            ("exclusiveMaximum", lambda item, bound: item >= bound),
        )
        for keyword, failed in checks:
            if keyword in schema and failed(value, schema[keyword]):
                return f"{location}: {keyword} constraint failed"
    return ""
