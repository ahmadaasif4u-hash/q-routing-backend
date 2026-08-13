import networkx as nx


class QRouter:
    """
    Dynamic Q-Routing engine.

    Supports:
    - optimized Q-route
    - fastest route
    - safest route
    - rerouting
    """

    def __init__(self, graph=None):
        self.graph = graph

    def set_graph(self, graph):
        self.graph = graph

    def _check_graph(self):
        if self.graph is None:
            raise ValueError("No road graph selected.")

    def _shortest_path(
        self,
        start_node,
        destination_node,
        weight,
    ):

        self._check_graph()

        route = nx.shortest_path(
            self.graph,
            start_node,
            destination_node,
            weight=weight,
        )

        cost = nx.shortest_path_length(
            self.graph,
            start_node,
            destination_node,
            weight=weight,
        )

        return route, float(cost)

    def calculate_route(
        self,
        start_node,
        destination_node,
    ):

        route, total_cost = self._shortest_path(
            start_node,
            destination_node,
            "q_cost",
        )

        return {
            "route": route,
            "total_cost": total_cost,
        }

    def calculate_fastest_route(
        self,
        start_node,
        destination_node,
    ):

        route, total_cost = self._shortest_path(
            start_node,
            destination_node,
            "travel_time",
        )

        return {
            "route": route,
            "total_cost": total_cost,
        }

    def prepare_safety_costs(self):

        self._check_graph()

        for u, v, key, data in self.graph.edges(
            keys=True,
            data=True,
        ):

            travel_time = float(
                data.get(
                    "travel_time",
                    data.get("length", 1.0),
                )
            )

            risk = float(
                data.get(
                    "road_risk",
                    0.0,
                )
            )

            hazard_penalty = 0.0

            for hazard in data.get(
                "hazards",
                [],
            ):

                hazard_penalty += float(
                    hazard.get(
                        "penalty",
                        0.0,
                    )
                )

            if data.get(
                "road_closed",
                False,
            ):

                data["safety_cost"] = float(
                    "inf"
                )

            else:

                data["safety_cost"] = (
                    travel_time
                    + (risk * 10.0)
                    + hazard_penalty
                )

    def calculate_safest_route(
        self,
        start_node,
        destination_node,
    ):

        self.prepare_safety_costs()

        route, total_cost = self._shortest_path(
            start_node,
            destination_node,
            "safety_cost",
        )

        return {
            "route": route,
            "total_cost": total_cost,
        }

    def calculate_alternatives(
        self,
        start_node,
        destination_node,
    ):

        fastest = self.calculate_fastest_route(
            start_node,
            destination_node,
        )

        safest = self.calculate_safest_route(
            start_node,
            destination_node,
        )

        optimized = self.calculate_route(
            start_node,
            destination_node,
        )

        return {
            "fastest": fastest,
            "safest": safest,
            "optimized": optimized,
        }

    def calculate_route_cost(
        self,
        route,
    ):

        self._check_graph()

        total = 0.0

        for u, v in zip(
            route[:-1],
            route[1:],
        ):

            edge_data = self.graph[u][v]

            if self.graph.is_multigraph():
                edge = edge_data[0]
            else:
                edge = edge_data

            total += float(
                edge.get(
                    "q_cost",
                    0.0,
                )
            )

        return total

    def reroute(
        self,
        start_node,
        destination_node,
        previous_route=None,
    ):

        result = self.calculate_route(
            start_node,
            destination_node,
        )

        new_route = result["route"]

        result["route_changed"] = (
            previous_route is not None
            and previous_route != new_route
        )

        return result