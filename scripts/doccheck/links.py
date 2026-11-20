"""Sections et liens Markdown, analysés avec markdown-it-py."""

import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

from .model import Issue


PARSER = MarkdownIt("commonmark").enable("table")
REQUIRED = {
    "adr": ("Contexte", "Décision", "Alternatives", "Conséquences"),
    "runbook": ("Objectif", "Préparation", "Étapes", "Vérifications"),
}
OPTIONAL_NONEMPTY = {"runbook": ("Retour arrière", "Références")}
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def slug(title: str) -> str:
    """Slug GitHub : Unicode conservé, ponctuation retirée, espaces en tirets."""
    value = title.strip().lower()
    value = "".join(char for char in value if char in "-_ " or not unicodedata.category(char).startswith(("P", "S")))
    return re.sub(r"\s", "-", value)


def heading_text(inline) -> str:
    return "".join(child.content for child in (inline.children or []) if child.type in ("text", "code_inline", "image"))


def headings(tokens):
    found = []
    counts = {}
    for index, token in enumerate(tokens[:-1]):
        if token.type != "heading_open":
            continue
        title = heading_text(tokens[index + 1])
        base = slug(title)
        count = counts.get(base, 0)
        counts[base] = count + 1
        found.append((index, int(token.tag[1:]), title, base if count == 0 else f"{base}-{count}", token.map[0] + 1))
    return found


def useful(tokens):
    for index, token in enumerate(tokens):
        if token.type in ("fence", "code_block") and token.content.strip():
            return True
        if token.type == "inline":
            if index and tokens[index - 1].type == "heading_open":
                continue
            content = COMMENT.sub("", token.content).strip()
            if content and any(child.type not in ("html_inline", "softbreak", "hardbreak") and child.content.strip() for child in (token.children or [])):
                return True
        if token.type == "html_block" and COMMENT.sub("", token.content).strip():
            return True
    return False


def check_sections(tokens, kind, path, body_line):
    if kind not in REQUIRED:
        return []
    sections = {}
    hs = headings(tokens)
    h2 = [(index, title, line) for index, level, title, _, line in hs if level == 2]
    for number, (index, title, line) in enumerate(h2):
        end = h2[number + 1][0] if number + 1 < len(h2) else len(tokens)
        sections.setdefault(title, []).append((line, useful(tokens[index + 3:end])))
    issues = []
    for title in REQUIRED[kind]:
        if title not in sections:
            issues.append(Issue(path, body_line, "section", f"section H2 manquante : {title}"))
        elif not any(nonempty for _, nonempty in sections[title]):
            issues.append(Issue(path, body_line + sections[title][0][0] - 1, "section", f"section vide : {title}"))
    for title in OPTIONAL_NONEMPTY.get(kind, ()):
        if title in sections and not any(nonempty for _, nonempty in sections[title]):
            issues.append(Issue(path, body_line + sections[title][0][0] - 1, "section", f"section vide : {title}"))
    return issues


def local_target(root: Path, source: Path, href: str):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        return None, parsed.fragment, None
    raw = unquote(parsed.path)
    if raw.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", raw):
        return None, parsed.fragment, "chemin absolu interdit"
    target = (source.parent / raw).resolve() if raw else source.resolve()
    if not target.is_relative_to(root.resolve()):
        return None, parsed.fragment, "chemin sortant du dépôt"
    return target, unquote(parsed.fragment), None


def external_error(href: str):
    try:
        parsed = urlsplit(href)
        if parsed.scheme in ("http", "https") and parsed.hostname and not re.search(r"\s", href):
            return None
        return "URL externe invalide"
    except ValueError:
        return "URL externe invalide"


def check_links(root: Path, document, published_by_path, cache):
    path = document.path.relative_to(root).as_posix()
    tokens = PARSER.parse(document.body)
    issues = check_sections(tokens, document.kind, path, document.body_line)
    for token in tokens:
        if token.type != "inline":
            continue
        line = document.body_line + token.map[0] if token.map else document.body_line
        for child in token.children or []:
            if child.type == "link_open":
                href = child.attrGet("href")
            elif child.type == "image":
                href = child.attrGet("src")
            else:
                continue
            if not href:
                continue
            try:
                parsed = urlsplit(href)
            except ValueError:
                issues.append(Issue(path, line, "lien", f"URL invalide : {href}"))
                continue
            if parsed.scheme or parsed.netloc:
                error = external_error(href)
                if error:
                    issues.append(Issue(path, line, "lien", f"{error} : {href}"))
                continue
            target, fragment, error = local_target(root, document.path, href)
            if error:
                issues.append(Issue(path, line, "lien", f"{error} : {href}"))
                continue
            if not target.is_file():
                issues.append(Issue(path, line, "lien", f"cible locale introuvable : {href}"))
                continue
            if target.suffix.lower() != ".md" or "research" in target.relative_to(root).parts:
                continue
            if fragment:
                if target not in cache:
                    try:
                        content = target.read_text(encoding="utf-8")
                        if content.startswith("---"):
                            from .frontmatter import parse
                            _, content, _, _ = parse(content, target.relative_to(root).as_posix(), required=False)
                        cache[target] = {entry[3] for entry in headings(PARSER.parse(content))}
                    except (OSError, UnicodeError) as exc:
                        issues.append(Issue(path, line, "lien", f"cible Markdown illisible : {exc}"))
                        continue
                if fragment not in cache[target]:
                    issues.append(Issue(path, line, "ancre", f"ancre introuvable : {href}"))
            destination = published_by_path.get(target)
            if destination and destination.metadata.get("status") in {"deprecated", "superseded", "outdated"}:
                issues.append(Issue(path, line, "référence", f"lien vers document obsolète : {destination.identity}", "warning"))
    return issues
