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


HAZARD_LAT = 25.2048
HAZARD_LON = 55.2708


result = hazards.apply_hazard(
    latitude=HAZARD_LAT,
    longitude=HAZARD_LON,
    penalty=0.0,
    hazard_type="emergency_closure",
    closed=True,
)


u, v, key = result["edge"]

edge = graph[u][v][key]


print("# ROAD CLOSURE TEST")
print("===================")

print("Affected edge:")
print(result["edge"])

print()

print("Hazard:")
print(result["hazard_type"])

print()

print("Road closed:")
print(result["closed"])

print()

print("Q-cost:")
print(edge["q_cost"])

print()

print("Stored hazard:")
print(edge["hazards"])