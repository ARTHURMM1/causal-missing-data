from causalgraphicalmodels import CausalGraphicalModel

# MNAR PROXY: Missingness depends on U, que é uma variável não observada. 
# Condicionar C não é suficiente para W e RW serem independentes.
# Assim, prever W é mais difícil, pois o missing depende de uma variável não observada.
# No caso do MNAR SELF, o missing dependia do proprio W, ou seja, do dado parcialmente observado.

mnar_proxy_graph = CausalGraphicalModel(
    nodes=[
        "C",
        "W",
        "X",
        "Y",
        "RW",
        "U"
    ],
    edges=[
        ("C", "W"),
        ("C", "X"),
        ("C", "Y"),

        ("W", "X"),
        ("W", "Y"),

        ("X", "Y"),

        ("U", "RW") #agora o missing depende de U, que é uma var não observada
    ]
)

# print(mnar_proxy_graph.is_d_separated("W", "RW", {"C"})) # False