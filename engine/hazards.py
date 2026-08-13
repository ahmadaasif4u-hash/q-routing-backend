import math
import osmnx as ox


class HazardEngine:

    def __init__(self, graph):
        self.graph = graph

    def _distance_m(self, lat1, lon1, lat2, lon2):
        r = 6371000.0

        p1 = math.radians(lat1)
        p2 = math.radians(lat2)

        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)

        a = (
            math.sin(dp / 2) ** 2
            + math.cos(p1)
            * math.cos(p2)
            * math.sin(dl / 2) ** 2
        )

        return (
            2
            * r
            * math.atan2(
                math.sqrt(a),
                math.sqrt(1 - a),
            )
        )

    def nearest_edge(
        self,
        latitude,
        longitude,
    ):

        u, v, key = ox.distance.nearest_edges(
            self.graph,
            X=longitude,
            Y=latitude,
        )

        edge = self.graph[u][v][key]

        return {
            "edge": (u, v, key),
            "edge_length_m": float(
                edge.get("length", 0.0)
            ),
        }

    def apply_hazard(
        self,
        latitude,
        longitude,
        penalty=0.0,
        hazard_type="unknown",
        closed=False,
        radius_m=250.0,
    ):

        affected_edges = []

        for u, v, key, edge in self.graph.edges(
            keys=True,
            data=True,
        ):

            midpoint_lat = (
                float(self.graph.nodes[u]["y"])
                + float(self.graph.nodes[v]["y"])
            ) / 2

            midpoint_lon = (
                float(self.graph.nodes[u]["x"])
                + float(self.graph.nodes[v]["x"])
            ) / 2

            distance = self._distance_m(
                latitude,
                longitude,
                midpoint_lat,
                midpoint_lon,
            )

            if distance > radius_m:
                continue

            if closed:
                edge["q_cost"] = float("inf")
            else:
                current_cost = float(
                    edge.get(
                        "q_cost",
                        edge.get("length", 1.0),
                    )
                )

                edge["q_cost"] = (
                    current_cost
                    + float(penalty)
                )

            edge.setdefault(
                "hazards",
                [],
            )

            edge["hazards"].append(
                {
                    "type": hazard_type,
                    "penalty": float(penalty),
                    "closed": bool(closed),
                    "distance_from_hazard_m": round(
                        distance,
                        2,
                    ),
                }
            )

            edge["road_closed"] = bool(closed)

            affected_edges.append(
                {
                    "u": int(u),
                    "v": int(v),
                    "key": int(key),
                    "distance_m": round(
                        distance,
                        2,
                    ),
                }
            )

        nearest = self.nearest_edge(
            latitude,
            longitude,
        )

        return {
            "edge": [
                int(nearest["edge"][0]),
                int(nearest["edge"][1]),
                int(nearest["edge"][2]),
            ],
            "edge_length_m": (
                nearest["edge_length_m"]
            ),
            "hazard_type": hazard_type,
            "penalty": float(penalty),
            "closed": bool(closed),
            "radius_m": float(radius_m),
            "affected_edges": affected_edges,
            "affected_edge_count": len(
                affected_edges
            ),
        }