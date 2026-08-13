import osmnx as ox
import networkx as nx

from engine.route_safety import RouteSafetyAnalyzer


print("Loading Dubai road network...")

graph = ox.graph_from_place(
    "Dubai, United Arab Emirates",
    network_type="drive"
)

print("Road network loaded.")

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

route = nx.shortest_path(
    graph,
    start_node,
    destination_node,
    weight="length"
)

print()
print("# REAL ROUTE SAFETY TEST")
print("========================")

print("Route nodes:", len(route))

analyzer = RouteSafetyAnalyzer(graph)

alerts = analyzer.analyze_route(
    route,
    minimum_angle=60.0
)

print()
print("Sharp turns detected:", len(alerts))

for alert in alerts[:10]:
    print()
    print(alert)

if len(alerts) > 10:
    print()
    print("Additional sharp turns:", len(alerts) - 10)