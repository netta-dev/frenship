import asyncio
from types import SimpleNamespace

import pytest

from jevsort.cli import MAX_ITEMS, MAX_TOKENS, orders, rank


class FakeJev:
    """Answers each Choice with probabilities proportional to a fixed weight per option text."""

    def __init__(self, weights: dict[str, float]):
        self.weights = weights
        self.criteria: list[dict[str, str]] = []

    async def system_one(self, *, state, questions, model):
        criteria = dict(questions["first"].criteria)
        self.criteria.append(criteria)
        total = sum(self.weights[text] for text in criteria.values())
        probs = {label: self.weights[text] / total for label, text in criteria.items()}
        return SimpleNamespace(
            choices={"first": SimpleNamespace(probabilities=probs)},
            usage=SimpleNamespace(input_tokens=100),
        )


def _items(weights: dict[str, float]) -> list[dict]:
    return [{"id": f"id-{text}", "text": text} for text in weights]


def test_rank_maps_every_shuffled_label_back_to_its_item():
    weights = {"low": 1.0, "top": 8.0, "mid": 3.0, "tiny": 0.5}
    jev = FakeJev(weights)

    ranked, tokens = asyncio.run(rank(jev, _items(weights), "which first?", None, repeats=6, seed=3))

    assert [id_ for id_, _ in ranked] == ["id-top", "id-mid", "id-low", "id-tiny"]
    assert ranked[0][1] == pytest.approx(8.0 / 12.5)
    assert tokens == 600
    assert len({tuple(c.values()) for c in jev.criteria}) > 1, "option order should vary between calls"
    assert all(set(c) == {"p1", "p2", "p3", "p4"} for c in jev.criteria)


def test_orders_follow_each_shuffle_with_its_reverse():
    out = orders(6, 5, seed=1)

    assert len(out) == 5
    assert all(sorted(o) == list(range(6)) for o in out)
    assert out[1] == out[0][::-1] and out[3] == out[2][::-1]


@pytest.mark.parametrize("n", [1, MAX_ITEMS + 1])
def test_rank_rejects_item_counts_outside_the_choice_limit(n):
    weights = {f"t{i}": 1.0 for i in range(n)}
    with pytest.raises(ValueError, match="items"):
        asyncio.run(rank(FakeJev(weights), _items(weights), "q", None, 2, 0))


def test_rank_rejects_duplicate_ids():
    items = [{"id": "a", "text": "x"}, {"id": "a", "text": "y"}]
    with pytest.raises(ValueError, match="unique"):
        asyncio.run(rank(FakeJev({"x": 1.0, "y": 1.0}), items, "q", None, 2, 0))


def test_rank_rejects_items_over_jevs_token_budget():
    weights = {"x" * (MAX_TOKENS * 2) + str(i): 1.0 for i in range(3)}
    with pytest.raises(ValueError, match="tokens"):
        asyncio.run(rank(FakeJev(weights), _items(weights), "q", None, 2, 0))
