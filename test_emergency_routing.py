import networkx as nx

from engine.q_router import QRouter
from engine.emergency import EmergencyVehicleEngine


graph = nx.DiGraph()

# Route A:
# Faster but more dangerous
graph.add_edge(
    "A",
    "B",
    travel_time=6.0,
    q_cost=6.0,
    risk=0.9,
)

graph.add_edge(
    "B",
    "C",
    travel_time=6.0,
    q_cost=6.0,
    risk=0.9,
)

# Route B:
# Slightly slower but much safer
graph.add_edge(
    "A",
    "D",
    travel_time=8.0,
    q_cost=8.0,
    risk=0.1,
)

graph.add_edge(
    "D",
    "C",
    travel_time=8.0,
    q_cost=8.0,
    risk=0.1,
)


router = QRouter(graph)
emergency = EmergencyVehicleEngine()


print("# EMERGENCY ROUTING TEST")
print("========================")


normal = router.calculate_route(
    "A",
    "C",
)

print()
print("NORMAL MODE")
print("Route:", normal["route"])
print("Cost:", normal["total_cost"])


emergency.set_mode(True)


for u, v, data in graph.edges(
    data=True
):

    risk = data.get(
        "risk",
        0.0,
    )

    priority_penalty = (
        emergency.calculate_priority_penalty(
            data["travel_time"],
            risk,
        )
    )

    data["q_cost"] = (
        data["travel_time"]
        + priority_penalty
    )


emergency_route = router.calculate_route(
    "A",
    "C",
)

print()
print("EMERGENCY MODE")
print("Route:", emergency_route["route"])
print("Cost:", emergency_route["total_cost"])