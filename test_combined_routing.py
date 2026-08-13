import networkx as nx

from engine.q_router import QRouter
from engine.edge_updater import EdgeUpdater


# -------------------------------------------------
# TEST ROAD NETWORK
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
    "D",
    travel_time=7.0,
    q_cost=7.0,
)

graph.add_edge(
    "D",
    "C",
    travel_time=7.0,
    q_cost=7.0,
)

graph.add_edge(
    "A",
    "C",
    travel_time=18.0,
    q_cost=18.0,
)


router = QRouter(graph)
updater = EdgeUpdater(graph)


# -------------------------------------------------
# NORMAL ROUTE
# -------------------------------------------------

normal = router.calculate_route(
    "A",
    "C",
)

print("# COMBINED Q-ROUTING TEST")
print("==========================")

print()
print("NORMAL CONDITIONS")
print("Route:", normal["route"])
print("Cost:", normal["total_cost"])


# -------------------------------------------------
# APPLY DIFFERENT CONDITIONS
# -------------------------------------------------

# A → B:
# heavy traffic + moderate flood
updater.update_edge(
    "A",
    "B",
    traffic_level="heavy",
    flood_penalty=3.0,
)


# B → C:
# severe traffic + major accident
updater.update_edge(
    "B",
    "C",
    traffic_level="severe",
    incident_type="major_accident",
)


# A → D:
# light traffic + small flood
updater.update_edge(
    "A",
    "D",
    traffic_level="light",
    flood_penalty=1.0,
)


# D → C:
# free traffic + no hazards
updater.update_edge(
    "D",
    "C",
    traffic_level="free",
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
print("AFTER COMBINED CONDITIONS")
print("==========================")

print(
    "Route:",
    rerouted["route"],
)

print(
    "Cost:",
    round(
        rerouted["total_cost"],
        3,
    ),
)

print(
    "Route changed:",
    rerouted["route_changed"],
)