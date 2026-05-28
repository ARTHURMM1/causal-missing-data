from mar_graph import mar_graph
from mnar_self_graph import mnar_self_graph

print("MAR")
print("\tW ⫫ RW :", mar_graph.is_d_separated("W", "RW", {}))
print("\tW ⫫ RW | C :", mar_graph.is_d_separated("W", "RW", {"C"}))

print("MNAR self")
print("\tW ⫫ RW | C :",mnar_self_graph.is_d_separated("W", "RW", {"C"}))