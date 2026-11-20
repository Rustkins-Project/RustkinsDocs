"""Extraction YAML stricte et validation des quatre schémas."""

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .model import Issue


SCHEMA_NAMES = {"document": "document", "runbook": "runbook", "adr": "adr", "knowledge": "knowledge"}
FORMATS = FormatChecker()


def valid_port(parsed):
    """Rejeter les ports vides, non numériques ou hors de 1..65535."""
    if parsed.netloc.endswith(":"):
        return False
    try:
        port = parsed.port
    except ValueError:
        return False
    return port is None or 1 <= port <= 65535


@FORMATS.checks("uri")
def absolute_uri(value):
    if not isinstance(value, str) or re.search(r"\s", value):
        return False
    try:
        parsed = urlsplit(value)
        return bool(
            valid_port(parsed)
            and parsed.scheme
            and (parsed.hostname if parsed.scheme in ("http", "https") else parsed.netloc or parsed.path)
        )
    except ValueError:
        return False


class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in result:
                raise yaml.constructor.ConstructorError(
                    None, None, f"clé YAML dupliquée : {key}", key_node.start_mark
                )
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def normalize_dates(value):
    """PyYAML transforme les dates non citées en date ; les schémas attendent ISO 8601."""
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return [normalize_dates(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_dates(item) for key, item in value.items()}
    return value


def parse(text: str, path: str, required: bool = True):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        if required:
            return {}, text, 1, [Issue(path, 1, "frontmatter", "frontmatter YAML manquant")]
        return {}, text, 1, []
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return {}, text, 1, [Issue(path, 1, "frontmatter", "délimiteur de fin --- manquant")]
    yaml_text = "".join(lines[1:close])
    body = "".join(lines[close + 1:])
    try:
        data = yaml.load(yaml_text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 2 if mark else 1
        return {}, body, close + 2, [Issue(path, line, "yaml", str(exc).splitlines()[0])]
    if not isinstance(data, dict):
        return {}, body, close + 2, [Issue(path, 1, "frontmatter", "le YAML doit être un objet")]
    return normalize_dates(data), body, close + 2, []


def load_schemas(root: Path):
    validators = {}
    issues = []
    for kind, name in SCHEMA_NAMES.items():
        path = root / "schemas" / f"{name}.schema.json"
        relative = path.relative_to(root).as_posix()
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validators[kind] = Draft202012Validator(schema, format_checker=FORMATS)
        except (OSError, ValueError, TypeError) as exc:
            issues.append(Issue(relative, None, "schema", f"schéma illisible ou invalide : {exc}"))
        except Exception as exc:  # SchemaError, sans masquer les diagnostics
            issues.append(Issue(relative, None, "schema", f"schéma invalide : {exc}"))
    return validators, issues


def validate_schema(metadata, validator, path: str, text: str):
    issues = []
    lines = text.splitlines()
    for error in sorted(validator.iter_errors(metadata), key=lambda item: (list(map(str, item.path)), item.message)):
        field = str(next(iter(error.path), next(iter(error.schema_path), "frontmatter")))
        line = next((i for i, content in enumerate(lines, 1) if content.startswith(f"{field}:")), 1)
        issues.append(Issue(path, line, "schema", f"{field}: {error.message}"))
    return issues
