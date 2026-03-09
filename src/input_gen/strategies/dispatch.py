from typing import Any

from hypothesis import strategies as st

from input_gen.strategies import containers, graphs, primitives


def build_strategy(schema: dict) -> st.SearchStrategy[Any]:
    """Route a schema to the appropriate strategy builder."""
    schema_type: str = schema.get("type", "")

    if schema_type == "graph":
        return graphs.graph_strategy(schema)
    if schema_type == "set":
        return containers.set_strategy(schema)
    if schema_type == "tuple":
        return containers.tuple_strategy(schema)
    if schema_type == "array":
        return containers.array_strategy(schema)
    if schema_type == "object":
        return containers.object_strategy(schema)

    return primitives.from_json_schema(schema)
