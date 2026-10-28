import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

ITEM = re.compile(r"^( *)(\d+)[.)][ \t]")
BULLET = re.compile(r"^( *)[-*+][ \t]")
HEADING = re.compile(r"^#{1,6}[ \t]+(.*?)[ \t]*#*[ \t]*$")
FENCE = re.compile(r"^ *(`{3,}|~{3,})[ \t]*([\w-]*)")
FOOTNOTE_BODY = re.compile(r"^\[\^([^\]]+)\]:")
FOOTNOTE_MARKER = re.compile(r"\[\^([^\]]+)\]")
LINK = re.compile(r"\]\(([^)\s]+)(?:[ \t]+\"[^\"]*\")?\)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
INLINE_CODE = re.compile(r"`[^`]*`")
MERMAID_TIMEOUT_S = 120


@dataclass(frozen=True)
class Finding:
    line: int
    problem: str


@dataclass
class _Line:
    number: int
    text: str
    # Inside a fenced code block, fence lines included.
    fenced: bool


@dataclass
class _Block:
    line: int
    info: str
    body: list[str]


def check_file(path: Path) -> list[Finding]:
    """Returns every problem in the doc at `path`, in line order."""
    lines, blocks = _scan(path.read_text())
    found = _lists(lines) + _footnotes(lines) + _links(path, lines) + _mermaid(blocks)
    return sorted(found, key=lambda f: f.line)


def _scan(text: str) -> tuple[list[_Line], list[_Block]]:
    """Returns the doc's lines, each marked fenced or not, and its fenced blocks."""
    lines: list[_Line] = []
    blocks: list[_Block] = []
    fence: str | None = None
    for n, raw in enumerate(text.splitlines(), 1):
        m = FENCE.match(raw)
        if fence is None and m:
            fence = m.group(1)
            blocks.append(_Block(n, m.group(2).lower(), []))
            lines.append(_Line(n, raw, True))
        elif fence is not None:
            if raw.strip().startswith(fence[0] * len(fence)) and not raw.strip().strip(fence[0]):
                fence = None
            else:
                blocks[-1].body.append(raw)
            lines.append(_Line(n, raw, True))
        else:
            lines.append(_Line(n, raw, False))
    return lines, blocks


def _lists(lines: list[_Line]) -> list[Finding]:
    """Flags ordered-list items that skip or repeat a number.

    A list that a paragraph, callout, or code fence interrupts may continue at the next number
    or restart at 1; a heading starts every list afresh.
    """
    found: list[Finding] = []
    # Open lists, innermost last: (indent, last number).
    stack: list[tuple[int, int]] = []
    # Last number of each list that an interruption ended, by indent, since the last heading.
    ended: dict[int, int] = {}
    blank_before = False

    def close_to(indent: int) -> None:
        while stack and stack[-1][0] >= indent:
            at, last = stack.pop()
            ended[at] = last

    def check(n: int, last: int, line: int) -> None:
        if n == last:
            found.append(Finding(line, f"list item {n} repeats the previous number"))
        elif n != last + 1:
            found.append(Finding(line, f"list item {n} follows {last}; expected {last + 1}"))

    for ln in lines:
        text = ln.text
        if not text.strip():
            blank_before = True
            continue
        indent = len(text) - len(text.lstrip(" "))
        if not ln.fenced and HEADING.match(text):
            stack.clear()
            ended.clear()
        elif not ln.fenced and (m := ITEM.match(text)):
            n = int(m.group(2))
            while stack and stack[-1][0] > indent:
                stack.pop()
            if stack and stack[-1][0] == indent:
                check(n, stack[-1][1], ln.number)
                stack[-1] = (indent, n)
            else:
                if indent in ended and n != 1:
                    check(n, ended[indent], ln.number)
                ended.pop(indent, None)
                stack.append((indent, n))
        elif (not ln.fenced and BULLET.match(text)) or text.lstrip().startswith(">") or ln.fenced or blank_before:
            # A bullet, a callout, a code fence, or a paragraph after a blank line ends the lists it isn't indented under.
            close_to(indent)
        blank_before = False
    return found


def _footnotes(lines: list[_Line]) -> list[Finding]:
    """Flags footnote markers without a body and bodies without a marker."""
    bodies: dict[str, int] = {}
    markers: dict[str, int] = {}
    for ln in lines:
        if ln.fenced:
            continue
        text = ln.text
        if m := FOOTNOTE_BODY.match(text):
            bodies.setdefault(m.group(1), ln.number)
            text = text[m.end():]
        for m in FOOTNOTE_MARKER.finditer(INLINE_CODE.sub("", text)):
            markers.setdefault(m.group(1), ln.number)
    found = [Finding(line, f"footnote [^{key}] has no body") for key, line in markers.items() if key not in bodies]
    found += [Finding(line, f"footnote body [^{key}] has no marker") for key, line in bodies.items() if key not in markers]
    return found


def _links(path: Path, lines: list[_Line]) -> list[Finding]:
    """Flags relative links whose file doesn't exist or whose anchor isn't a heading in it."""
    found: list[Finding] = []
    headings: dict[Path, set[str]] = {}
    for ln in lines:
        if ln.fenced:
            continue
        for m in LINK.finditer(INLINE_CODE.sub("", ln.text)):
            target = m.group(1)
            if SCHEME.match(target) or target.startswith(("/", "~")):
                continue
            file_part, _, anchor = target.partition("#")
            dest = (path.parent / unquote(file_part)).resolve() if file_part else path.resolve()
            if not dest.exists():
                found.append(Finding(ln.number, f"link target {file_part} doesn't exist"))
                continue
            if not anchor or dest.suffix != ".md":
                continue
            if dest not in headings:
                headings[dest] = _anchors(dest)
            if anchor.lower() not in headings[dest] and unquote(anchor).casefold() not in headings[dest]:
                found.append(Finding(ln.number, f"link anchor #{anchor} isn't a heading in {file_part or path.name}"))
    return found


def _anchors(path: Path) -> set[str]:
    """Returns every anchor a heading in `path` answers to: its GitHub slug and its case-folded text."""
    out: set[str] = set()
    seen: dict[str, int] = {}
    lines, _ = _scan(path.read_text())
    for ln in lines:
        if ln.fenced or not (m := HEADING.match(ln.text)):
            continue
        title = m.group(1)
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        out.add(slug if count == 0 else f"{slug}-{count}")
        out.add(title.casefold())
    return out


def _mermaid(blocks: list[_Block]) -> list[Finding]:
    """Flags Mermaid blocks that mermaid-cli can't parse, one call per block."""
    found: list[Finding] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, block in enumerate(b for b in blocks if b.info == "mermaid"):
            src = Path(tmp) / f"block{i}.mmd"
            src.write_text("\n".join(block.body) + "\n")
            try:
                res = subprocess.run(
                    ["npx", "-y", "@mermaid-js/mermaid-cli", "-q", "-i", str(src), "-o", str(src.with_suffix(".svg"))],
                    capture_output=True, text=True, timeout=MERMAID_TIMEOUT_S,
                )
            except FileNotFoundError:
                return [Finding(block.line, "mermaid blocks unchecked: npx not found")]
            except subprocess.TimeoutExpired:
                found.append(Finding(block.line, f"mermaid block unchecked: mermaid-cli ran past {MERMAID_TIMEOUT_S} s"))
                continue
            if res.returncode:
                detail = next((l.strip() for l in res.stderr.splitlines() if "error" in l.lower()), res.stderr.strip()[:200])
                found.append(Finding(block.line, f"mermaid block doesn't parse: {detail}"))
    return found
