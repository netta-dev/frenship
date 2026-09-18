"""`comment-lint`: judge each comment against the comment and prose rules; print the ones that break one.

    comment-lint FILE...                 whole files
    comment-lint --diff HEAD [--repo .]  comments the diff added
    comment-lint --dry-run FILE...       list extracted comments, no API call
    comment-lint --text 'comment' --context 'code'   judge one comment (re-judging a rewrite)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from comment_lint.extract import SUPPORTED, Comment, extract, extract_diff, supported
from comment_lint.rules import questions

MODEL = "jev-latest"
DEFAULT_EXCLUDE = ["docs/designs/**", "docs/designs/*"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="comment-lint")
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--diff", metavar="RANGE", help="git range; review only comments the diff added")
    ap.add_argument("--repo", type=Path, default=Path("."), help="repo root for --diff")
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="repo-relative glob to skip in --diff mode; docs/designs is always skipped")
    ap.add_argument("--text", help="judge this one comment instead of extracting")
    ap.add_argument("--context", default="", help="code around --text")
    ap.add_argument("--dry-run", action="store_true", help="extract only, no API call")
    ap.add_argument("--threshold", type=float, default=0.45, help="min 'breaks a rule' probability to flag")
    ap.add_argument("--rule-floor", type=float, default=0.15,
                    help="on a flagged axis, list every rule at or above this probability")
    ap.add_argument("--limit", type=int, help="judge at most N comments")
    ap.add_argument("--json", action="store_true", help="emit one JSON object per comment")
    ap.add_argument("--all", action="store_true", help="print clean comments too")
    args = ap.parse_args(argv)

    skipped: list[Path] = []
    if args.text is not None:
        comments = [Comment(Path("-"), 1, 1, "comment", args.text, args.context)]
    elif args.diff:
        comments, skipped = extract_diff(args.repo.resolve(), args.diff, DEFAULT_EXCLUDE + args.exclude)
    elif args.files:
        skipped = [f for f in args.files if not supported(f)]
        comments = [c for f in args.files if supported(f) for c in extract(f)]
    else:
        ap.error("give FILE..., --diff RANGE, or --text")
    if args.limit:
        comments = comments[: args.limit]

    if skipped:
        print(
            f"not reviewed (no extractor): {', '.join(str(p) for p in skipped)}; "
            f"supported: {', '.join(sorted(s.lstrip('.') for s in SUPPORTED))}",
            file=sys.stderr,
        )

    if args.dry_run:
        for c in comments:
            tag = " label" if c.label else ""
            print(f"{c.ref}-{c.end} [{c.kind}{tag}]\n{c.text}\n")
        print(f"{len(comments)} comments", file=sys.stderr)
        return 0

    _load_key()
    from typesafe_sdk import TypeSafeClient

    qs = questions()
    usage_in = usage_out = 0
    flagged = 0
    with TypeSafeClient() as client:
        for c in comments:
            r = client.system_one(state=_state(c), questions=qs, model=MODEL)
            usage_in += r.usage.input_tokens
            usage_out += r.usage.output_tokens
            cr, pr = r.choices["comment_rule"], r.choices["prose_rule"]
            nc, np_ = r.nouls["breaks_comment_rule"].noul, r.nouls["breaks_prose_rule"].noul
            # The noul gates; the choice's distribution names every rule to fix.
            hits = {
                k: _rules(v, args.rule_floor) for k, v, gate in (("comment", cr, nc), ("prose", pr, np_))
                if gate >= args.threshold
            }
            if c.label and "prose" in hits:
                hits["prose"] = [(r, p) for r, p in hits["prose"] if r != "P2_telegraphese"]
                if not hits["prose"]:
                    del hits["prose"]
            if hits:
                flagged += 1
            if not hits and not args.all:
                continue
            if args.json:
                print(json.dumps({
                    "ref": c.ref, "end": c.end, "kind": c.kind, "label": c.label, "text": c.text,
                    "breaks_comment_rule": round(nc, 2), "breaks_prose_rule": round(np_, 2),
                    "comment_dist": _top(cr.probabilities),
                    "prose_dist": _top(pr.probabilities),
                    "flags": {k: [f"{rule} {p}" for rule, p in rules] for k, rules in hits.items()},
                }))
            else:
                _print(c, cr, pr, nc, np_, args.rule_floor)
    print(
        f"\n{len(comments)} comments, {flagged} flagged; "
        f"tokens in={usage_in} out={usage_out}",
        file=sys.stderr,
    )
    return 0


def _load_key() -> None:
    """Read TYPESAFE_API_KEY from ~/.env.d/typesafe when the shell didn't export it."""
    if os.environ.get("TYPESAFE_API_KEY"):
        return
    path = Path.home() / ".env.d" / "typesafe"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip().removeprefix("export ")
        if line.startswith("TYPESAFE_API_KEY="):
            os.environ["TYPESAFE_API_KEY"] = line.split("=", 1)[1].strip().strip("'\"")
            return


def _state(c: Comment) -> dict:
    return {
        "kind": c.kind,
        "comment": c.text,
        "code_around_it": c.context,
    }


def _rules(answer, floor: float) -> list[tuple[str, float]]:
    """Every non-none rule at or above `floor`, best first; the best one alone if none reach it."""
    ranked = sorted(((k, round(v, 2)) for k, v in answer.probabilities.items() if k != "none"), key=lambda kv: -kv[1])
    above = [kv for kv in ranked if kv[1] >= floor]
    return above or ranked[:1]


def _top(probs: dict, n: int = 3) -> dict:
    return {k: round(v, 2) for k, v in sorted(probs.items(), key=lambda kv: -kv[1])[:n]}


def _fmt(rules: list[tuple[str, float]]) -> str:
    return " · ".join(f"{r} {p}" for r, p in rules)


def _print(c: Comment, cr, pr, nc: float, np_: float, floor: float) -> None:
    print(f"## {c.ref} [{c.kind}{' label' if c.label else ''}]")
    print(f"comment: breaks a rule {nc:.2f}; {_fmt(_rules(cr, floor))}")
    print(f"prose:   breaks a rule {np_:.2f}; {_fmt(_rules(pr, floor))}")
    for line in c.text.splitlines():
        print(f"    {line}")
    print()


if __name__ == "__main__":
    sys.exit(main())
