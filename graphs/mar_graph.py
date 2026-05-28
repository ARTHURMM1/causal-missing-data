from causalgraphicalmodels import CausalGraphicalModel

mar_graph = CausalGraphicalModel(
    nodes=[
        "C",
        "W",
        "X",
        "Y",
        "RW"
    ],
    edges=[
        ("C", "W"),
        ("C", "X"),
        ("C", "Y"),

        ("W", "X"),
        ("W", "Y"),

        ("X", "Y"),

        ("C", "RW")
    ]
)

# print(mar_graph.is_d_separated("W", "RW", {"C"})) # True
# print(mar_graph.is_d_separated("W", "RW", set())) # False