"""Demo of generating random values from schemas."""

from input_gen import generate

# --- Primitives ---
print("=== Primitives ===")
print("integer:", generate({"type": "integer", "minimum": 1, "maximum": 100}))
print("float:  ", generate({"type": "number", "minimum": 0.0, "maximum": 1.0}))
print("boolean:", generate({"type": "boolean"}))
print(
    "string: ",
    generate(
        {"type": "string", "pattern": "^[a-z]+$", "minLength": 5, "maxLength": 10}
    ),
)

# --- Containers ---
print("\n=== Containers ===")
print(
    "array:",
    generate(
        {"type": "array", "items": {"type": "integer"}, "minItems": 3, "maxItems": 5}
    ),
)
print(
    "set:  ",
    generate(
        {
            "type": "set",
            "items": {
                "type": "string",
                "pattern": "^[a-z]+$",
                "minLength": 5,
                "maxLength": 10,
            },
            "minItems": 2,
            "maxItems": 4,
        }
    ),
)
print(
    "tuple:",
    generate(
        {
            "type": "tuple",
            "prefixItems": [
                {"type": "integer"},
                {
                    "type": "string",
                    "pattern": "^[a-z]+$",
                    "minLength": 5,
                    "maxLength": 10,
                },
                {"type": "boolean"},
            ],
        }
    ),
)
print(
    "object:",
    generate(
        {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[a-z]+$",
                    "minLength": 5,
                    "maxLength": 10,
                },
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
                "active": {"type": "boolean"},
            },
        }
    ),
)

# --- Graphs ---
print("\n=== Graphs ===")

print("undirected unweighted (adjacency_list):")
print(
    generate(
        {
            "type": "graph",
            "directed": False,
            "weighted": False,
            "min_nodes": 4,
            "max_nodes": 6,
            "connected": True,
            "acyclic": False,
            "output_format": "adjacency_list",
        }
    )
)

print("\ndirected weighted (edge_list):")
print(
    generate(
        {
            "type": "graph",
            "directed": True,
            "weighted": True,
            "min_nodes": 3,
            "max_nodes": 5,
            "connected": True,
            "acyclic": False,
            "output_format": "edge_list",
            "weight_min": 1.0,
            "weight_max": 20.0,
        }
    )
)

print("\ntree / connected acyclic (adjacency_matrix):")
print(
    generate(
        {
            "type": "graph",
            "directed": False,
            "weighted": False,
            "min_nodes": 4,
            "max_nodes": 6,
            "connected": True,
            "acyclic": True,
            "output_format": "adjacency_matrix",
        }
    )
)

print("\nDAG / directed acyclic (adjacency_list):")
print(
    generate(
        {
            "type": "graph",
            "directed": True,
            "weighted": False,
            "min_nodes": 4,
            "max_nodes": 6,
            "connected": True,
            "acyclic": True,
            "output_format": "adjacency_list",
        }
    )
)
