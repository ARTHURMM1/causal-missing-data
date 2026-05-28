from causalgraphicalmodels import CausalGraphicalModel

# MNAR SELF: Missingness depends on W itself, ou seja, o dado parcialmente observado influencia 
# o proprio missing. Condicionar C não é suficiente para W e RW serem independentes

mnar_self_graph = CausalGraphicalModel(
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

        ("C", "RW"),

        ("W", "RW") #agora o dado parcialmente observado W influencia o proprio missing --> MNAR. Condicionar C não é suficiente para W e RW serem independentes
    ]
)

# print(mnar_self_graph.is_d_separated("W", "RW", {"C"})) # False