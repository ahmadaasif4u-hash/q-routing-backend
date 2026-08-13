import osmnx as ox

from engine.hazards import HazardEngine


print("Loading Dubai road network...")

graph = ox.graph_from_place(
    "Dubai, United Arab Emirates",
    network_type="drive",
)

print("Road network loaded.")
print()


hazards = HazardEngine(graph)


# Test hazard location in Dubai.
HAZARD_LAT = 25.2048
HAZARD_LON = 55.2708


result = hazards.apply_hazard(
    latitude=HAZARD_LAT,
    longitude=HAZARD_LON,
    penalty=1000.0,
    hazard_type="major_accident",
)


print("# LOCALIZED HAZARD TEST")
print("========================")

print("Hazard location:")
print(
    HAZARD_LAT,
    HAZARD_LON,
)

print()

print("Affected road edge:")
print(
    result["edge"]
)

print()

print("Road segment length:")
print(
    result["edge_length_m"],
    "meters",
)

print()

print("Hazard type:")
print(
    result["hazard_type"]
)

print()

print("Penalty:")
print(
    result["penalty"]
)

print()

u, v, key = result["edge"]

edge = graph[
    u
][
    v
][
    key
]

print("New q_cost:")
print(
    edge["q_cost"]
)

print()

print("Stored hazards:")
print(
    edge["hazards"]
)