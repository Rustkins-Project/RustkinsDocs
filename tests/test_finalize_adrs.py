"""The post-merge job must only publish evidence-backed ADR approvals."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import finalize_adrs  # noqa: E402
from finalize_adrs import accept_adr, merged_pull_for_commit, valid_approvals  # noqa: E402


PROPOSAL = """---
id: ADR-0099
title: Example
status: proposed
topics: [architecture]
applies_to: [all]
decided_at: null
approved_by: []
supersedes: []
related_work_items: []
references: []
---

# Example
"""


def review(login, state="APPROVED", sha="head", date="2026-11-24T23:30:00Z", kind="User"):
    return {
        "user": {"login": login, "type": kind},
        "state": state,
        "commit_id": sha,
        "submitted_at": date,
        "html_url": f"https://github.com/example/repo/pull/1#review-{login}",
    }


def test_accepts_only_current_human_approvals_and_records_paris_date():
    approvals = valid_approvals(
        [
            review("author"),
            review("bot[bot]", kind="Bot"),
            review("stale", sha="old"),
            review("retracted", date="2026-11-24T20:00:00Z"),
            review("retracted", state="CHANGES_REQUESTED", date="2026-11-24T21:00:00Z"),
            review("Alexis"),
        ],
        "head",
        "author",
    )
    assert [item["user"]["login"] for item in approvals] == ["Alexis"]

    result = accept_adr(PROPOSAL, "decisions/ADR-0099-example.md", approvals, "https://github.com/example/repo/pull/1")
    assert "status: accepted" in result
    assert "approved_by: [\"Alexis\"]" in result
    assert "decided_at: 2026-11-25" in result
    assert "https://github.com/example/repo/pull/1#review-Alexis" in result
    assert result.endswith("# Example\n")
    assert accept_adr(result, "decisions/ADR-0099-example.md", approvals, "https://github.com/example/repo/pull/1") is None


def test_rejects_proposal_with_fake_existing_approval():
    with pytest.raises(ValueError, match="déjà des métadonnées"):
        accept_adr(PROPOSAL.replace("approved_by: []", "approved_by: [someone]"), "adr.md", [review("Alexis")], "https://github.com/example/repo/pull/1")


def test_preserves_multiline_references():
    proposal = PROPOSAL.replace("references: []", "references:\n  - https://example.com/source")
    result = accept_adr(proposal, "adr.md", [review("Alexis")], "https://github.com/example/repo/pull/1")
    assert "https://example.com/source" in result
    assert result.count("https://example.com/source") == 1


def test_only_exact_merge_commit_selects_pr():
    class Github:
        def pages(self, endpoint):
            assert endpoint == "commits/merge/pulls"
            yield {"number": 1, "merged_at": "2026-11-24T12:00:00Z", "merge_commit_sha": "other", "base": {"ref": "main"}}
            yield {"number": 2, "merged_at": "2026-11-24T12:00:00Z", "merge_commit_sha": "merge", "base": {"ref": "main"}}

    assert merged_pull_for_commit(Github(), "merge")["number"] == 2


def test_finalization_changes_only_proposed_adrs_from_merged_pr(tmp_path, monkeypatch):
    merge_sha = "a" * 40
    decisions = tmp_path / "decisions"
    decisions.mkdir()
    proposed = decisions / "ADR-0099-example.md"
    proposed.write_text(PROPOSAL, encoding="utf-8")
    untouched = decisions / "ADR-0098-untouched.md"
    untouched.write_text(PROPOSAL.replace("ADR-0099", "ADR-0098"), encoding="utf-8")

    class Github:
        def __init__(self, repository, token):
            assert repository == "example/repo"
            assert token == "test-token"

        def pages(self, endpoint):
            if endpoint == f"commits/{merge_sha}/pulls":
                return iter([{"number": 1, "merged_at": "2026-11-24T12:00:00Z", "merge_commit_sha": merge_sha, "base": {"ref": "main"}}])
            if endpoint == "pulls/1/files":
                return iter([
                    {"filename": "decisions/ADR-0099-example.md", "status": "added"},
                    {"filename": "decisions/ADR-0098-untouched.md", "status": "removed"},
                    {"filename": "docs/other.md", "status": "modified"},
                ])
            if endpoint == "pulls/1/reviews":
                return iter([review("Alexis")])
            raise AssertionError(endpoint)

        def get(self, endpoint):
            assert endpoint == "pulls/1"
            return {
                "merged_at": "2026-11-24T12:00:00Z",
                "merge_commit_sha": merge_sha,
                "head": {"sha": "head"},
                "user": {"login": "author"},
                "html_url": "https://github.com/example/repo/pull/1",
            }

    monkeypatch.setattr(finalize_adrs, "GitHub", Github)
    monkeypatch.setenv("GITHUB_REPOSITORY", "example/repo")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_SHA", merge_sha)
    monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
    output = tmp_path / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    finalize_adrs.main()
    assert "status: accepted" in proposed.read_text(encoding="utf-8")
    assert untouched.read_text(encoding="utf-8").splitlines()[3] == "status: proposed"
    assert output.read_text(encoding="utf-8") == "changed=true\npull_number=1\n"
