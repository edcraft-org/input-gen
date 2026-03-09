from collections.abc import Callable
from typing import Any

from faker import Faker
from hypothesis import strategies as st
from hypothesis_jsonschema import from_schema

_faker = Faker("en_US")

FAKER_PROVIDERS: dict[str, Callable[[], str]] = {
    "name": _faker.name,
    "first_name": _faker.first_name,
    "last_name": _faker.last_name,
    "address": _faker.address,
    "city": _faker.city,
    "country": _faker.country,
    "street_address": _faker.street_address,
    "postcode": _faker.postcode,
    "state": _faker.state,
}


def faker_string_strategy(provider: str) -> st.SearchStrategy[str]:
    """Return a Hypothesis strategy that generates realistic strings via Faker."""
    fn = FAKER_PROVIDERS.get(provider)
    if fn is None:
        raise ValueError(
            f"Unknown faker provider: {provider!r}. Available: {sorted(FAKER_PROVIDERS)}"
        )
    return st.builds(fn)


def from_json_schema(schema: dict) -> st.SearchStrategy[Any]:
    """Convert a JSON Schema for a primitive type to a Hypothesis strategy.

    If the schema has a "faker" key (and type "string"), returns a strategy
    that generates realistic strings via Faker. Otherwise delegates to
    hypothesis-jsonschema for full JSON Schema support: patterns, formats,
    enums, oneOf, etc.
    """
    if schema.get("type") == "string" and (provider := schema.get("faker")):
        return faker_string_strategy(str(provider))
    return from_schema(schema)
