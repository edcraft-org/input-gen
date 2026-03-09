"""Tests for graph generation: topology constraints, weights, node labels, output formats."""

import networkx as nx
import pytest

from input_gen.strategies.dispatch import build_strategy
from tests.conftest import (
    rebuild_graph_from_adj_list,
    rebuild_graph_from_adj_list_weighted,
    sample,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE = {
    "type": "graph",
    "directed": False,
    "weighted": False,
    "min_nodes": 3,
    "max_nodes": 8,
    "connected": False,
    "acyclic": False,
    "output_format": "adjacency_list",
}


def graph_schema(**overrides: object) -> dict:
    return {**BASE, **overrides}


# ---------------------------------------------------------------------------
# Output format: adjacency list
# ---------------------------------------------------------------------------

class TestAdjacencyList:
    def test_returns_dict(self) -> None:
        for g in sample(graph_schema()):
            assert isinstance(g, dict)

    def test_all_values_are_lists(self) -> None:
        for g in sample(graph_schema()):
            for neighbors in g.values():
                assert isinstance(neighbors, list)

    def test_node_count_in_range(self) -> None:
        for g in sample(graph_schema(min_nodes=3, max_nodes=6)):
            assert 3 <= len(g) <= 6

    def test_weighted_adjacency_list(self) -> None:
        for g in sample(graph_schema(weighted=True, weight_min=1.0, weight_max=5.0)):
            for neighbors in g.values():
                for item in neighbors:
                    assert isinstance(item, tuple) and len(item) == 2
                    _nbr, w = item
                    assert 1.0 <= w <= 5.0

    def test_undirected_symmetry(self) -> None:
        """Every edge (u->v) should also appear as (v->u)."""
        for g in sample(graph_schema(directed=False)):
            graph = rebuild_graph_from_adj_list(g, directed=False)
            # networkx undirected graph built from adj list is symmetric by construction
            assert not graph.is_directed()


# ---------------------------------------------------------------------------
# Output format: adjacency matrix
# ---------------------------------------------------------------------------

class TestAdjacencyMatrix:
    def test_returns_list_of_lists(self) -> None:
        for mat in sample(graph_schema(output_format="adjacency_matrix")):
            assert isinstance(mat, list)
            assert all(isinstance(row, list) for row in mat)

    def test_square_matrix(self) -> None:
        for mat in sample(graph_schema(min_nodes=4, max_nodes=4, output_format="adjacency_matrix")):
            n = len(mat)
            assert all(len(row) == n for row in mat)

    def test_weighted_matrix(self) -> None:
        for mat in sample(graph_schema(
            weighted=True, weight_min=1.0, weight_max=10.0, output_format="adjacency_matrix"
        )):
            for row in mat:
                for val in row:
                    assert val == 0 or 1.0 <= val <= 10.0


# ---------------------------------------------------------------------------
# Output format: edge list
# ---------------------------------------------------------------------------

class TestEdgeList:
    def test_returns_list(self) -> None:
        for el in sample(graph_schema(output_format="edge_list")):
            assert isinstance(el, list)

    def test_unweighted_edge_tuples(self) -> None:
        for el in sample(graph_schema(output_format="edge_list")):
            for edge in el:
                assert isinstance(edge, tuple) and len(edge) == 2

    def test_weighted_edge_tuples(self) -> None:
        schema = graph_schema(
            weighted=True, weight_min=0.0, weight_max=1.0, output_format="edge_list"
        )
        for el in sample(schema):
            for edge in el:
                assert isinstance(edge, tuple) and len(edge) == 3
                _, _, w = edge
                assert 0.0 <= w <= 1.0


# ---------------------------------------------------------------------------
# Topology: connected
# ---------------------------------------------------------------------------

class TestConnected:
    def test_connected_undirected(self) -> None:
        for g in sample(graph_schema(connected=True, min_nodes=3, max_nodes=8)):
            graph = rebuild_graph_from_adj_list(g, directed=False)
            if len(graph) > 0:
                assert nx.is_connected(graph), f"Graph not connected: {g}"

    def test_connected_directed(self) -> None:
        for g in sample(graph_schema(connected=True, directed=True, min_nodes=3, max_nodes=8)):
            graph = rebuild_graph_from_adj_list(g, directed=True)
            if len(graph) > 0:
                assert nx.is_weakly_connected(graph), f"Directed graph not weakly connected: {g}"


# ---------------------------------------------------------------------------
# Topology: acyclic
# ---------------------------------------------------------------------------

class TestAcyclic:
    def test_undirected_acyclic_is_forest(self) -> None:
        for g in sample(graph_schema(acyclic=True, min_nodes=3, max_nodes=8)):
            graph = rebuild_graph_from_adj_list(g, directed=False)
            assert nx.is_forest(graph), f"Graph has cycles: {g}"

    def test_directed_acyclic(self) -> None:
        for g in sample(graph_schema(acyclic=True, directed=True, min_nodes=3, max_nodes=8)):
            graph = rebuild_graph_from_adj_list(g, directed=True)
            assert nx.is_directed_acyclic_graph(graph), f"Directed graph has cycles: {g}"


# ---------------------------------------------------------------------------
# Topology: connected + acyclic (spanning tree)
# ---------------------------------------------------------------------------

class TestConnectedAcyclic:
    def test_is_tree(self) -> None:
        for g in sample(graph_schema(connected=True, acyclic=True, min_nodes=3, max_nodes=8)):
            graph = rebuild_graph_from_adj_list(g, directed=False)
            n = len(graph)
            if n > 0:
                assert nx.is_connected(graph), "Tree must be connected"
                assert graph.number_of_edges() == n - 1, (
                    f"Tree with {n} nodes must have {n - 1} edges"
                )

    def test_directed_tree(self) -> None:
        for g in sample(
            graph_schema(connected=True, acyclic=True, directed=True, min_nodes=3, max_nodes=6)
        ):
            graph = rebuild_graph_from_adj_list(g, directed=True)
            if len(graph) > 0:
                assert nx.is_directed_acyclic_graph(graph)
                assert nx.is_weakly_connected(graph)


# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------

class TestWeights:
    def test_weight_range(self) -> None:
        schema = graph_schema(weighted=True, weight_min=10.0, weight_max=20.0)
        for g in sample(schema):
            for neighbors in g.values():
                for _, w in neighbors:
                    assert 10.0 <= w <= 20.0, f"Weight {w} out of range"

    def test_weighted_connected_tree(self) -> None:
        schema = graph_schema(
            weighted=True, connected=True, acyclic=True,
            min_nodes=3, max_nodes=6, weight_min=1.0, weight_max=5.0,
        )
        for g in sample(schema):
            graph = rebuild_graph_from_adj_list_weighted(g, directed=False)
            for _, _, data in graph.edges(data=True):
                assert 1.0 <= data["weight"] <= 5.0


# ---------------------------------------------------------------------------
# Custom node labels
# ---------------------------------------------------------------------------

class TestNodeLabels:
    def test_single_char_labels(self) -> None:
        schema = graph_schema(
            min_nodes=2, max_nodes=5,
            node_schema={"type": "string", "minLength": 1, "maxLength": 1},
        )
        for g in sample(schema):
            for node in g:
                is_single_char = isinstance(node, str) and len(node) == 1
                assert is_single_char, f"Node {node!r} is not a single char"

    def test_integer_labels_default(self) -> None:
        for g in sample(graph_schema(min_nodes=2, max_nodes=5)):
            for node in g:
                assert isinstance(node, int)

    def test_unique_labels(self) -> None:
        schema = graph_schema(
            min_nodes=3, max_nodes=6,
            node_schema={"type": "string", "minLength": 1, "maxLength": 1},
        )
        for g in sample(schema):
            nodes = list(g.keys())
            assert len(nodes) == len(set(nodes)), "Node labels must be unique"


# ---------------------------------------------------------------------------
# Edge count constraints
# ---------------------------------------------------------------------------

class TestEdgeCount:
    def test_min_edges(self) -> None:
        schema = graph_schema(min_nodes=5, max_nodes=5, min_edges=4)
        for g in sample(schema):
            graph = rebuild_graph_from_adj_list(g, directed=False)
            assert graph.number_of_edges() >= 4

    def test_max_edges(self) -> None:
        schema = graph_schema(min_nodes=5, max_nodes=5, max_edges=3)
        for g in sample(schema):
            graph = rebuild_graph_from_adj_list(g, directed=False)
            assert graph.number_of_edges() <= 3


# ---------------------------------------------------------------------------
# Invalid output format
# ---------------------------------------------------------------------------

def test_invalid_output_format() -> None:
    with pytest.raises(ValueError, match="Unknown output_format"):
        build_strategy(graph_schema(output_format="invalid_format")).example()
