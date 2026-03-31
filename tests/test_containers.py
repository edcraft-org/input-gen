"""Tests for container type generation (array, object, set, tuple) including nesting."""

from tests.conftest import sample


class TestArray:
    def test_type(self) -> None:
        for v in sample({"type": "array", "items": {"type": "integer"}}):
            assert isinstance(v, list)

    def test_element_types(self) -> None:
        for v in sample({"type": "array", "items": {"type": "integer"}}):
            assert all(isinstance(x, int) for x in v)

    def test_min_items(self) -> None:
        for v in sample({"type": "array", "items": {"type": "string"}, "minItems": 3}):
            assert len(v) >= 3

    def test_max_items(self) -> None:
        for v in sample({"type": "array", "items": {"type": "boolean"}, "maxItems": 2}):
            assert len(v) <= 2

    def test_min_max_items(self) -> None:
        schema = {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 2,
            "maxItems": 5,
        }
        for v in sample(schema):
            assert 2 <= len(v) <= 5

    def test_sorted(self) -> None:
        schema = {
            "type": "array",
            "items": {"type": "integer", "minimum": 0, "maximum": 100},
            "minItems": 2,
            "maxItems": 8,
            "sorted": True,
        }
        for v in sample(schema):
            assert v == sorted(v)

    def test_unique(self) -> None:
        schema = {
            "type": "array",
            "items": {"type": "integer", "minimum": 0, "maximum": 1000},
            "minItems": 5,
            "maxItems": 10,
            "unique": True,
        }
        for v in sample(schema):
            assert len(v) == len(set(v))

    def test_nested_array(self) -> None:
        schema = {
            "type": "array",
            "items": {"type": "array", "items": {"type": "integer"}, "minItems": 1},
            "minItems": 1,
        }
        for v in sample(schema):
            assert isinstance(v, list)
            for inner in v:
                assert isinstance(inner, list)
                assert len(inner) >= 1


class TestObject:
    def test_type(self) -> None:
        schema = {
            "type": "object",
            "properties": {"x": {"type": "integer"}, "y": {"type": "string"}},
        }
        for v in sample(schema):
            assert isinstance(v, dict)

    def test_all_keys_present(self) -> None:
        schema = {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "boolean"}},
        }
        for v in sample(schema):
            assert "a" in v and "b" in v

    def test_value_types(self) -> None:
        schema = {
            "type": "object",
            "properties": {"n": {"type": "integer"}, "flag": {"type": "boolean"}},
        }
        for v in sample(schema):
            assert isinstance(v["n"], int)
            assert isinstance(v["flag"], bool)


class TestSet:
    def test_type(self) -> None:
        for v in sample({"type": "set", "items": {"type": "integer"}}):
            assert isinstance(v, frozenset)

    def test_element_types(self) -> None:
        for v in sample({"type": "set", "items": {"type": "integer"}}):
            assert all(isinstance(x, int) for x in v)

    def test_min_max_size(self) -> None:
        for v in sample(
            {"type": "set", "items": {"type": "string"}, "minItems": 2, "maxItems": 4}
        ):
            assert 2 <= len(v) <= 4

    def test_uniqueness(self) -> None:
        # frozenset already guarantees unique elements; this confirms it
        for v in sample({"type": "set", "items": {"type": "integer"}, "minItems": 3}):
            assert len(v) == len(set(v))


class TestTuple:
    def test_type(self) -> None:
        schema = {
            "type": "tuple",
            "prefixItems": [{"type": "integer"}, {"type": "string"}],
        }
        for v in sample(schema):
            assert isinstance(v, tuple)

    def test_length(self) -> None:
        schema = {
            "type": "tuple",
            "prefixItems": [{"type": "integer"}, {"type": "string"}],
        }
        for v in sample(schema):
            assert len(v) == 2

    def test_element_types(self) -> None:
        schema = {
            "type": "tuple",
            "prefixItems": [
                {"type": "integer"},
                {"type": "string"},
                {"type": "boolean"},
            ],
        }
        for v in sample(schema):
            assert isinstance(v[0], int)
            assert isinstance(v[1], str)
            assert isinstance(v[2], bool)


class TestNestedCustomTypes:
    def test_array_of_tuples(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "type": "tuple",
                "prefixItems": [{"type": "number"}, {"type": "boolean"}],
            },
            "minItems": 2,
        }
        for v in sample(schema):
            assert len(v) >= 2
            for item in v:
                assert isinstance(item, tuple)
                assert isinstance(item[0], float | int)
                assert isinstance(item[1], bool)

    def test_set_of_strings(self) -> None:
        schema = {
            "type": "set",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1,
        }
        for v in sample(schema):
            assert isinstance(v, frozenset)
            assert all(isinstance(s, str) and len(s) >= 1 for s in v)

    def test_object_with_array_value(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "nums": {"type": "array", "items": {"type": "integer"}, "minItems": 1},
            },
        }
        for v in sample(schema):
            assert isinstance(v["nums"], list)
            assert len(v["nums"]) >= 1
