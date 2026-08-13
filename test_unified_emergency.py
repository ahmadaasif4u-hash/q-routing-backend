import networkx as nx

from engine.edge_updater import EdgeUpdater
from engine.q_router import QRouter


graph = nx.DiGraph()

# FAST ROUTE
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

# ALTERNATIVE ROUTE
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


updater = EdgeUpdater(graph)
router = QRouter(graph)


print("# UNIFIED EMERGENCY Q-ROUTING TEST")
print("==================================")


# NORMAL CONDITIONS
for u, v in graph.edges():

    updater.update_edge(
        u,
        v,
        traffic_level="free",
        weather_penalty=0.0,
        flood_penalty=0.0,
        incident_type="none",
        emergency_mode=False,
        road_risk=0.0,
    )


normal = router.calculate_route(
    "A",
    "C",
)


print()
print("NORMAL CONDITIONS")
print("Route:", normal["route"])
print("Cost:", normal["total_cost"])


# SEVERE CONDITIONS ON FAST ROUTE
for u, v in [("A", "B"), ("B", "C")]:

    updater.update_edge(
        u,
        v,
        traffic_level="severe",
        weather_penalty=4.0,
        flood_penalty=6.0,
        incident_type="major_accident",
        emergency_mode=True,
        road_risk=0.8,
    )


# SAFE ALTERNATIVE
for u, v in [("A", "D"), ("D", "C")]:

    updater.update_edge(
        u,
        v,
        traffic_level="light",
        weather_penalty=0.0,
        flood_penalty=0.0,
        incident_type="none",
        emergency_mode=True,
        road_risk=0.1,
    )


emergency = router.calculate_route(
    "A",
    "C",
)


print()
print("EMERGENCY + SEVERE CONDITIONS")
print("Route:", emergency["route"])
print("Cost:", emergency["total_cost"])
print(
    "Route changed:",
    normal["route"] != emergency["route"],
)