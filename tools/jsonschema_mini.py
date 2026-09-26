#!/usr/bin/env python3
"""A deliberately small JSON Schema 2020-12 subset validator, standard library only.

Why this exists rather than `pip install jsonschema`:

  The repository's offline verification must run in a container with no egress.
  A validator that cannot run in the environment where the evidence is produced
  is not a gate, it is a suggestion.

What it supports, and nothing else:

  type, const, enum, required, properties, additionalProperties (bool),
  items, minItems, uniqueItems, minLength, maxLength, pattern,
  minimum, maximum, oneOf, anyOf, allOf, not, if/then/else,
  $ref to "#/$defs/..." and to "<file>#/$defs/...".

Anything a schema uses that is NOT in that list raises UnsupportedKeyword.
That is the important design decision: an unsupported keyword must fail loudly,
because a validator that silently ignores a constraint reports PASS for a
document it never checked, and a green light nobody checked is worse than no
light at all.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SUPPORTED = {
    "$schema", "$id", "$defs", "$ref", "title", "description", "examples", "default",
    "type", "const", "enum", "required", "properties", "additionalProperties",
    "items", "minItems", "uniqueItems", "minLength", "maxLength", "pattern",
    "minimum", "maximum", "oneOf", "anyOf", "allOf", "not", "if", "then", "else",
}

TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "integer": int, "number": (int, float), "null": type(None),
}


class UnsupportedKeyword(Exception):
    pass


class SchemaStore:
    """Loads schema files lazily so a relative $ref resolves against the schema dir."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self._cache: dict[str, dict] = {}

    def load(self, filename: str) -> dict:
        if filename not in self._cache:
            self._cache[filename] = json.loads((self.root / filename).read_text(encoding="utf-8"))
        return self._cache[filename]


def _type_ok(value, expected: str) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    py = TYPES.get(expected)
    if py is None:
        raise UnsupportedKeyword(f"unknown type '{expected}'")
    if expected in ("string", "array", "object"):
        return isinstance(value, py)
    return isinstance(value, py)


def _resolve(ref: str, current: dict, store: SchemaStore) -> tuple[dict, dict]:
    """Returns (subschema, the document it came from) so nested $refs resolve correctly."""
    if ref.startswith("#/"):
        doc = current
        pointer = ref[2:]
    else:
        filename, _, pointer = ref.partition("#/")
        doc = store.load(filename)
    node = doc
    for part in pointer.split("/"):
        if part:
            node = node[part]
    return node, doc


def validate(instance, schema: dict, store: SchemaStore, doc: dict | None = None,
             path: str = "$") -> list[str]:
    """Returns a list of human-readable errors. Empty list means valid."""
    doc = doc if doc is not None else schema
    errors: list[str] = []

    unknown = set(schema) - SUPPORTED
    if unknown:
        raise UnsupportedKeyword(f"{path}: schema uses unsupported keyword(s) {sorted(unknown)}")

    if "$ref" in schema:
        sub, subdoc = _resolve(schema["$ref"], doc, store)
        return validate(instance, sub, store, subdoc, path)

    if "type" in schema:
        expected = schema["type"]
        options = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(instance, t) for t in options):
            errors.append(f"{path}: expected type {expected}, got {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: longer than maxLength {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: has {len(instance)} item(s), minItems is {schema['minItems']}")
        if schema.get("uniqueItems"):
            seen = [json.dumps(i, sort_keys=True) for i in instance]
            if len(set(seen)) != len(seen):
                errors.append(f"{path}: items are not unique")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors += validate(item, schema["items"], store, doc, f"{path}[{i}]")

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property '{key}'")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in instance:
                errors += validate(instance[key], sub, store, doc, f"{path}.{key}")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: additional property '{key}' is not allowed")

    for keyword in ("allOf",):
        for i, sub in enumerate(schema.get(keyword, [])):
            errors += validate(instance, sub, store, doc, f"{path}({keyword}[{i}])")
    if "anyOf" in schema:
        if not any(not validate(instance, s, store, doc, path) for s in schema["anyOf"]):
            errors.append(f"{path}: does not match any schema in anyOf")
    if "oneOf" in schema:
        matched = sum(1 for s in schema["oneOf"] if not validate(instance, s, store, doc, path))
        if matched != 1:
            errors.append(f"{path}: matched {matched} schemas in oneOf, expected exactly 1")
    if "not" in schema and not validate(instance, schema["not"], store, doc, path):
        errors.append(f"{path}: must not match the 'not' schema")
    if "if" in schema:
        branch = "then" if not validate(instance, schema["if"], store, doc, path) else "else"
        if branch in schema:
            errors += validate(instance, schema[branch], store, doc, path)

    return errors
