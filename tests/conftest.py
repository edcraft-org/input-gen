"""Shared fixtures and helpers for the test suite."""

import networkx as nx

from input_gen.strategies.dispatch import build_strategy

# Run each test multiple times to catch non-determinism
SAMPLES = 15


def sample(schema: dict, n: int = SAMPLES) -> list:
    strat = build_strategy(schema)
    return [strat.example() for _ in range(n)]


def rebuild_graph_from_adj_list(
    adj: dict, directed: bool = False
) -> nx.Graph | nx.DiGraph:
    """Reconstruct a networkx graph from an adjacency list (unweighted)."""
    graph: nx.Graph | nx.DiGraph = nx.DiGraph() if directed else nx.Graph()
    graph.add_nodes_from(adj.keys())
    for node, neighbors in adj.items():
        for nbr in neighbors:
            graph.add_edge(node, nbr)
    return graph


def rebuild_graph_from_adj_list_weighted(
    adj: dict, directed: bool = False
) -> nx.Graph | nx.DiGraph:
    """Reconstruct a networkx graph from a weighted adjacency list."""
    graph: nx.Graph | nx.DiGraph = nx.DiGraph() if directed else nx.Graph()
    graph.add_nodes_from(adj.keys())
    for node, neighbors in adj.items():
        for nbr, w in neighbors:
            graph.add_edge(node, nbr, weight=w)
    return graph
