from typing import Any

import networkx as nx
from hypothesis import strategies as st
from hypothesis.strategies import composite


def _max_edges(num_nodes: int, directed: bool) -> int:
    return num_nodes * (num_nodes - 1) if directed else num_nodes * (num_nodes - 1) // 2


def _orient_as_dag(undirected: nx.Graph) -> nx.DiGraph:
    """Orient an undirected graph as a DAG using per-component BFS."""
    dag: nx.DiGraph = nx.DiGraph()
    dag.add_nodes_from(undirected.nodes())
    for component in nx.connected_components(undirected):
        subgraph = undirected.subgraph(component)
        root = next(iter(component))
        for u, v in nx.bfs_edges(subgraph, source=root):
            dag.add_edge(u, v)
    return dag


def _build_connected_acyclic(
    num_nodes: int, directed: bool, nodes: list, rng: Any
) -> nx.Graph | nx.DiGraph:
    """Build a spanning tree; orient as DAG if directed."""
    tree: nx.Graph = nx.random_labeled_tree(num_nodes, seed=rng)
    mapping = {i: nodes[i] for i in range(num_nodes)}
    tree = nx.relabel_nodes(tree, mapping)
    if directed:
        return _orient_as_dag(tree)
    return tree


def _build_connected_cyclic(
    num_nodes: int,
    num_edges: int,
    directed: bool,
    nodes: list,
    rng: Any,
) -> nx.Graph | nx.DiGraph:
    """Spanning tree + random extra edges to reach num_edges total edges."""
    graph: nx.Graph | nx.DiGraph = nx.DiGraph() if directed else nx.Graph()
    graph.add_nodes_from(nodes)

    # Spanning tree for connectivity
    undirected_tree: nx.Graph = nx.random_labeled_tree(num_nodes, seed=rng)
    mapping = {i: nodes[i] for i in range(num_nodes)}
    undirected_tree = nx.relabel_nodes(undirected_tree, mapping)

    if directed:
        # BFS-orient the tree so the result is weakly connected
        root = nodes[0]
        for u, v in nx.bfs_edges(undirected_tree, source=root):
            graph.add_edge(u, v)
    else:
        graph.add_edges_from(undirected_tree.edges())

    # Add extra edges up to num_edges
    max_e = _max_edges(num_nodes, directed)
    target = min(num_edges, max_e)
    all_possible = [
        (u, v)
        for u in nodes
        for v in nodes
        if u != v
        and not graph.has_edge(u, v)
        and (directed or not graph.has_edge(v, u))
    ]
    rng.shuffle(all_possible)
    needed = target - graph.number_of_edges()
    for u, v in all_possible[:needed]:
        graph.add_edge(u, v)
    return graph


def _build_forest(
    num_nodes: int, num_edges: int, directed: bool, nodes: list, rng: Any
) -> nx.Graph | nx.DiGraph:
    """Random forest (possibly disconnected acyclic graph) with exactly num_edges edges."""
    if num_nodes <= 1:
        result: nx.Graph | nx.DiGraph = nx.DiGraph() if directed else nx.Graph()
        result.add_nodes_from(nodes)
        return result

    undirected_tree: nx.Graph = nx.random_labeled_tree(num_nodes, seed=rng)
    mapping = {i: nodes[i] for i in range(num_nodes)}
    undirected_tree = nx.relabel_nodes(undirected_tree, mapping)

    # Remove edges to reach num_edges (clamped to valid forest range)
    target = max(0, min(num_edges, num_nodes - 1))
    edges = list(undirected_tree.edges())
    rng.shuffle(edges)
    undirected_tree.remove_edges_from(edges[target:])

    if directed:
        return _orient_as_dag(undirected_tree)
    return undirected_tree


def _build_random(
    num_nodes: int, num_edges: int, directed: bool, nodes: list, rng: Any
) -> nx.Graph | nx.DiGraph:
    """Arbitrary random graph with num_edges edges."""
    graph: nx.Graph | nx.DiGraph = nx.gnm_random_graph(
        num_nodes, num_edges, directed=directed, seed=rng
    )
    mapping = {i: nodes[i] for i in range(num_nodes)}
    return nx.relabel_nodes(graph, mapping)


def _to_adjacency_list(graph: nx.Graph | nx.DiGraph, weighted: bool) -> dict:
    result: dict = {}
    for node in graph.nodes():
        if weighted:
            result[node] = [
                (nbr, graph[node][nbr].get("weight", 1.0))
                for nbr in graph.neighbors(node)
            ]
        else:
            result[node] = list(graph.neighbors(node))
    return result


def _to_adjacency_matrix(graph: nx.Graph | nx.DiGraph, weighted: bool) -> list[list]:
    nodes = sorted(graph.nodes(), key=str)
    n = len(nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}
    matrix: list[list] = [[0.0 if weighted else 0] * n for _ in range(n)]
    for u, v, data in graph.edges(data=True):
        w = data.get("weight", 1.0) if weighted else 1
        matrix[node_idx[u]][node_idx[v]] = w
        if not graph.is_directed():
            matrix[node_idx[v]][node_idx[u]] = w
    return matrix


def _to_edge_list(graph: nx.Graph | nx.DiGraph, weighted: bool) -> list:
    if weighted:
        return [
            (u, v, data.get("weight", 1.0)) for u, v, data in graph.edges(data=True)
        ]
    return list(graph.edges())


@composite
def graph_strategy(draw: Any, schema: dict) -> Any:  # noqa: C901
    from input_gen.strategies import dispatch

    directed: bool = schema.get("directed", False)
    weighted: bool = schema.get("weighted", False)
    min_nodes: int = schema.get("min_nodes", 1)
    max_nodes: int = schema.get("max_nodes", 10)
    min_edges: int | None = schema.get("min_edges")
    max_edges: int | None = schema.get("max_edges")
    connected: bool = schema.get("connected", False)
    acyclic: bool = schema.get("acyclic", False)
    node_schema: dict | None = schema.get("node_schema")
    output_format: str = schema.get("output_format", "adjacency_list")
    weight_min: float = schema.get("weight_min", 1.0)
    weight_max: float = schema.get("weight_max", 10.0)

    rng = draw(st.randoms())

    # Draw node count
    num_nodes = draw(st.integers(min_value=min_nodes, max_value=max_nodes))

    # Draw node labels
    if node_schema is not None:
        nodes = list(
            draw(
                st.frozensets(
                    dispatch.build_strategy(node_schema),
                    min_size=num_nodes,
                    max_size=num_nodes,
                )
            )
        )
    else:
        nodes = list(range(num_nodes))

    # Determine edge count range
    max_possible = _max_edges(num_nodes, directed)
    if connected and acyclic:
        # Spanning tree always has exactly num_nodes - 1 edges
        fixed_edges = max(0, num_nodes - 1)
        if min_edges is not None and min_edges > fixed_edges:
            msg = (
                f"min_edges={min_edges} is impossible for a connected acyclic graph "
                f"with {num_nodes} nodes (always has exactly {fixed_edges} edges)"
            )
            raise ValueError(msg)
        if max_edges is not None and max_edges < fixed_edges:
            msg = (
                f"max_edges={max_edges} is impossible for a connected acyclic graph "
                f"with {num_nodes} nodes (always has exactly {fixed_edges} edges)"
            )
            raise ValueError(msg)
        num_edges = fixed_edges
    else:
        low = min_edges if min_edges is not None else 0
        if connected:
            # Connected graph needs at least num_nodes - 1 edges
            min_for_connected = max(0, num_nodes - 1)
            if max_edges is not None and max_edges < min_for_connected:
                msg = (
                    f"max_edges={max_edges} is impossible for a connected graph "
                    f"with {num_nodes} nodes (requires at least {min_for_connected} edges)"
                )
                raise ValueError(msg)
            low = max(low, min_for_connected)
        if not connected and acyclic:
            # Forest has at most num_nodes - 1 edges
            max_for_forest = max(0, num_nodes - 1)
            if min_edges is not None and min_edges > max_for_forest:
                msg = (
                    f"min_edges={min_edges} is impossible for an acyclic graph "
                    f"with {num_nodes} nodes (forest has at most {max_for_forest} edges)"
                )
                raise ValueError(msg)
            max_possible = min(max_possible, max_for_forest)
        high = min(max_edges if max_edges is not None else max_possible, max_possible)
        high = max(high, low)
        num_edges = draw(st.integers(min_value=low, max_value=high))

    # Build graph
    result_graph: nx.Graph | nx.DiGraph
    if connected and acyclic:
        result_graph = _build_connected_acyclic(num_nodes, directed, nodes, rng)
    elif connected and not acyclic:
        result_graph = _build_connected_cyclic(num_nodes, num_edges, directed, nodes, rng)
    elif not connected and acyclic:
        result_graph = _build_forest(num_nodes, num_edges, directed, nodes, rng)
    else:
        result_graph = _build_random(num_nodes, num_edges, directed, nodes, rng)

    # Add weights
    if weighted:
        for u, v in result_graph.edges():
            result_graph[u][v]["weight"] = draw(
                st.floats(min_value=weight_min, max_value=weight_max)
            )

    # Convert to output format
    if output_format == "adjacency_list":
        return _to_adjacency_list(result_graph, weighted)
    if output_format == "adjacency_matrix":
        return _to_adjacency_matrix(result_graph, weighted)
    if output_format == "edge_list":
        return _to_edge_list(result_graph, weighted)

    msg = f"Unknown output_format: {output_format!r}"
    raise ValueError(msg)
