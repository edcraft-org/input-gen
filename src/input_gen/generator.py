from typing import Any

from input_gen.strategies import dispatch


def generate(schema: dict) -> Any:
    """Generate one example value from a schema.

    Args:
        schema: A JSON Schema dict or custom schema (graph, set, tuple, array, object).

    Returns:
        A single generated value matching the schema.

    Example:
        generate({"type": "integer", "minimum": 1, "maximum": 100})
        generate({"type": "graph", "directed": False, "min_nodes": 3, ...})
    """
    return dispatch.build_strategy(schema).example()
