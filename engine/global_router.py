import osmnx as ox

from engine.q_router import QRouter


def route_global(
    start_lat,
    start_lon,
    destination_lat,
    destination_lon,
    graph_manager,
):
    graph = graph_manager.get_graph(
        destination_lat,
        destination_lon,
    )

    for u, v, key, data in graph.edges(
        keys=True,
        data=True,
    ):
        length = float(
            data.get("length", 1.0)
        )

        data["travel_time"] = length
        data["q_cost"] = length

    start_node = ox.distance.nearest_nodes(
        graph,
        X=start_lon,
        Y=start_lat,
    )

    destination_node = ox.distance.nearest_nodes(
        graph,
        X=destination_lon,
        Y=destination_lat,
    )

    router = QRouter(graph)

    result = router.calculate_route(
        start_node,
        destination_node,
    )

    route_coordinates = []

    for node in result["route"]:
        node_data = graph.nodes[node]

        route_coordinates.append(
            {
                "latitude": float(
                    node_data["y"]
                ),
                "longitude": float(
                    node_data["x"]
                ),
            }
        )

    return {
        "status": "success",
        "route": [
            int(node)
            for node in result["route"]
        ],
        "route_coordinates": route_coordinates,
        "route_nodes": len(
            result["route"]
        ),
        "route_cost": float(
            result["total_cost"]
        ),
    }