"""Valider la documentation RustkinsDocs. Exécutable depuis n'importe quel dossier."""

import argparse
import os
from pathlib import Path

from doccheck.rules import validate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", help="référence Git de base pour vérifier la conservation des IDs")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    documents, issues = validate(args.root, args.base_ref)
    for issue in issues:
        location = f"{issue.path}:{issue.line}" if issue.line else issue.path
        print(f"{location}: {issue.level} [{issue.category}] {issue.message}")
        if os.environ.get("GITHUB_ACTIONS"):
            message = f"[{issue.category}] {issue.message}".replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            annotation = "error" if issue.level == "error" else "warning"
            line = f",line={issue.line}" if issue.line else ""
            print(f"::{annotation} file={issue.path}{line}::{message}")
    errors = sum(issue.level == "error" for issue in issues)
    warnings = sum(issue.level == "warning" for issue in issues)
    print(f"Validation : {len(documents)} fichiers Markdown, {errors} erreurs, {warnings} avertissements")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
