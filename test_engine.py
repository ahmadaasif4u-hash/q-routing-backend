import networkx as nx

from engine.q_router import QRouter
from engine.edge_updater import EdgeUpdater


# -------------------------------------------------
# CREATE TEST ROAD NETWORK
# -------------------------------------------------

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


# -------------------------------------------------
# CREATE ENGINES
# -------------------------------------------------

router = QRouter(graph)
updater = EdgeUpdater(graph)


# -------------------------------------------------
# NORMAL ROUTE
# -------------------------------------------------

normal = router.calculate_route(
    "A",
    "C",
)


print("# NORMAL ROUTE")
print("================")
print(
    "Route:",
    normal["route"],
)

print(
    "Cost:",
    normal["total_cost"],
)


# -------------------------------------------------
# APPLY TRAFFIC
# -------------------------------------------------

updater.update_edge(
    "A",
    "B",
    traffic_penalty=10.0,
)


updater.update_edge(
    "B",
    "C",
    traffic_penalty=10.0,
)


# -------------------------------------------------
# REROUTE
# -------------------------------------------------

rerouted = router.reroute(
    "A",
    "C",
    previous_route=normal["route"],
)


print()
print("# AFTER TRAFFIC")
print("================")
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