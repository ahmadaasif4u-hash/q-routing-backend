from routing.q_routing import RoutingGraph, QRoutingEngine
from prediction.hazards import (
    Hazard,
    HazardType,
    HazardStatus,
)


graph = RoutingGraph()

# Route A → B → C
graph.add_road(
    "A",
    "B",
    travel_time=5,
    distance=4
)

graph.add_road(
    "B",
    "C",
    travel_time=5,
    distance=4
)

# Alternative route
graph.add_road(
    "A",
    "C",
    travel_time=15,
    distance=12
)


# Simulate a predicted flood on B → C.
#
# This is NOT real weather data.
# It is only a test of the routing system.

flood = Hazard(
    hazard_type=HazardType.FLOODING,
    status=HazardStatus.PREDICTED,
    confidence=0.9,
    predicted_delay=20,
    severity=0.9,
    description="Predicted flooding may significantly delay traffic."
)

# Apply the predicted delay to B → C.
graph.roads["B"][0].predicted_delay = flood.routing_penalty()


engine = QRoutingEngine(graph)

result = engine.shortest_dynamic_route("A", "C")


print("# PREDICTED HAZARD TEST")
print()
print("Hazard:", flood.hazard_type.value)
print("Status:", flood.status.value)
print("Confidence:", flood.confidence)
print("Predicted delay:", flood.predicted_delay)
print("Routing penalty:", flood.routing_penalty())
print()

if result:
    print("Selected route:", result["route"])
    print("Total cost:", result["total_cost"])
else:
    print("No route found.")