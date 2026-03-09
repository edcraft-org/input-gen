# Input Generator

A Python package that converts a JSON config into [Hypothesis](https://hypothesis.readthedocs.io/) strategies and generates inputs.

## How it works

1. Frontend defines input constraints (e.g. "an integer between 1 and 100")
2. Constraints are expressed as a JSON config and sent to the backend
3. Backend calls `generate(schema)` from this package for each schema in the config
4. The package converts the schema into a Hypothesis strategy and calls `.example()` to produce a value
5. Generated inputs are returned to the frontend

## Installation

```bash
uv sync
```

## Usage

```python
from input_gen import generate

generate({"type": "integer", "minimum": 1, "maximum": 100})  # 42
generate({"type": "boolean"})                                 # True
generate({"type": "string", "minLength": 1, "maxLength": 10}) # "hello"
```

`generate(schema)` takes a single schema and returns one generated value. The backend calls it once per input per value.

---

## Schema format

Each `schema` is either a standard JSON Schema object or one of the custom extensions described below.

### Standard types (via JSON Schema)

These follow the [JSON Schema](https://json-schema.org/) spec and support the full range of keywords (`minimum`, `maximum`, `minLength`, `pattern`, `enum`, `oneOf`, etc.).

| `"type"` | Example schema |
|---|---|
| `"integer"` | `{"type": "integer", "minimum": 0, "maximum": 100}` |
| `"number"` | `{"type": "number", "minimum": -1.0, "maximum": 1.0}` |
| `"string"` | `{"type": "string", "minLength": 3, "pattern": "^[a-z]+$"}` |
| `"boolean"` | `{"type": "boolean"}` |

### Container types

Container types are handled natively by the package and support **arbitrary nesting** — including custom types like `graph` inside arrays.

#### `"array"`

```json
{
  "type": "array",
  "items": {"type": "integer", "minimum": 0},
  "minItems": 1,
  "maxItems": 10
}
```

#### `"set"`

Returns a Python `frozenset`. Elements must be hashable.

```json
{
  "type": "set",
  "items": {"type": "string"},
  "minItems": 0,
  "maxItems": 5
}
```

#### `"tuple"`

Returns a Python `tuple` with per-position types defined by `items`.

```json
{
  "type": "tuple",
  "prefixItems": [{"type": "integer"}, {"type": "string"}]
}
```

#### `"object"`

```json
{
    "type": "object",
    "properties": {
        "x": {"type": "integer"}
    }
}
```

### Graph type

```json
{
  "type": "graph",
  "directed": false,
  "weighted": false,
  "min_nodes": 3,
  "max_nodes": 10,
  "min_edges": null,
  "max_edges": null,
  "connected": true,
  "acyclic": false,
  "node_schema": {"type": "string", "minLength": 1, "maxLength": 1},
  "output_format": "adjacency_list",
  "weight_min": 1.0,
  "weight_max": 10.0
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `directed` | bool | `false` | Whether edges have direction |
| `weighted` | bool | `false` | Whether edges have numeric weights |
| `min_nodes` | int | `1` | Minimum number of nodes |
| `max_nodes` | int | `10` | Maximum number of nodes |
| `min_edges` | int\|null | `null` | Minimum edges (null = unconstrained) |
| `max_edges` | int\|null | `null` | Maximum edges (null = unconstrained) |
| `connected` | bool | `false` | Guarantee the graph is connected |
| `acyclic` | bool | `false` | Guarantee no cycles (forest/tree/DAG) |
| `node_schema` | schema\|null | `null` | Schema for node labels; defaults to integers |
| `output_format` | string | `"adjacency_list"` | One of `adjacency_list`, `adjacency_matrix`, `edge_list` |
| `weight_min` | float | `1.0` | Minimum edge weight (when `weighted=true`) |
| `weight_max` | float | `10.0` | Maximum edge weight (when `weighted=true`) |

**Topology combinations:**

| `connected` | `acyclic` | Result |
|---|---|---|
| `true` | `true` | Spanning tree (exactly n−1 edges) |
| `true` | `false` | Connected graph with possible cycles |
| `false` | `true` | Forest (one or more trees) |
| `false` | `false` | Arbitrary random graph |

**Output formats:**

| Format | Unweighted | Weighted |
|---|---|---|
| `adjacency_list` | `{node: [neighbor, ...]}` | `{node: [(neighbor, weight), ...]}` |
| `adjacency_matrix` | `[[0, 1, ...], ...]` | `[[0.0, 1.5, ...], ...]` |
| `edge_list` | `[(u, v), ...]` | `[(u, v, weight), ...]` |

---

## Full example

```python
from input_gen import generate

# Primitive
generate({"type": "integer", "minimum": 1, "maximum": 50})
# 17

# Nested: array of (float, bool) tuples
generate({
    "type": "array",
    "items": {
        "type": "tuple",
        "prefixItems": [{"type": "number"}, {"type": "boolean"}],
    },
    "minItems": 2,
})
# [(0.5, True), (-1.2, False), (3.0, True)]

# Connected weighted tree with character node labels
generate({
    "type": "graph",
    "directed": False,
    "weighted": True,
    "min_nodes": 4,
    "max_nodes": 8,
    "connected": True,
    "acyclic": True,
    "node_schema": {"type": "string", "minLength": 1, "maxLength": 1},
    "output_format": "adjacency_list",
    "weight_min": 1.0,
    "weight_max": 20.0,
})
# {"a": [("b", 5.2), ("c", 11.0)], "b": [("a", 5.2)], ...}
```

---

## Development

```bash
uv sync           # install all dependencies
uv run pytest     # run tests
uv run mypy src/  # type check
uv run ruff check # lint
```
