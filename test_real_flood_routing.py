import time

import osmnx as ox
import networkx as nx

from hazards.flood_risk import calculate_flood_risk
from hazards.flood_risk import flood_penalty


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
# BASE ROAD COST
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
print("Route nodes:", len(initial_route))
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
# HAZARDOUS BUT PASSABLE FLOOD
# -------------------------------------------------

flood_risk = calculate_flood_risk(
    rainfall_mm=25,
    elevation_m=20,
    drainage_factor=0.5,
    water_proximity_factor=0.5,
)


print()
print("# FLOOD EVENT")
print("==============")
print(
    "Flood risk:",
    round(flood_risk, 3),
)


affected_segments = 0


for u, v in zip(
    initial_route[:-1],
    initial_route[1:],
):

    if graph.has_edge(u, v):

        edge = graph[u][v][0]

        edge["q_cost"] = flood_penalty(
            edge["q_cost"],
            flood_risk,
        )

        affected_segments += 1


print(
    "Affected route segments:",
    affected_segments,
)


# -------------------------------------------------
# REROUTE
# -------------------------------------------------

start_time = time.perf_counter()

try:

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

    print()
    print("# FLOOD Q-ROUTING")
    print("==================")

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

except nx.NetworkXNoPath:

    print()
    print(
        "NO SAFE ROUTE AVAILABLE"
    )