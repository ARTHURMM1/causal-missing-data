from graphviz import Digraph

dot = Digraph()

# estrutura para o DAG do MAR
dot.node("C")
dot.node("W")
dot.node("Y")
dot.node("X")
dot.node("RW")

dot.edge("C", "W")
dot.edge("C", "RW")
dot.edge("W", "X")
dot.edge("X", "Y")
dot.edge("W", "Y")

# dot.node("U", style="dashed")

dot.render("mar_graph", format="png")
