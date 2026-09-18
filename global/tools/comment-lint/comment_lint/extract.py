"""Pull comments and docstrings out of source files, each with the code around it.

Python: `#` blocks via `tokenize`, docstrings via `ast`. Dart and proto: `//` blocks,
`///` doc blocks, and `/* */` blocks via a small scanner that skips string literals.
Consecutive lines of one kind merge into a block. In diff mode only blocks that overlap
an added line survive, so the review sees what the change wrote.
"""

from __future__ import annotations

import ast
import fnmatch
import io
import re
import subprocess
import tokenize
from dataclasses import dataclass
from pathlib import Path

BEFORE = 6
AFTER = 12

SUPPORTED = {
    ".py": "python",
    ".dart": "c-style", ".proto": "c-style",
    ".toml": "hash", ".yaml": "hash", ".yml": "hash", ".ini": "hash", ".cfg": "hash",
    ".conf": "hash", ".sh": "hash", ".bash": "hash", ".zsh": "hash",
}

# Changed files that carry no code comments, skipped without a word. Any other unsupported
# file is reported, so a language nobody thought of shows up instead of vanishing.
SILENT = {
    ".md", ".txt", ".rst", ".json", ".lock", ".csv", ".tsv", ".svg", ".png", ".jpg", ".jpeg",
    ".gif", ".ico", ".webp", ".pdf", ".woff", ".woff2", ".ttf", ".env", ".gitignore",
}

_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
_PY_FIELD = re.compile(r"^\s*[A-Za-z_]\w*\s*[:=]")
_C_FIELD = re.compile(r"^\s*(@\w+\s+)?[\w<>?,\[\] .]+\s+\w+\s*(=[^;]*)?[;,]\s*$")
_HASH_FIELD = re.compile(r"""^\s*["']?[\w.\-]+["']?\s*[:=]""")

Block = tuple[int, int, str, str]  # start, end, kind, text


@dataclass
class Comment:
    path: Path
    line: int  # 1-based, first line of the block
    end: int  # inclusive
    kind: str  # "comment" | "docstring"
    text: str
    context: str  # source lines around the block, the block included
    label: bool = False  # one-line comment directly above a field or constant

    @property
    def ref(self) -> str:
        return f"{self.path}:{self.line}"


def supported(path: Path) -> bool:
    return path.suffix in SUPPORTED


def extract(path: Path) -> list[Comment]:
    source = path.read_text()
    lines = source.splitlines()
    style = SUPPORTED.get(path.suffix)
    if style == "python":
        blocks = _hash_blocks(source) + _docstrings(source)
        field = _PY_FIELD
    elif style == "hash":
        blocks = _line_blocks(lines, ("#",), doc_prefix=None)
        field = _HASH_FIELD
    else:
        blocks = _c_style_blocks(lines)
        field = _C_FIELD
    blocks.sort(key=lambda b: b[0])
    out = []
    for start, end, kind, text in blocks:
        lo = max(0, start - 1 - BEFORE)
        hi = min(len(lines), end + AFTER)
        context = "\n".join(lines[lo:hi])
        nxt = lines[end] if end < len(lines) else ""
        label = kind == "comment" and start == end and field.match(nxt) is not None
        out.append(Comment(path, start, end, kind, text, context, label))
    return out


def _hash_blocks(source: str) -> list[Block]:
    blocks: list[Block] = []
    cur: list[tuple[int, str]] = []

    def flush() -> None:
        if cur:
            blocks.append((cur[0][0], cur[-1][0], "comment", "\n".join(t for _, t in cur)))
            cur.clear()

    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT:
            row = tok.start[0]
            if cur and row != cur[-1][0] + 1:
                flush()
            cur.append((row, tok.string))
        elif tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            flush()
    flush()
    return blocks


def _docstrings(source: str) -> list[Block]:
    tree = ast.parse(source)
    out = []
    nodes = [tree, *[n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]]
    for node in nodes:
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            out.append((first.lineno, first.end_lineno or first.lineno, "docstring", first.value.value))
    return out


def _line_blocks(lines: list[str], markers: tuple[str, ...], doc_prefix: str | None) -> list[Block]:
    """Line comments starting with one of `markers`, outside string literals, merged into blocks."""
    blocks: list[Block] = []
    cur: list[tuple[int, str]] = []

    def flush() -> None:
        if cur:
            blocks.append((cur[0][0], cur[-1][0], "comment", "\n".join(t for _, t in cur)))
            cur.clear()

    for row, line in enumerate(lines, 1):
        found = _line_comment(line, markers)
        if found is None:
            flush()
            continue
        col, text = found
        trailing = line[:col].strip() != ""
        if trailing or (cur and row != cur[-1][0] + 1):
            flush()
        cur.append((row, text))
        if trailing:
            flush()
    flush()
    return blocks


def _c_style_blocks(lines: list[str]) -> list[Block]:
    """`//` and `///` line comments and `/* */` blocks, ignoring `//` inside strings."""
    blocks: list[Block] = []
    cur: list[tuple[int, str]] = []
    cur_kind = ""
    in_block = False
    block_start = 0
    block_lines: list[str] = []

    def flush() -> None:
        nonlocal cur_kind
        if cur:
            blocks.append((cur[0][0], cur[-1][0], cur_kind, "\n".join(t for _, t in cur)))
            cur.clear()
        cur_kind = ""

    for row, line in enumerate(lines, 1):
        if in_block:
            block_lines.append(line)
            if "*/" in line:
                in_block = False
                text = "\n".join(block_lines)
                kind = "docstring" if text.lstrip().startswith("/**") else "comment"
                blocks.append((block_start, row, kind, text))
            continue
        found = _line_comment(line, ("//", "/*"))
        if found is None:
            flush()
            continue
        col, text = found
        if text.startswith("/*"):
            flush()
            if "*/" in text:
                kind = "docstring" if text.startswith("/**") else "comment"
                blocks.append((row, row, kind, text))
            else:
                in_block, block_start, block_lines = True, row, [text]
            continue
        kind = "docstring" if text.startswith("///") else "comment"
        trailing = line[:col].strip() != ""
        if trailing or kind != cur_kind or (cur and row != cur[-1][0] + 1):
            flush()
        cur_kind = kind
        cur.append((row, text))
        if trailing:
            flush()
    flush()
    return blocks


def _line_comment(line: str, markers: tuple[str, ...]) -> tuple[int, str] | None:
    """Column and text of the first comment marker outside a string literal, if any."""
    quote: str | None = None
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if line.startswith(quote, i):
                i += len(quote)
                quote = None
                continue
            i += 1
            continue
        if ch in "'\"":
            quote = line[i : i + 3] if line.startswith(ch * 3, i) else ch
            i += len(quote)
            continue
        if any(line.startswith(m, i) for m in markers):
            return i, line[i:].rstrip()
        i += 1
    return None


def added_lines(repo: Path, rev_range: str) -> dict[Path, set[int]]:
    """Map each changed file to the set of post-image line numbers the diff added."""
    diff = subprocess.run(
        ["git", "-C", str(repo), "diff", "-U0", rev_range],
        check=True, capture_output=True, text=True,
    ).stdout
    out: dict[Path, set[int]] = {}
    current: Path | None = None
    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            current = repo / raw[6:]
            out.setdefault(current, set())
        elif raw.startswith("@@") and current is not None:
            m = _HUNK.match(raw)
            if not m:
                continue
            start = int(m.group(1))
            count = int(m.group(2) or 1)
            out[current].update(range(start, start + count))
    return out


def extract_diff(
    repo: Path, rev_range: str, exclude: list[str]
) -> tuple[list[Comment], list[Path]]:
    """Comments the diff added, plus the changed source files no extractor covers."""
    out: list[Comment] = []
    skipped: list[Path] = []
    for path, lines in added_lines(repo, rev_range).items():
        rel = str(path.relative_to(repo))
        if not path.exists() or any(fnmatch.fnmatch(rel, g) for g in exclude):
            continue
        if not supported(path):
            if path.suffix not in SILENT and path.name not in SILENT:
                skipped.append(path)
            continue
        for c in extract(path):
            if any(c.line <= ln <= c.end for ln in lines):
                out.append(c)
    return out, skipped
