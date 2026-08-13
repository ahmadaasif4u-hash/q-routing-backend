import osmnx as ox

print("Downloading real road network...")

graph = ox.graph_from_place(
    "Dubai, United Arab Emirates",
    network_type="drive"
)

print()
print("REAL ROAD NETWORK LOADED")
print("=========================")
print("Number of road intersections:", len(graph.nodes))
print("Number of road connections:", len(graph.edges))