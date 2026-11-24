"""Accept proposed ADRs from a merged, human-approved pull request."""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from doccheck.frontmatter import parse


PARIS = ZoneInfo("Europe/Paris")
FIELD = re.compile(r"^[A-Za-z_][A-Za-z_0-9-]*:")
ADR_PATH = re.compile(r"^decisions/ADR-[0-9]{4,}-[^/]+\.md$")


class GitHub:
    def __init__(self, repository: str, token: str):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("GITHUB_REPOSITORY invalide")
        self.repository = repository
        self.token = token

    def get(self, endpoint: str):
        request = Request(
            f"https://api.github.com/repos/{self.repository}/{endpoint}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            raise RuntimeError(f"GitHub API {endpoint}: HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"GitHub API {endpoint}: {exc.reason}") from exc

    def pages(self, endpoint: str):
        page = 1
        while True:
            separator = "&" if "?" in endpoint else "?"
            items = self.get(f"{endpoint}{separator}per_page=100&page={page}")
            if not isinstance(items, list):
                raise ValueError(f"Réponse GitHub inattendue pour {endpoint}")
            yield from items
            if len(items) < 100:
                break
            page += 1


def merged_pull_for_commit(github: GitHub, sha: str):
    pulls = [
        pull for pull in github.pages(f"commits/{sha}/pulls")
        if pull.get("merged_at")
        and pull.get("merge_commit_sha") == sha
        and pull.get("base", {}).get("ref") == "main"
    ]
    if len(pulls) > 1:
        raise ValueError(f"Plusieurs PR fusionnées correspondent à {sha}")
    return pulls[0] if pulls else None


def reviewed_adrs(github: GitHub, number: int):
    return [
        file["filename"]
        for file in github.pages(f"pulls/{number}/files")
        if file.get("status") in {"added", "modified"}
        and isinstance(file.get("filename"), str)
        and ADR_PATH.fullmatch(file["filename"])
    ]


def valid_approvals(reviews: list[dict], head_sha: str, author: str):
    """Keep the latest decisive review per human on the final PR head."""
    by_reviewer = {}
    for review in reviews:
        user = review.get("user") or {}
        login = user.get("login")
        if (
            user.get("type") != "User"
            or not isinstance(login, str)
            or login.casefold() == author.casefold()
            or review.get("commit_id") != head_sha
        ):
            continue
        state = review.get("state")
        if state not in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            continue
        submitted = review.get("submitted_at") or ""
        current = by_reviewer.get(login.casefold())
        if current is None or submitted >= (current.get("submitted_at") or ""):
            by_reviewer[login.casefold()] = review
    return sorted(
        (review for review in by_reviewer.values() if review["state"] == "APPROVED"),
        key=lambda review: (review["submitted_at"], review["user"]["login"].casefold()),
    )


def replace_field(lines: list[str], name: str, value: str):
    matches = [i for i, line in enumerate(lines) if line.startswith(f"{name}:")]
    if len(matches) != 1:
        raise ValueError(f"Champ {name} absent ou dupliqué")
    start = matches[0]
    end = start + 1
    while end < len(lines) and not FIELD.match(lines[end]):
        end += 1
    lines[start:end] = [f"{name}: {value}\n"]


def accept_adr(text: str, path: str, approvals: list[dict], pull_url: str):
    metadata, _, _, issues = parse(text, path)
    if issues:
        raise ValueError(f"{path}: frontmatter invalide : {issues[0].message}")
    if metadata.get("status") != "proposed":
        return None
    if metadata.get("approved_by") != [] or metadata.get("decided_at") is not None:
        raise ValueError(f"{path}: une proposition porte déjà des métadonnées d'approbation")
    references = metadata.get("references")
    if not isinstance(references, list) or not all(isinstance(ref, str) for ref in references):
        raise ValueError(f"{path}: références invalides")

    approvers = list(dict.fromkeys(review["user"]["login"] for review in approvals))
    decided_at = max(
        datetime.fromisoformat(review["submitted_at"].replace("Z", "+00:00")).astimezone(PARIS)
        for review in approvals
    ).date().isoformat()
    evidence = [pull_url] + [review["html_url"] for review in approvals]
    references = list(dict.fromkeys(references + evidence))

    lines = text.splitlines(keepends=True)
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        raise ValueError(f"{path}: frontmatter non terminé")
    frontmatter = lines[1:closing]
    replace_field(frontmatter, "status", "accepted")
    replace_field(frontmatter, "approved_by", json.dumps(approvers, ensure_ascii=False))
    replace_field(frontmatter, "decided_at", decided_at)
    replace_field(frontmatter, "references", json.dumps(references, ensure_ascii=False))
    updated = "".join(lines[:1] + frontmatter + lines[closing:])
    parsed, _, _, issues = parse(updated, path)
    if issues or parsed["status"] != "accepted" or parsed["approved_by"] != approvers:
        raise ValueError(f"{path}: mise à jour du frontmatter invalide")
    return updated


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    sha = os.environ.get("ADR_MERGE_SHA") or os.environ["GITHUB_SHA"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("SHA de fusion invalide")
    root = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
    github = GitHub(repository, os.environ["GITHUB_TOKEN"])
    pull = merged_pull_for_commit(github, sha)
    if pull is None:
        print("Aucune PR fusionnée pour ce commit : aucun changement.")
        return
    number = pull["number"]
    paths = reviewed_adrs(github, number)
    if not paths:
        print(f"PR #{number} : aucune ADR à finaliser.")
        return
    pull = github.get(f"pulls/{number}")
    if not pull.get("merged_at") or pull.get("merge_commit_sha") != sha:
        raise ValueError(f"PR #{number} : fusion non vérifiée")
    reviews = list(github.pages(f"pulls/{number}/reviews"))
    approvals = valid_approvals(reviews, pull["head"]["sha"], pull["user"]["login"])
    if not approvals:
        raise ValueError(f"PR #{number} : aucune approbation humaine du dernier commit")

    changed = []
    for name in paths:
        path = root / name
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f"Chemin ADR invalide : {name}")
        original = path.read_text(encoding="utf-8")
        updated = accept_adr(original, name, approvals, pull["html_url"])
        if updated is not None and updated != original:
            path.write_text(updated, encoding="utf-8", newline="")
            changed.append(name)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"changed={'true' if changed else 'false'}\n")
            stream.write(f"pull_number={number}\n")
    print(f"PR #{number} : {len(changed)} ADR finalisée(s) : {', '.join(changed)}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, RuntimeError) as exc:
        print(f"Finalisation ADR impossible : {exc}", file=sys.stderr)
        sys.exit(1)
