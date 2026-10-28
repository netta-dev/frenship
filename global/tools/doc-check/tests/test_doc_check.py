import shutil
from pathlib import Path

import pytest

from doc_check.checks import check_file


def _check(tmp_path: Path, text: str) -> list[tuple[int, str]]:
    path = tmp_path / "doc.md"
    path.write_text(text)
    return [(f.line, f.problem) for f in check_file(path)]


def test_a_clean_list_passes(tmp_path):
    assert _check(tmp_path, "1. a\n2. b\n3. c\n") == []


def test_a_gap_is_flagged(tmp_path):
    assert _check(tmp_path, "1. a\n2. b\n4. c\n") == [(3, "list item 4 follows 2; expected 3")]


def test_a_repeat_is_flagged(tmp_path):
    assert _check(tmp_path, "7. a\n8. b\n8. c\n9. d\n") == [(3, "list item 8 repeats the previous number")]


def test_a_list_that_a_callout_splits_continues(tmp_path):
    text = "1. a\n2. b\n\n> [!info]- **Rationale** — b\n> why\n\n3. c\n"
    assert _check(tmp_path, text) == []


def test_a_repeat_after_a_callout_is_flagged(tmp_path):
    text = "1. a\n2. b\n\n> [!info]- **Rationale** — b\n> why\n\n2. c\n"
    assert _check(tmp_path, text) == [(7, "list item 2 repeats the previous number")]


def test_a_heading_starts_lists_afresh(tmp_path):
    assert _check(tmp_path, "1. a\n2. b\n\n## Next\n\n5. c\n6. d\n") == []


def test_a_nested_list_numbers_on_its_own(tmp_path):
    assert _check(tmp_path, "1. a\n   1. x\n   2. y\n2. b\n   1. z\n") == []


def test_numbered_lines_in_a_code_fence_are_ignored(tmp_path):
    assert _check(tmp_path, "1. a\n\n```\n1. x\n1. y\n```\n\n2. b\n") == []


def test_a_marker_without_a_body_and_a_body_without_a_marker(tmp_path):
    text = "A claim.[^src] And `[^code]` in code.\n\n[^other]: An orphan body.\n"
    assert _check(tmp_path, text) == [
        (1, "footnote [^src] has no body"),
        (3, "footnote body [^other] has no marker"),
    ]


def test_a_marker_followed_by_a_colon_counts(tmp_path):
    text = "1. **Site** — `f`[^loc]: what it does.\n\n[^loc]: `f.py`.\n"
    assert _check(tmp_path, text) == []


def test_a_missing_file_is_flagged(tmp_path):
    assert _check(tmp_path, "See [the plan](plan.md).\n") == [(1, "link target plan.md doesn't exist")]


def test_a_missing_anchor_is_flagged(tmp_path):
    (tmp_path / "plan.md").write_text("# Plan\n\n## Resolved decisions\n")
    assert _check(tmp_path, "See [it](plan.md#open-questions).\n") == [
        (1, "link anchor #open-questions isn't a heading in plan.md")
    ]


def test_good_anchors_and_urls_pass(tmp_path):
    (tmp_path / "plan.md").write_text("# Plan\n\n## Resolved decisions\n\n```\n## Not a heading\n```\n")
    text = (
        "[a](plan.md#resolved-decisions), [b](plan.md#Resolved%20decisions), [c](#local-heading), "
        "[d](https://example.com/x#y), ![e](plan.md)\n\n## Local heading\n"
    )
    assert _check(tmp_path, text) == []


@pytest.mark.skipif(shutil.which("npx") is None, reason="needs npx")
def test_the_mermaid_traps_are_flagged_and_the_alias_passes(tmp_path):
    text = (
        "```mermaid\nsequenceDiagram\n    A->>B: one; two\n```\n\n"
        "```mermaid\nsequenceDiagram\n    participant Box\n    Box->>A: hi\n```\n\n"
        "```mermaid\nsequenceDiagram\n    participant Bx as Box\n    Bx->>A: hi\n```\n"
    )
    found = _check(tmp_path, text)
    assert [line for line, _ in found] == [1, 6]
    assert all(problem.startswith("mermaid block doesn't parse") for _, problem in found)
