import time
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
# INITIAL ROAD COSTS
# -------------------------------------------------

normal_conditions = RoadConditions()

for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    length = data.get("length", 0)

    speed_kmh = 40

    travel_time = (
        length / 1000
    ) / speed_kmh * 60

    data["q_cost"] = calculate_dynamic_cost(
        travel_time,
        normal_conditions
    )


# -------------------------------------------------
# INITIAL ROUTE
# -------------------------------------------------

start_time = time.perf_counter()

initial_route = nx.shortest_path(
    graph,
    start_node,
    destination_node,
    weight="q_cost"
)

initial_calculation_time = (
    time.perf_counter() - start_time
)


initial_cost = nx.shortest_path_length(
    graph,
    start_node,
    destination_node,
    weight="q_cost"
)


print("# INITIAL ROUTE")
print("================")
print("Route nodes:", len(initial_route))
print(
    "Initial cost:",
    round(initial_cost, 3)
)
print(
    "Calculation time:",
    round(initial_calculation_time, 6),
    "seconds"
)


# -------------------------------------------------
# DISRUPT ROADS ACTUALLY USED BY THE ROUTE
# -------------------------------------------------

print()
print("Simulating disruption on the current route...")


affected_edges = []


for u, v in zip(
    initial_route[:-1],
    initial_route[1:]
):

    # Make the selected road extremely expensive.
    graph[u][v][0]["q_cost"] *= 100

    affected_edges.append((u, v))


print(
    "Affected route segments:",
    len(affected_edges)
)


# -------------------------------------------------
# REROUTE
# -------------------------------------------------

start_time = time.perf_counter()

new_route = nx.shortest_path(
    graph,
    start_node,
    destination_node,
    weight="q_cost"
)

reroute_time = (
    time.perf_counter() - start_time
)


new_cost = nx.shortest_path_length(
    graph,
    start_node,
    destination_node,
    weight="q_cost"
)


# -------------------------------------------------
# RESULTS
# -------------------------------------------------

print()
print("# REROUTING")
print("=============")
print("New route nodes:", len(new_route))
print(
    "New route cost:",
    round(new_cost, 3)
)

print(
    "Rerouting time:",
    round(reroute_time, 6),
    "seconds"
)

print()
print("# Q-ROUTING PERFORMANCE")
print("========================")
print(
    "Initial calculation:",
    round(initial_calculation_time, 6),
    "seconds"
)

print(
    "Rerouting:",
    round(reroute_time, 6),
    "seconds"
)

print(
    "Route changed:",
    initial_route != new_route
)