"""Découverte, références, graphe ADR et conservation des identifiants."""

import re
import subprocess
from pathlib import Path

from .frontmatter import load_schemas, parse, validate_schema
from .links import check_links
from .model import Document, Issue


PRODUCT_VERSIONS = frozenset({"V0", "V1", "V2", "V3", "all"})
PREFIX = {"document": "DOC", "runbook": "RUN", "adr": "ADR", "knowledge": "KNOW"}
LOCATION_TYPES = {
    "architecture": "architecture", "specifications": "specification", "conventions": "convention",
    "project-management": "project-management", "versions": "version", "cross-cutting": "cross-cutting",
}
IDENTITY = re.compile(r"^(DOC|RUN|ADR|KNOW)-[0-9]{4,}$")
OBSOLETE = {"document": "deprecated", "runbook": "deprecated", "adr": "superseded", "knowledge": "outdated"}


def discover(root: Path):
    paths = []
    for directory, kind in (("docs", "document"), ("decisions", "adr"), ("knowledge", "knowledge")):
        folder = root / directory
        if not folder.exists():
            continue
        for path in folder.rglob("*.md"):
            if path.name.lower() == "readme.md":
                paths.append((path, "navigation"))
            elif directory == "docs" and path.relative_to(folder).parts[0] == "operations":
                paths.append((path, "runbook"))
            else:
                paths.append((path, kind))
    for name in ("README.md", "INDEX.md"):
        if (root / name).is_file():
            paths.append((root / name, "navigation"))
    for kind in PREFIX:
        paths.append((root / "templates" / f"{kind}.md", f"template:{kind}"))
    return sorted(paths, key=lambda item: str(item[0]))


def read_documents(root: Path, validators):
    documents, issues = [], []
    for path, kind in discover(root):
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append(Issue(relative, None, "lecture", str(exc)))
            continue
        schema_kind = kind.split(":")[-1]
        metadata, body, body_line, parse_issues = parse(text, relative, kind != "navigation")
        issues.extend(parse_issues)
        document = Document(path, schema_kind if kind.startswith("template:") else kind, metadata, body, body_line)
        documents.append(document)
        if kind == "navigation" or parse_issues:
            continue
        validator = validators.get(schema_kind)
        if validator:
            issues.extend(validate_schema(metadata, validator, relative, text))
        identifier = document.identity
        if identifier and IDENTITY.fullmatch(identifier):
            expected = PREFIX[schema_kind]
            if identifier.split("-", 1)[0] != expected:
                issues.append(Issue(relative, 2, "id", f"identifiant {identifier} incompatible avec {schema_kind} (attendu {expected})"))
            if kind.startswith("template:"):
                if int(identifier.split("-", 1)[1]) != 0:
                    issues.append(Issue(relative, 2, "id", "le template doit utiliser l'identifiant réservé 0000"))
            elif int(identifier.split("-", 1)[1]) == 0:
                issues.append(Issue(relative, 2, "id", "identifiant 0000 réservé aux templates"))
        versions = metadata.get("applies_to")
        if isinstance(versions, list):
            for value in versions:
                if isinstance(value, str) and value not in PRODUCT_VERSIONS:
                    issues.append(Issue(relative, None, "version", f"version produit inconnue : {value}"))
            if "all" in versions and len(versions) != 1:
                issues.append(Issue(relative, None, "version", "all doit être la seule valeur de applies_to"))
        if kind == "document":
            parts = path.relative_to(root / "docs").parts
            expected_type = LOCATION_TYPES.get(parts[0])
            if expected_type and metadata.get("type") != expected_type:
                issues.append(Issue(relative, None, "type", f"type attendu dans docs/{parts[0]}/ : {expected_type}"))
    return documents, issues


def registry(root, documents):
    by_id, by_path, issues = {}, {}, []
    for document in documents:
        if document.kind not in PREFIX or document.path.parent == root / "templates":
            continue
        by_path[document.path.resolve()] = document
        identifier = document.identity
        if not identifier or not IDENTITY.fullmatch(identifier):
            continue
        if identifier in by_id:
            first = by_id[identifier].path.relative_to(root).as_posix()
            second = document.path.relative_to(root).as_posix()
            issues.append(Issue(second, 2, "id", f"identifiant {identifier} dupliqué : {first} et {second}"))
        else:
            by_id[identifier] = document
    return by_id, by_path, issues


def references(root, documents, by_id):
    issues = []
    for document in documents:
        if document.kind not in PREFIX or document.path.parent == root / "templates":
            continue
        path = document.path.relative_to(root).as_posix()
        for field in ("related_docs", "related_adrs", "supersedes"):
            values = document.metadata.get(field, [])
            if not isinstance(values, list):
                continue
            for target_id in values:
                if not isinstance(target_id, str) or not IDENTITY.fullmatch(target_id):
                    continue  # Le schéma donne le diagnostic de format.
                if target_id == document.identity:
                    issues.append(Issue(path, None, "référence", f"auto-référence interdite dans {field} : {target_id}"))
                target = by_id.get(target_id)
                if target is None:
                    issues.append(Issue(path, None, "référence", f"{field} cible inexistante : {target_id}"))
                elif field != "supersedes" and target.metadata.get("status") == OBSOLETE.get(target.kind):
                    issues.append(Issue(path, None, "référence", f"{field} cible un document obsolète : {target_id}", "warning"))
    return issues


def adr_graph(root, by_id):
    adrs = {identifier: doc for identifier, doc in by_id.items() if doc.kind == "adr"}
    issues = []
    replaced = set()
    for identifier, document in adrs.items():
        targets = document.metadata.get("supersedes", [])
        if not isinstance(targets, list):
            continue
        for target_id in targets:
            target = adrs.get(target_id)
            if target is None:
                continue  # Référence manquante déjà diagnostiquée.
            if document.metadata.get("status") == "accepted":
                replaced.add(target_id)
                if target.metadata.get("status") != "superseded":
                    issues.append(Issue(document.path.relative_to(root).as_posix(), None, "adr", f"{identifier} acceptée remplace {target_id}, qui doit être superseded"))
    for identifier, document in adrs.items():
        if document.metadata.get("status") == "superseded" and identifier not in replaced:
            issues.append(Issue(document.path.relative_to(root).as_posix(), None, "adr", f"{identifier} superseded sans ADR accepted qui la remplace"))
    state = {}
    reported = set()

    def visit(identifier, chain):
        state[identifier] = 1
        targets = adrs[identifier].metadata.get("supersedes", [])
        for target in targets if isinstance(targets, list) else []:
            if target not in adrs:
                continue
            if state.get(target) == 1:
                cycle = chain[chain.index(target):] + [target] if target in chain else [identifier, target]
                key = tuple(sorted(set(cycle)))
                if key not in reported:
                    reported.add(key)
                    issues.append(Issue(adrs[identifier].path.relative_to(root).as_posix(), None, "adr", f"cycle de remplacement : {' -> '.join(cycle)}"))
            elif state.get(target) != 2:
                visit(target, chain + [target])
        state[identifier] = 2

    for identifier in adrs:
        if not state.get(identifier):
            visit(identifier, [identifier])
    return issues


def historical(root: Path, base_ref: str, by_id):
    issues = []
    try:
        listing = subprocess.run(["git", "ls-tree", "-rz", "--name-only", base_ref, "--", "docs", "decisions", "knowledge"], cwd=root, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        return [Issue(".", None, "historique", f"base Git inaccessible ({base_ref}) : {exc}")]
    previous = {}
    for raw_path in listing.stdout.split(b"\0"):
        if not raw_path:
            continue
        try:
            path = raw_path.decode("utf-8")
        except UnicodeDecodeError:
            issues.append(Issue(".", None, "historique", "chemin Git non encodé en UTF-8 dans la base"))
            continue
        if not path.endswith(".md") or Path(path).name.lower() == "readme.md":
            continue
        try:
            result = subprocess.run(["git", "show", f"{base_ref}:{path}"], cwd=root, text=True, encoding="utf-8", capture_output=True, check=True)
            data, _, _, parse_issues = parse(result.stdout, path)
            if parse_issues:
                issues.append(Issue(path, None, "historique", "frontmatter de la base invalide"))
                continue
            identifier = data.get("id")
            if not isinstance(identifier, str) or not IDENTITY.fullmatch(identifier):
                issues.append(Issue(path, None, "historique", f"ID de la base invalide : {identifier}"))
            elif identifier in previous:
                issues.append(Issue(path, None, "historique", f"ID {identifier} dupliqué dans la base : {previous[identifier]} et {path}"))
            else:
                previous[identifier] = path
        except (OSError, subprocess.CalledProcessError) as exc:
            issues.append(Issue(path, None, "historique", f"lecture de la base impossible : {exc}"))
    current_paths = {doc.path.relative_to(root).as_posix(): doc.identity for doc in by_id.values()}
    for identifier, old_path in previous.items():
        if identifier not in by_id:
            new_id = current_paths.get(old_path)
            detail = f"ancien {old_path} ({identifier}), nouveau {old_path} ({new_id})" if new_id else f"{old_path} ({identifier}) supprimé"
            issues.append(Issue(old_path, None, "historique", f"identité publiée absente : {detail}"))
    return issues


def validate(root: Path, base_ref: str | None = None):
    root = root.resolve()
    validators, issues = load_schemas(root)
    documents, read_issues = read_documents(root, validators)
    issues.extend(read_issues)
    by_id, by_path, registry_issues = registry(root, documents)
    issues.extend(registry_issues)
    issues.extend(references(root, documents, by_id))
    issues.extend(adr_graph(root, by_id))
    cache = {}
    for document in documents:
        issues.extend(check_links(root, document, by_path, cache))
    if base_ref:
        issues.extend(historical(root, base_ref, by_id))
    return documents, issues
