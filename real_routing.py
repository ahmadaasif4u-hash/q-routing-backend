import osmnx as ox
import networkx as nx


print("Loading Dubai road network...")

graph = ox.graph_from_place(
    "Dubai, United Arab Emirates",
    network_type="drive"
)

print("Road network loaded.")
print()


# Choose two real locations in Dubai.
# These are only test coordinates for now.

START = (25.2048, 55.2708)
DESTINATION = (25.1972, 55.2744)


# Find the nearest road intersections.
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


print("Start road node:", start_node)
print("Destination road node:", destination_node)


# Calculate the fastest route using real road lengths.
route = nx.shortest_path(
    graph,
    start_node,
    destination_node,
    weight="length"
)


# Calculate total route distance.
route_distance = sum(
    graph.edges[u, v, 0].get("length", 0)
    for u, v in zip(route[:-1], route[1:])
)


print()
print("REAL Q-ROUTING ROAD TEST")
print("=========================")
print("Number of road nodes:", len(graph.nodes))
print("Number of route nodes:", len(route))
print("Route distance:", round(route_distance, 2), "meters")
print()
print("Route successfully calculated.")