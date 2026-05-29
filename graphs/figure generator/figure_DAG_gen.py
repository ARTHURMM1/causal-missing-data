from graphviz import Digraph

dot = Digraph()

# estrutura para o DAG do MAR
dot.node("C")
dot.node("W")
dot.node("Y")
dot.node("X")
dot.node("RW")
dot.node("U", style="dashed")

dot.edge("C", "W")
# dot.edge("C", "RW")
dot.edge("C", "X")
dot.edge("C", "Y")
dot.edge("W", "X")
dot.edge("X", "Y")
dot.edge("W", "Y")
dot.edge("U", "RW")
dot.edge("U", "W")

# dot.node("U", style="dashed")

dot.render("mnar_proxy_graph", format="png")


