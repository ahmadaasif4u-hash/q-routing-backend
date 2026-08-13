import osmnx as ox
import networkx as nx

from engine.q_router import QRouter


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


# Initialize dynamic route costs.
for u, v, key, data in graph.edges(
    keys=True,
    data=True,
):
    data["q_cost"] = float(
        data.get("length", 1.0)
    )


router = QRouter(graph)


# -------------------------------------------------
# NORMAL ROUTE
# -------------------------------------------------

normal_result = router.calculate_route(
    start_node,
    destination_node,
)

normal_route = normal_result["route"]


print("# NORMAL ROUTE")
print("==============")

print(
    "Route nodes:",
    len(normal_route),
)

print(
    "Route cost:",
    round(
        normal_result["total_cost"],
        2,
    ),
)

print()


# -------------------------------------------------
# FIND A ROUTE EDGE WITH AN ALTERNATIVE
# -------------------------------------------------

selected_edge = None


for i in range(
    len(normal_route) - 1
):

    u = normal_route[i]
    v = normal_route[i + 1]

    test_graph = graph.copy()

    if test_graph.has_edge(u, v):

        keys = list(
            test_graph[u][v].keys()
        )

        for key in keys:

            test_graph.remove_edge(
                u,
                v,
                key=key,
            )

    try:

        alternative_exists = nx.has_path(
            test_graph,
            start_node,
            destination_node,
        )

    except nx.NetworkXError:

        alternative_exists = False


    if alternative_exists:

        selected_edge = (
            u,
            v,
        )

        break


if selected_edge is None:

    print(
        "No suitable road segment with "
        "an alternative route was found."
    )

    raise SystemExit


hazard_u, hazard_v = selected_edge


print("# SELECTED CLOSURE")
print("==================")

print(
    "Closed edge:",
    [
        hazard_u,
        hazard_v,
    ],
)

print()


# -------------------------------------------------
# CLOSE THE REAL ROAD SEGMENT
# -------------------------------------------------

if graph.has_edge(
    hazard_u,
    hazard_v,
):

    keys = list(
        graph[
            hazard_u
        ][
            hazard_v
        ].keys()
    )

    for key in keys:

        graph.remove_edge(
            hazard_u,
            hazard_v,
            key=key,
        )


print("# AFTER CLOSURE")
print("===============")


# -------------------------------------------------
# REROUTE
# -------------------------------------------------

reroute_result = router.calculate_route(
    start_node,
    destination_node,
)

new_route = reroute_result["route"]


print(
    "New route nodes:",
    len(new_route),
)

print(
    "New route cost:",
    round(
        reroute_result["total_cost"],
        2,
    ),
)

print(
    "Route changed:",
    normal_route != new_route,
)


closed_edge_present = any(
    u == hazard_u
    and v == hazard_v
    for u, v in zip(
        new_route[:-1],
        new_route[1:],
    )
)


print(
    "Closed edge still present:",
    closed_edge_present,
)