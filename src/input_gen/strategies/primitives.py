from typing import Any

from hypothesis import strategies as st
from hypothesis_jsonschema import from_schema


def from_json_schema(schema: dict) -> st.SearchStrategy[Any]:
    """Convert a JSON Schema for a primitive type to a Hypothesis strategy.

    Delegates to hypothesis-jsonschema for full JSON Schema support:
    patterns, formats, enums, oneOf, etc.
    """
    return from_schema(schema)
