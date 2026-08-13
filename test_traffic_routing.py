import networkx as nx

from engine.q_router import QRouter
from engine.edge_updater import EdgeUpdater


graph = nx.DiGraph()

graph.add_edge(
    "A",
    "B",
    travel_time=5.0,
    q_cost=5.0,
)

graph.add_edge(
    "B",
    "C",
    travel_time=5.0,
    q_cost=5.0,
)

graph.add_edge(
    "A",
    "C",
    travel_time=15.0,
    q_cost=15.0,
)


router = QRouter(graph)
updater = EdgeUpdater(graph)


print("# TRAFFIC ROUTING TEST")
print("=======================")


normal = router.calculate_route(
    "A",
    "C",
)

print()
print("NORMAL CONDITIONS")
print(
    "Route:",
    normal["route"],
)

print(
    "Cost:",
    normal["total_cost"],
)


# Apply severe traffic to A -> B
updater.update_edge(
    "A",
    "B",
    traffic_level="severe",
)


# Apply severe traffic to B -> C
updater.update_edge(
    "B",
    "C",
    traffic_level="severe",
)


rerouted = router.reroute(
    "A",
    "C",
    previous_route=normal["route"],
)


print()
print("AFTER SEVERE TRAFFIC")
print(
    "Route:",
    rerouted["route"],
)

print(
    "Cost:",
    rerouted["total_cost"],
)

print(
    "Route changed:",
    rerouted["route_changed"],
)