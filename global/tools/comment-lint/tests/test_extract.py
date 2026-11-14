from pathlib import Path

from comment_lint.extract import extract


def _comments(tmp_path: Path, name: str, source: str) -> list[tuple[int, str]]:
    path = tmp_path / name
    path.write_text(source)
    return [(c.line, c.text) for c in extract(path)]


def test_python_directives_are_dropped_and_the_text_after_them_kept(tmp_path):
    source = (
        "f = open(p)  # noqa: SIM115\n"
        "x = g()  # type: ignore[arg-type]\n"
        "# Retries once: the venue drops the first order after a reconnect.\n"
        "y = h()  # noqa: F401  # pyright: ignore[reportUnusedImport]\n"
        "z = k()  # noqa: N802 — mirrors the ib_async API\n"
    )
    assert _comments(tmp_path, "m.py", source) == [
        (3, "# Retries once: the venue drops the first order after a reconnect."),
        (5, "# mirrors the ib_async API"),
    ]


def test_dart_ignore_directives_are_dropped(tmp_path):
    source = (
        "// coverage:ignore-file\n"
        "// ignore_for_file: type=lint\n"
        "// ignore_for_file: unused_import, avoid_print\n"
        "// dart format off\n"
        "import 'a.dart';\n"
        "void main() {\n"
        "  print(x); // ignore: avoid_print\n"
        "  // Waits for the first frame before reading the size.\n"
        "  run();\n"
        "}\n"
    )
    assert _comments(tmp_path, "m.dart", source) == [
        (8, "// Waits for the first frame before reading the size."),
    ]
