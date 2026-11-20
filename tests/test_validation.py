"""Tests fonctionnels sur de petits dépôts documentaires autonomes."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from doccheck.frontmatter import parse  # noqa: E402
from doccheck.links import PARSER, headings, slug  # noqa: E402
from doccheck.rules import validate  # noqa: E402


BODIES = {
    "document": "# Document\n\nTexte.\n",
    "runbook": "# Procédure\n\n## Objectif\n\nTexte.\n\n## Préparation\n\nTexte.\n\n## Étapes\n\n1. Commande.\n\n## Vérifications\n\nTexte.\n",
    "adr": "# Décision\n\n## Contexte\n\nTexte.\n\n## Décision\n\nTexte.\n\n## Alternatives\n\nTexte.\n\n## Conséquences\n\nTexte.\n",
    "knowledge": "# Connaissance\n\nTexte.\n",
}
META = {
    "document": {"id": "DOC-0001", "title": "Document", "type": "architecture", "status": "draft", "summary": "Résumé", "topics": ["test"], "applies_to": ["V0"]},
    "runbook": {"id": "RUN-0001", "title": "Procédure", "type": "operation", "status": "draft", "summary": "Résumé", "topics": ["test"], "applies_to": ["V0"]},
    "adr": {"id": "ADR-0001", "title": "Décision", "status": "proposed", "topics": ["test"], "applies_to": ["V0"], "decided_at": None, "approved_by": [], "supersedes": [], "related_work_items": [], "references": []},
    "knowledge": {"id": "KNOW-0001", "title": "Note", "type": "technical-note", "status": "candidate", "topics": ["test"], "applies_to": ["V0"], "verified_at": None, "references": []},
}
PATHS = {"document": "docs/architecture/a.md", "runbook": "docs/operations/a.md", "adr": "decisions/a.md", "knowledge": "knowledge/a.md"}


@pytest.fixture
def repo(tmp_path):
    shutil.copytree(REPO / "schemas", tmp_path / "schemas")
    shutil.copytree(REPO / "templates", tmp_path / "templates")
    return tmp_path


def write(repo, kind="document", *, path=None, metadata=None, body=None, raw=None):
    target = repo / (path or PATHS[kind])
    target.parent.mkdir(parents=True, exist_ok=True)
    data = META[kind] | (metadata or {})
    if raw is None:
        import yaml
        raw = "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n\n" + (BODIES[kind] if body is None else body)
    target.write_text(raw, encoding="utf-8")
    return target


def messages(repo, base_ref=None):
    return validate(repo, base_ref)[1]


def has(issues, part, level="error"):
    return any(part in issue.message and issue.level == level for issue in issues)


def test_four_schemas_and_frontmatters(repo):
    for kind in META:
        schema = json.loads((repo / "schemas" / f"{kind}.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        write(repo, kind)
    assert not [issue for issue in messages(repo) if issue.level == "error"]


@pytest.mark.parametrize("kind,change,fragment", [
    ("document", {"title": ""}, "title"),
    ("runbook", {"type": "architecture"}, "operation"),
    ("adr", {"status": "accepted"}, "approved_by"),
    ("knowledge", {"verified_at": "2026-99-99", "status": "verified"}, "verified_at"),
    ("document", {"extra": 1}, "Additional properties"),
    ("document", {"related_work_items": [0]}, "related_work_items"),
    ("document", {"references": ["not-a-uri"]}, "references"),
])
def test_schema_rejects_invalid_values(repo, kind, change, fragment):
    write(repo, kind, metadata=change)
    assert has(messages(repo), fragment)


def test_missing_malformed_duplicate_yaml_and_dates(repo):
    path = write(repo, raw="# Sans frontmatter\n")
    assert has(messages(repo), "frontmatter YAML manquant")
    path.write_text("---\nid: DOC-0001\nid: DOC-0002\n---\n# Titre\n", encoding="utf-8")
    assert has(messages(repo), "clé YAML dupliquée")
    path.write_text("---\nid: [\n---\n# Titre\n", encoding="utf-8")
    assert has(messages(repo), "expected") or has(messages(repo), "parsing")
    data, _, _, errors = parse("---\ndecided_at: 2026-11-20\n---\r\n# Éléphant\r\n", "test.md")
    assert not errors and data["decided_at"] == "2026-11-20"


@pytest.mark.parametrize("versions,valid", [
    (["V0"], True), (["V0", "V1", "V2"], True), (["all"], True),
    (["V4"], False), (["V1", "all"], False), (["V0", "V0"], False),
])
def test_product_versions_in_all_categories(repo, versions, valid):
    for kind in META:
        write(repo, kind, metadata={"applies_to": versions})
    assert (not any(issue.level == "error" for issue in messages(repo))) == valid


def test_ids_and_templates(repo):
    write(repo, metadata={"id": "DOC-0000"})
    assert has(messages(repo), "réservé aux templates")
    write(repo, metadata={"id": "RUN-0001"})
    assert has(messages(repo), "incompatible")
    write(repo, metadata={"id": "DOC-0001"})
    write(repo, path="docs/architecture/b.md")
    assert has(messages(repo), "dupliqué : docs/architecture/a.md et docs/architecture/b.md")
    assert not any("0000" in issue.message for issue in messages(repo))


def test_type_follows_location(repo):
    write(repo, path="docs/specifications/a.md")
    assert has(messages(repo), "type attendu")


def test_related_docs_and_adrs(repo):
    write(repo)
    write(repo, "runbook")
    write(repo, "adr")
    write(repo, metadata={"related_docs": ["RUN-0001"], "related_adrs": ["ADR-0001"]})
    assert not [issue for issue in messages(repo) if issue.level == "error"]
    write(repo, metadata={"related_docs": ["../a.md"]})
    assert has(messages(repo), "related_docs")
    write(repo, metadata={"related_docs": ["DOC-9999"], "related_adrs": ["ADR-9999"]})
    assert has(messages(repo), "cible inexistante : DOC-9999")
    assert has(messages(repo), "cible inexistante : ADR-9999")
    write(repo, metadata={"related_docs": ["DOC-0001", "DOC-0001"]})
    assert has(messages(repo), "auto-référence") and has(messages(repo), "non-unique")


def test_obsolete_reference_warns_but_missing_errors(repo):
    write(repo, metadata={"related_docs": ["RUN-0001"]})
    write(repo, "runbook", metadata={"status": "deprecated"})
    assert has(messages(repo), "document obsolète", "warning")
    assert not [issue for issue in messages(repo) if issue.level == "error"]


def test_obsolete_markdown_link_warns(repo):
    write(repo, body="# Document\n\n[runbook](../operations/a.md)\n")
    write(repo, "runbook", metadata={"status": "deprecated"})
    assert has(messages(repo), "lien vers document obsolète", "warning")


def test_sections_ignore_code_and_comments(repo):
    body = "# ADR\n\n```md\n## Contexte\n```\n\n## Décision\n<!-- vide -->\n\n## Alternatives\nTexte.\n\n## Conséquences\nTexte.\n"
    write(repo, "adr", body=body)
    assert has(messages(repo), "section H2 manquante : Contexte")
    assert has(messages(repo), "section vide : Décision")
    write(repo, "runbook", body=BODIES["runbook"] + "\n## Retour arrière\n<!-- vide -->\n")
    assert has(messages(repo), "section vide : Retour arrière")
    write(repo, "runbook", body=BODIES["runbook"].replace("## Objectif\n\nTexte.", "## Objectif\n\n### Sous-titre"))
    assert has(messages(repo), "section vide : Objectif")


def test_links_references_images_anchors_unicode_and_code(repo):
    write(repo, body="# Document\n\n## Installation\n\n## Installation\n\n## Éléphant !\n\n[local](#installation-1) [accent](#%C3%A9l%C3%A9phant-)\n\n[référence][cible] ![image](image%20test.png) [mmd](modele.mmd)\n\n`[faux](absent.md)`\n\n```md\n[faux](absent.md)\n```\n\n[cible]: ../architecture/b.md#titre\n")
    write(repo, path="docs/architecture/b.md", metadata={"id": "DOC-0002"}, body="# Titre\n")
    (repo / "docs/architecture/image test.png").write_bytes(b"PNG")
    (repo / "docs/architecture/modele.mmd").write_text("graph TD", encoding="utf-8")
    assert not [issue for issue in messages(repo) if issue.level == "error"]
    assert slug("Éléphant !") == "éléphant-"
    (repo / "docs/architecture/modele.mmd").unlink()
    assert has(messages(repo), "cible locale introuvable")


def test_heading_collisions_reserve_generated_anchors(repo):
    body = "# Document\n\n## Installation\n\n## Installation\n\n## Installation-1\n\n[third](#installation-1-1)\n"
    write(repo, body=body)
    anchors = [item[3] for item in headings(PARSER.parse(body))]
    assert anchors == ["document", "installation", "installation-1", "installation-1-1"]
    assert not [issue for issue in messages(repo) if issue.level == "error"]


def test_navigation_research_and_bad_links(repo):
    write(repo)
    (repo / "README.md").write_text("# Accueil\n\n[doc](docs/architecture/a.md)\n", encoding="utf-8")
    (repo / "INDEX.md").write_text("# Index\n\n[local](#index)\n", encoding="utf-8")
    (repo / "research").mkdir()
    (repo / "research" / "bad.md").write_text("[broken](missing.md)", encoding="utf-8")
    assert not [issue for issue in messages(repo) if issue.level == "error"]
    (repo / "README.md").write_text("# Accueil\n\n[bad](missing.md) [escape](../outside.md)\n", encoding="utf-8")
    assert has(messages(repo), "cible locale introuvable") and has(messages(repo), "chemin sortant")


def test_external_url_syntax_without_network(repo, monkeypatch):
    import socket
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("network used"))
    write(repo, body="# Document\n\n[ok](https://example.org/a#b) [bad](https://)\n")
    assert has(messages(repo), "URL externe invalide")


def test_mailto_and_ftp_links_without_network(repo, monkeypatch):
    import socket
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("network used"))
    write(repo, body="# Document\n\n[mail](mailto:team@example.org) [ftp](ftp://example.org/file.txt)\n")
    assert not [issue for issue in messages(repo) if issue.level == "error"]
    write(repo, body="# Document\n\n[bad mail](mailto:) [bad ftp](ftp://)\n")
    assert sum(issue.category == "lien" for issue in messages(repo)) == 2


@pytest.mark.parametrize("url,valid", [
    ("https://example.org:443/test", True),
    ("https://example.org:65535/test", True),
    ("https://example.org:abc/test", False),
    ("https://example.org:65536/test", False),
    ("https://example.org:0/test", False),
    ("https://example.org:/test", False),
])
def test_ports_in_markdown_and_frontmatter(repo, url, valid):
    write(repo, metadata={"references": [url]}, body=f"# Document\n\n[lien]({url})\n")
    errors = [issue for issue in messages(repo) if issue.level == "error"]
    if valid:
        assert not errors
    else:
        assert any(issue.category == "lien" for issue in errors)
        assert any(issue.category == "schema" for issue in errors)


def test_adr_graph(repo):
    write(repo, "adr", metadata={"id": "ADR-0001", "status": "superseded"})
    write(repo, "adr", path="decisions/b.md", metadata={"id": "ADR-0002", "status": "accepted", "approved_by": ["Alexis"], "decided_at": "2026-11-20", "supersedes": ["ADR-0001"]})
    assert not [issue for issue in messages(repo) if issue.level == "error"]
    write(repo, "adr", path="decisions/c.md", metadata={"id": "ADR-0003", "status": "accepted", "approved_by": ["Timothy"], "decided_at": "2026-11-20", "supersedes": ["ADR-0001"]})
    assert not [issue for issue in messages(repo) if issue.level == "error"]
    write(repo, "adr", path="decisions/b.md", metadata={"id": "ADR-0002", "status": "accepted", "approved_by": ["Alexis"], "decided_at": "2026-11-20", "supersedes": ["ADR-0002"]})
    assert has(messages(repo), "auto-référence") and has(messages(repo), "cycle de remplacement")
    write(repo, "adr", path="decisions/b.md", metadata={"id": "ADR-0002", "supersedes": ["ADR-0001"]})
    write(repo, "adr", path="decisions/c.md", metadata={"id": "ADR-0003"})
    assert has(messages(repo), "superseded sans ADR accepted")


def test_adr_cycle_and_wrong_status(repo):
    write(repo, "adr", metadata={"id": "ADR-0001", "status": "accepted", "approved_by": ["A"], "decided_at": "2026-11-20", "supersedes": ["ADR-0002"]})
    write(repo, "adr", path="decisions/b.md", metadata={"id": "ADR-0002", "status": "proposed", "supersedes": ["ADR-0001"]})
    assert has(messages(repo), "qui doit être superseded") and has(messages(repo), "cycle de remplacement")


def git(repo, *args):
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return result


def test_workflow_checks_merge_result(repo, monkeypatch):
    workflow = yaml.safe_load((REPO / ".github/workflows/docs-validation.yml").read_text(encoding="utf-8"))
    steps = workflow["jobs"]["docs-validation"]["steps"]
    checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
    assert "ref" not in checkout.get("with", {})

    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(repo))
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-m", "base")
    git(repo, "switch", "-c", "feature")
    write(repo, path="docs/architecture/feature.md", metadata={"id": "DOC-0050"})
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-m", "feature doc")
    assert not [issue for issue in messages(repo) if issue.level == "error"]
    git(repo, "switch", "main")
    write(repo, path="docs/architecture/main.md", metadata={"id": "DOC-0050"})
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-m", "main doc")
    git(repo, "switch", "feature")
    assert not [issue for issue in messages(repo, "main") if issue.level == "error"]
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.org", "merge", "--no-ff", "main", "-m", "merge result")
    assert has(messages(repo, "main"), "identifiant DOC-0050 dupliqué")


def test_history_move_new_change_and_delete(repo, monkeypatch):
    write(repo)
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(repo))
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-m", "base")
    original = repo / PATHS["document"]
    moved = repo / "docs/architecture/moved.md"
    original.rename(moved)
    write(repo, path="docs/architecture/new.md", metadata={"id": "DOC-0002"})
    assert not [issue for issue in messages(repo, "HEAD") if issue.level == "error"]
    write(repo, path="docs/architecture/moved.md", metadata={"id": "DOC-0003"})
    assert has(messages(repo, "HEAD"), "identité publiée absente")
    moved.unlink()
    assert has(messages(repo, "HEAD"), "supprimé")


def test_history_same_path_id_change(repo, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(repo))
    write(repo)
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-m", "base")
    write(repo, metadata={"id": "DOC-0002"})
    assert has(messages(repo, "HEAD"), "nouveau docs/architecture/a.md (DOC-0002)")


def test_history_unicode_filename(repo, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(repo))
    name = "docs/architecture/guide-équipe.md"
    write(repo, path=name)
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-m", "base")
    assert not [issue for issue in messages(repo, "HEAD") if issue.level == "error"]
    write(repo, path=name, metadata={"id": "DOC-0002"})
    assert has(messages(repo, "HEAD"), f"nouveau {name} (DOC-0002)")


def test_cli_exit_codes(repo):
    write(repo)
    command = [sys.executable, str(REPO / "scripts/validate_docs.py"), "--root", str(repo)]
    good = subprocess.run(command, text=True, capture_output=True)
    assert good.returncode == 0 and "0 erreurs" in good.stdout
    write(repo, body="# Document\n\n[lien](missing.md)\n")
    bad = subprocess.run(command, text=True, capture_output=True)
    assert bad.returncode != 0 and "cible locale introuvable" in bad.stdout


def test_pre_commit_runs_only_document_validation():
    """Le commit local vérifie les documents ; la CI garde pytest et l'historique."""
    configuration = yaml.safe_load((REPO / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    assert len(configuration["repos"]) == 1
    assert configuration["repos"][0]["repo"] == "local"
    hooks = configuration["repos"][0]["hooks"]
    assert len(hooks) == 1
    hook = hooks[0]
    assert hook["entry"] == "python scripts/validate_docs.py"
    assert hook["language"] == "python"
    assert hook["always_run"] is True
    assert hook["pass_filenames"] is False
    assert hook["stages"] == ["pre-commit"]

    dependencies = [
        line.strip()
        for line in (REPO / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
        and not line.strip().lower().startswith("pytest")
    ]
    assert hook["additional_dependencies"] == dependencies

    workflow = yaml.safe_load((REPO / ".github/workflows/docs-validation.yml").read_text(encoding="utf-8"))
    runs = [str(step.get("run", "")) for step in workflow["jobs"]["docs-validation"]["steps"]]
    assert any("python -m pytest -q" in run for run in runs)
    assert any("python scripts/validate_docs.py --base-ref" in run for run in runs)
    assert any("python scripts/validate_docs.py" in run for run in runs)
