import time

import osmnx as ox
import networkx as nx

from hazards.road_hazard_integration import (
    apply_flood_risk_to_route,
)


print("Loading Dubai road network...")

graph = ox.graph_from_place(
    "Dubai, United Arab Emirates",
    network_type="drive",
)

print("Road network loaded.")
print()


START = (25.2048, 55.2708)
DESTINATION = (25.1972, 55.2744)


start_node = ox.distance.nearest_nodes(
    graph,
    X=START[1],
    Y=START[0],
)

destination_node = ox.distance.nearest_nodes(
    graph,
    X=DESTINATION[1],
    Y=DESTINATION[0],
)


# -------------------------------------------------
# BASE ROAD COSTS
# -------------------------------------------------

for u, v, key, data in graph.edges(
    keys=True,
    data=True,
):

    length = data.get("length", 0)

    speed_kmh = 40

    travel_time = (
        (length / 1000)
        / speed_kmh
        * 60
    )

    data["q_cost"] = travel_time


# -------------------------------------------------
# INITIAL ROUTE
# -------------------------------------------------

start_time = time.perf_counter()

initial_route = nx.shortest_path(
    graph,
    start_node,
    destination_node,
    weight="q_cost",
)

initial_time = (
    time.perf_counter() - start_time
)

initial_cost = nx.shortest_path_length(
    graph,
    start_node,
    destination_node,
    weight="q_cost",
)


print("# INITIAL ROUTE")
print("================")
print(
    "Route nodes:",
    len(initial_route),
)

print(
    "Initial cost:",
    round(initial_cost, 3),
)

print(
    "Calculation time:",
    round(initial_time, 6),
    "seconds",
)


# -------------------------------------------------
# VARIABLE FLOOD CONDITIONS
# -------------------------------------------------

route_segments = len(initial_route) - 1

flood_risks = []

for index in range(route_segments):

    # Most roads remain relatively safe.
    risk = 0.10

    # Create several localized flooded areas.
    if 10 <= index <= 15:
        risk = 0.75

    elif 28 <= index <= 32:
        risk = 0.60

    elif index == 40:
        risk = 0.90

    flood_risks.append(risk)


print()
print("# VARIABLE FLOOD CONDITIONS")
print("============================")

print(
    "Total route segments:",
    route_segments,
)

print(
    "High-risk segments:",
    sum(
        risk >= 0.75
        for risk in flood_risks
    ),
)


# -------------------------------------------------
# APPLY ROAD-SPECIFIC FLOOD RISK
# -------------------------------------------------

affected = apply_flood_risk_to_route(
    graph,
    initial_route,
    flood_risks,
)


print(
    "Segments with flood data:",
    affected,
)


# -------------------------------------------------
# REROUTE
# -------------------------------------------------

start_time = time.perf_counter()

new_route = nx.shortest_path(
    graph,
    start_node,
    destination_node,
    weight="q_cost",
)

reroute_time = (
    time.perf_counter() - start_time
)

new_cost = nx.shortest_path_length(
    graph,
    start_node,
    destination_node,
    weight="q_cost",
)


# -------------------------------------------------
# RESULTS
# -------------------------------------------------

print()
print("# VARIABLE FLOOD Q-ROUTING")
print("===========================")

print(
    "New route nodes:",
    len(new_route),
)

print(
    "New route cost:",
    round(new_cost, 3),
)

print(
    "Rerouting time:",
    round(reroute_time, 6),
    "seconds",
)

print(
    "Route changed:",
    initial_route != new_route,
)