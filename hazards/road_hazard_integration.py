from hazards.flood_risk import flood_penalty


def apply_flood_risk_to_edge(
    edge_data: dict,
    flood_risk: float,
) -> float:

    base_cost = edge_data.get(
        "q_cost",
        edge_data.get("length", 1.0),
    )

    new_cost = flood_penalty(
        base_cost,
        flood_risk,
    )

    edge_data["flood_risk"] = flood_risk
    edge_data["q_cost"] = new_cost

    return new_cost


def apply_flood_risk_to_route(
    graph,
    route,
    flood_risks,
) -> int:

    affected = 0

    for index, (u, v) in enumerate(
        zip(route[:-1], route[1:])
    ):

        edge = graph[u][v][0]

        # Use the corresponding risk for this
        # individual road segment.
        risk = flood_risks[index]

        apply_flood_risk_to_edge(
            edge,
            risk,
        )

        affected += 1

    return affected