"""End-to-end tests for the generate() public API."""

from input_gen import generate
from tests.conftest import rebuild_graph_from_adj_list


class TestGenerateBasic:
    def test_integer(self) -> None:
        result = generate({"type": "integer", "minimum": 1, "maximum": 10})
        assert isinstance(result, int) and 1 <= result <= 10

    def test_boolean(self) -> None:
        assert isinstance(generate({"type": "boolean"}), bool)

    def test_string(self) -> None:
        assert isinstance(generate({"type": "string"}), str)

    def test_float(self) -> None:
        result = generate({"type": "number", "minimum": 0.0, "maximum": 1.0})
        assert isinstance(result, float | int) and 0.0 <= result <= 1.0


class TestGenerateContainers:
    def test_array(self) -> None:
        result = generate({"type": "array", "items": {"type": "number"}, "minItems": 1})
        assert isinstance(result, list) and len(result) >= 1

    def test_set(self) -> None:
        result = generate(
            {"type": "set", "items": {"type": "string"}, "minItems": 1, "maxItems": 4}
        )
        assert isinstance(result, frozenset) and 1 <= len(result) <= 4

    def test_tuple(self) -> None:
        result = generate(
            {"type": "tuple", "prefixItems": [{"type": "integer"}, {"type": "string"}]}
        )
        assert isinstance(result, tuple) and len(result) == 2

    def test_object(self) -> None:
        result = generate({
            "type": "object",
            "properties": {"x": {"type": "integer"}, "flag": {"type": "boolean"}},
        })
        assert isinstance(result, dict) and "x" in result and "flag" in result

    def test_graph_nested_in_array(self) -> None:
        result = generate({
            "type": "array",
            "items": {
                "type": "graph",
                "directed": False,
                "weighted": False,
                "min_nodes": 2,
                "max_nodes": 5,
                "connected": False,
                "acyclic": False,
                "output_format": "adjacency_list",
            },
            "minItems": 1,
            "maxItems": 3,
        })
        assert isinstance(result, list) and 1 <= len(result) <= 3
        for g in result:
            assert isinstance(g, dict)


class TestGenerateGraph:
    def test_connected_graph(self) -> None:
        result = generate({
            "type": "graph",
            "directed": False,
            "weighted": False,
            "min_nodes": 3,
            "max_nodes": 6,
            "connected": True,
            "acyclic": False,
            "output_format": "adjacency_list",
        })
        assert isinstance(result, dict)

    def test_connected_tree_each_call(self) -> None:
        schema = {
            "type": "graph",
            "directed": False,
            "weighted": False,
            "min_nodes": 3,
            "max_nodes": 6,
            "connected": True,
            "acyclic": True,
            "output_format": "adjacency_list",
        }
        for _ in range(5):
            raw_g = generate(schema)
            graph = rebuild_graph_from_adj_list(raw_g, directed=False)
            assert len(graph) >= 3
            if len(graph) > 0:
                assert graph.number_of_edges() == len(graph) - 1


class TestGenerateIndependence:
    def test_multiple_calls_vary(self) -> None:
        """Multiple calls should not always produce identical results."""
        results = [generate({"type": "integer", "minimum": 0, "maximum": 1000}) for _ in range(20)]
        assert len(set(results)) > 1
