import networkx as nx

from engine.edge_updater import EdgeUpdater


graph = nx.DiGraph()

graph.add_edge(
    "A",
    "B",
    travel_time=10.0,
    q_cost=10.0,
)

updater = EdgeUpdater(graph)


print("# EMERGENCY EDGE INTEGRATION TEST")
print("================================")


normal_cost = updater.update_edge(
    "A",
    "B",
    traffic_level="free",
    emergency_mode=False,
    road_risk=0.8,
)

print()
print("NORMAL MODE")
print("Emergency enabled:", updater.emergency_mode_enabled())
print("Edge cost:", normal_cost)


emergency_cost = updater.update_edge(
    "A",
    "B",
    traffic_level="free",
    emergency_mode=True,
    road_risk=0.8,
)

print()
print("EMERGENCY MODE")
print("Emergency enabled:", updater.emergency_mode_enabled())
print("Edge cost:", emergency_cost)
print(
    "Emergency penalty:",
    graph["A"]["B"]["emergency_penalty"],
)