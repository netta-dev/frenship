"""`jevsort`: rank items by one question, with jev weighing each item against all the others in a single Choice.

    jevsort --question 'Which should go first?' [--context TEXT] < items.jsonl
    jevsort --question ... --top 10 --json items.jsonl

Each input line is `{"id": ..., "text": ...}`; at most 255 items, jev's Choice limit, and about 32k
tokens in all, its per-call budget; past either, it stops. One call's
probabilities come rounded to 0.01 and favor the first few options, so the ranking averages
`--repeats` calls, each listing the options in a different order.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
from pathlib import Path

from typesafe_sdk import AsyncTypeSafeClient, Choice

MODEL = "jev-latest"
MAX_ITEMS = 255
# jev's budget for the state plus the longest question; every item's text goes into that one question.
MAX_TOKENS = 32_000
# Measured on jev: 89,950 characters of inbox items came to 25,387 input tokens.
CHARS_PER_TOKEN = 3.5
CONCURRENCY = 8


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="jevsort")
    ap.add_argument("input", nargs="?", type=Path, help="JSON-lines file; stdin when omitted")
    ap.add_argument("--question", required=True, help="asks which item comes first")
    ap.add_argument("--context", help="background jev reads with every call")
    ap.add_argument("--repeats", type=int, default=10, help="calls to average, each in a different option order")
    ap.add_argument("--seed", type=int, default=0, help="seeds the option orders")
    ap.add_argument("--top", type=int, help="print only the first N")
    ap.add_argument("--json", action="store_true", help="emit one JSON object per item")
    args = ap.parse_args(argv)

    lines = (args.input.read_text() if args.input else sys.stdin.read()).splitlines()
    items = [json.loads(line) for line in lines if line.strip()]
    _load_key()
    try:
        ranked, tokens = asyncio.run(_rank_with_api(items, args))
    except ValueError as e:
        print(f"jevsort: {e}", file=sys.stderr)
        return 2
    for n, (id_, score) in enumerate(ranked[: args.top], 1):
        if args.json:
            print(json.dumps({"rank": n, "id": id_, "score": round(score, 4)}))
        else:
            print(f"{n:3}  {score:.3f}  {id_}")
    print(f"{len(items)} items, {args.repeats} calls; tokens in={tokens}", file=sys.stderr)
    return 0


async def _rank_with_api(items: list[dict], args: argparse.Namespace) -> tuple[list[tuple[str, float]], int]:
    async with AsyncTypeSafeClient() as client:
        return await rank(client, items, args.question, args.context, args.repeats, args.seed)


async def rank(
    client, items: list[dict], question: str, context: str | None, repeats: int, seed: int
) -> tuple[list[tuple[str, float]], int]:
    """Return each item's id with its mean probability of being picked first, best first, and the input tokens used.

    `items` are `{"id", "text"}` dicts with unique ids, 2 to 255 of them, within jev's token budget;
    anything else raises ValueError.
    Equal scores keep input order.
    """
    ids = [it["id"] for it in items]
    if not 2 <= len(ids) <= MAX_ITEMS:
        raise ValueError(f"needs 2 to {MAX_ITEMS} items, got {len(ids)}")
    if len(set(ids)) != len(ids):
        raise ValueError("item ids must be unique")
    chars = len(question) + len(context or "") + sum(len(it["text"]) for it in items)
    if chars / CHARS_PER_TOKEN > MAX_TOKENS:
        raise ValueError(
            f"the items come to about {chars / CHARS_PER_TOKEN:,.0f} tokens, over jev's {MAX_TOKENS:,} per call; "
            "splitting them across calls isn't built yet"
        )
    state = {"context": context} if context else {}
    sem = asyncio.Semaphore(CONCURRENCY)

    async def ask(order: list[int]) -> tuple[dict[int, float], int]:
        # The labels are neutral so that an id can't sway the pick.
        labels = {f"p{n + 1}": i for n, i in enumerate(order)}
        q = Choice(instructions=question, criteria={label: items[i]["text"] for label, i in labels.items()})
        async with sem:
            r = await client.system_one(state=state, questions={"first": q}, model=MODEL)
        probs = r.choices["first"].probabilities
        return {i: probs.get(label, 0.0) for label, i in labels.items()}, r.usage.input_tokens or 0

    answers = await asyncio.gather(*(ask(o) for o in orders(len(ids), repeats, seed)))
    mean = [sum(a[i] for a, _ in answers) / len(answers) for i in range(len(ids))]
    ranked = sorted(range(len(ids)), key=lambda i: -mean[i])
    return [(ids[i], mean[i]) for i in ranked], sum(t for _, t in answers)


def orders(n: int, repeats: int, seed: int) -> list[list[int]]:
    """Return `repeats` permutations of range(n). Each shuffle is followed by its reverse, which centers every item's mean position."""
    rng = random.Random(seed)
    out: list[list[int]] = []
    while len(out) < repeats:
        order = list(range(n))
        rng.shuffle(order)
        out += [order, order[::-1]]
    return out[:repeats]


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


if __name__ == "__main__":
    sys.exit(main())
