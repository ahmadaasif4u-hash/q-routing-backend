import math


class RouteSafetyAnalyzer:
    """
    Analyzes an OSMnx route for sharp turns
    and calculates their distance from the route start.
    """

    def __init__(self, graph):
        self.graph = graph

    def _angle(
        self,
        previous_node,
        current_node,
        next_node,
    ):

        previous = self.graph.nodes[previous_node]
        current = self.graph.nodes[current_node]
        next_point = self.graph.nodes[next_node]

        p1 = (
            previous["x"],
            previous["y"],
        )

        p2 = (
            current["x"],
            current["y"],
        )

        p3 = (
            next_point["x"],
            next_point["y"],
        )

        v1 = (
            p2[0] - p1[0],
            p2[1] - p1[1],
        )

        v2 = (
            p3[0] - p2[0],
            p3[1] - p2[1],
        )

        magnitude1 = math.hypot(
            v1[0],
            v1[1],
        )

        magnitude2 = math.hypot(
            v2[0],
            v2[1],
        )

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        dot = (
            v1[0] * v2[0]
            + v1[1] * v2[1]
        )

        cosine = dot / (
            magnitude1 * magnitude2
        )

        cosine = max(
            -1.0,
            min(1.0, cosine),
        )

        return math.degrees(
            math.acos(cosine)
        )

    def _edge_distance(
        self,
        u,
        v,
    ):
        """
        Get the distance of an OSMnx edge in meters.
        """

        edge_data = self.graph[u][v]

        if self.graph.is_multigraph():

            distances = [
                data.get("length", 0.0)
                for data in edge_data.values()
            ]

            if not distances:
                return 0.0

            return min(distances)

        return edge_data.get(
            "length",
            0.0,
        )

    def analyze_route(
        self,
        route,
        minimum_angle=60.0,
    ):

        alerts = []
        distance_from_start = 0.0

        for i in range(1, len(route) - 1):

            previous_node = route[i - 1]
            current_node = route[i]
            next_node = route[i + 1]

            distance_from_start += (
                self._edge_distance(
                    previous_node,
                    current_node,
                )
            )

            angle = self._angle(
                previous_node,
                current_node,
                next_node,
            )

            if angle < minimum_angle:
                continue

            alerts.append(
                {
                    "alert_type": "sharp_turn",
                    "severity": (
                        "high"
                        if angle >= 90
                        else "medium"
                    ),
                    "node": current_node,
                    "turn_angle": round(
                        angle,
                        2,
                    ),
                    "distance_from_start_m": float(
    round(
        distance_from_start,
        1,
    )
),
                    "message": (
                        "Sharp turn ahead in "
                        f"{round(distance_from_start)} m."
                    ),
                }
            )

        return alerts