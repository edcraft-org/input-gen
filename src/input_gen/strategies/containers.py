from typing import Any

from hypothesis import strategies as st

from input_gen.strategies import dispatch


def array_strategy(schema: dict) -> st.SearchStrategy[Any]:
    items_schema: dict = schema.get("items", {})
    min_size: int = schema.get("minItems", 0)
    max_size: int | None = schema.get("maxItems")
    return st.lists(
        dispatch.build_strategy(items_schema),
        min_size=min_size,
        max_size=max_size,
    )


def object_strategy(schema: dict) -> st.SearchStrategy[Any]:
    properties: dict = schema.get("properties", {})
    return st.fixed_dictionaries(
        {key: dispatch.build_strategy(val) for key, val in properties.items()}
    )


def set_strategy(schema: dict) -> st.SearchStrategy[Any]:
    items_schema: dict = schema.get("items", {})
    min_size: int = schema.get("minItems", 0)
    max_size: int | None = schema.get("maxItems")
    return st.frozensets(
        dispatch.build_strategy(items_schema),
        min_size=min_size,
        max_size=max_size,
    )


def tuple_strategy(schema: dict) -> st.SearchStrategy[Any]:
    prefix_items: list[dict] = schema.get("prefixItems", [])
    return st.tuples(*[dispatch.build_strategy(s) for s in prefix_items])
