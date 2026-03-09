"""Tests for primitive type generation (integer, number, string, boolean, enum)."""

import re

import pytest

from input_gen.strategies.dispatch import build_strategy
from tests.conftest import sample


class TestInteger:
    def test_type(self) -> None:
        for v in sample({"type": "integer"}):
            assert isinstance(v, int)

    def test_bounds(self) -> None:
        for v in sample({"type": "integer", "minimum": 1, "maximum": 100}):
            assert 1 <= v <= 100

    def test_exclusive_bounds(self) -> None:
        for v in sample(
            {"type": "integer", "exclusiveMinimum": 0, "exclusiveMaximum": 5}
        ):
            assert 0 < v < 5


class TestNumber:
    def test_type(self) -> None:
        for v in sample({"type": "number"}):
            assert isinstance(v, float | int)

    def test_bounds(self) -> None:
        for v in sample({"type": "number", "minimum": -1.0, "maximum": 1.0}):
            assert -1.0 <= v <= 1.0


class TestString:
    def test_type(self) -> None:
        for v in sample({"type": "string"}):
            assert isinstance(v, str)

    def test_min_max_length(self) -> None:
        for v in sample({"type": "string", "minLength": 3, "maxLength": 8}):
            assert 3 <= len(v) <= 8

    def test_pattern(self) -> None:
        pattern = "^[a-z]{3}$"
        for v in sample({"type": "string", "pattern": pattern}, n=10):
            assert re.fullmatch(pattern, v), f"{v!r} does not match {pattern}"


class TestBoolean:
    def test_type(self) -> None:
        for v in sample({"type": "boolean"}):
            assert isinstance(v, bool)

    def test_both_values_possible(self) -> None:
        values = set(sample({"type": "boolean"}, n=50))
        assert values == {True, False}


class TestEnum:
    def test_enum_values(self) -> None:
        choices = [1, "hello", True]
        for v in sample({"enum": choices}, n=30):
            assert v in choices

    def test_string_enum(self) -> None:
        choices = ["red", "green", "blue"]
        for v in sample({"enum": choices}):
            assert v in choices


class TestOneOf:
    def test_one_of(self) -> None:
        schema = {"oneOf": [{"type": "integer"}, {"type": "string"}]}
        for v in sample(schema, n=10):
            assert isinstance(v, int | str)


@pytest.mark.parametrize("run", range(5))
def test_integer_determinism_runs(run: int) -> None:
    """Ensure multiple calls produce valid results (not always the same)."""
    vals = [
        build_strategy({"type": "integer", "minimum": 0, "maximum": 1000}).example()
        for _ in range(10)
    ]
    assert all(0 <= v <= 1000 for v in vals)
