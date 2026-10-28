"""Check markdown docs' mechanics before a hand-off.

    doc-check <doc>...    one `<file>:<line>: <problem>` line per finding; exit 1 on any

Checks and their rules: `doc_check.checks`.
"""

import argparse
import sys
from pathlib import Path

from doc_check.checks import check_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="doc-check", description="Check markdown docs' mechanics.")
    parser.add_argument("docs", nargs="+", type=Path)
    args = parser.parse_args(argv)
    failed = False
    for doc in args.docs:
        for f in check_file(doc):
            print(f"{doc}:{f.line}: {f.problem}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
