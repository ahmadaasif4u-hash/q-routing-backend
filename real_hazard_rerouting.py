import time

import osmnx as ox
import networkx as nx

from weather.weather_data import WeatherData
from hazards.hazard_engine import analyze_weather
from hazards.road_risk import apply_hazard_penalty


print("Loading Dubai road network...")

graph = ox.graph_from_place(
    "Dubai, United Arab Emirates",
    network_type="drive"
)

print("Road network loaded.")
print()


# -------------------------------------------------
# TEST LOCATION
# -------------------------------------------------

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
# NORMAL ROAD COSTS
# -------------------------------------------------

for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    length = data.get("length", 0)

    speed_kmh = 40

    travel_time = (
        length / 1000
    ) / speed_kmh * 60

    data["q_cost"] = travel_time


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

initial_time = (
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
    "Route cost:",
    round(initial_cost, 3)
)

print(
    "Calculation time:",
    round(initial_time, 6),
    "seconds"
)


# -------------------------------------------------
# SIMULATED SEVERE WEATHER
# -------------------------------------------------

severe_weather = WeatherData(
    temperature_c=42,
    precipitation_probability=95,
    precipitation_mm=25,
    wind_speed_kmh=70,
    visibility_km=1,
)


hazards = analyze_weather(
    severe_weather
)


print()
print("# DETECTED HAZARDS")
print("===================")

for hazard in hazards:

    print(
        hazard.hazard,
        "| risk:",
        round(hazard.risk_score, 3),
        "| severity:",
        hazard.severity
    )


# -------------------------------------------------
# APPLY HAZARDS TO THE ACTUAL ROUTE
# -------------------------------------------------

print()
print("Applying hazards to current route...")


affected_edges = []


for u, v in zip(
    initial_route[:-1],
    initial_route[1:]
):

    edge_data = graph[u][v][0]

    base_cost = edge_data["q_cost"]

    edge_data["q_cost"] = apply_hazard_penalty(
        base_cost,
        hazards
    )

    affected_edges.append((u, v))


print(
    "Affected road segments:",
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
print("# Q-ROUTING HAZARD REROUTING")
print("============================")

print(
    "New route nodes:",
    len(new_route)
)

print(
    "New route cost:",
    round(new_cost, 3)
)

print(
    "Rerouting time:",
    round(reroute_time, 6),
    "seconds"
)

print(
    "Route changed:",
    initial_route != new_route
)