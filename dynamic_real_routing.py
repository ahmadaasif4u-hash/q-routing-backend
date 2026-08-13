import osmnx as ox
import networkx as nx

from routing.dynamic_weights import (
    RoadConditions,
    calculate_dynamic_cost,
)


print("Loading Dubai road network...")

graph = ox.graph_from_place(
    "Dubai, United Arab Emirates",
    network_type="drive"
)

print("Road network loaded.")
print()


START = (25.2048, 55.2708)
DESTINATION = (25.1972, 55.2744)


start_node = ox.distance.nearest_nodes(
    graph,
    X=START[1],
    Y=START[0]
)

destination_node = ox.distance.nearest_nodes(
    graph,
    X=DESTINATION[1],
    Y=DESTINATION[0]
)


# -------------------------------------------------
# Prototype dynamic road conditions
# -------------------------------------------------

conditions = RoadConditions(
    traffic_multiplier=1.0,
    predicted_delay_minutes=0.0,
    hazard_risk=0.0,
)


# -------------------------------------------------
# Convert real road lengths into travel-time costs
# -------------------------------------------------

for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    length = data.get("length", 0)

    # Prototype average speed.
    # This is NOT real traffic data yet.
    speed_kmh = 40

    travel_time_minutes = (
        length / 1000
    ) / speed_kmh * 60

    cost = calculate_dynamic_cost(
        travel_time_minutes,
        conditions
    )

    data["q_cost"] = cost


# -------------------------------------------------
# Calculate dynamic route
# -------------------------------------------------

route = nx.shortest_path(
    graph,
    start_node,
    destination_node,
    weight="q_cost"
)


total_cost = nx.shortest_path_length(
    graph,
    start_node,
    destination_node,
    weight="q_cost"
)


print("# DYNAMIC REAL-ROAD ROUTING")
print("============================")
print("Start node:", start_node)
print("Destination node:", destination_node)
print("Route nodes:", len(route))
print("Dynamic route cost:", round(total_cost, 3))
print()
print("Dynamic route successfully calculated.")