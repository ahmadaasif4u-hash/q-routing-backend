from engine.dynamic_cost import DynamicCostEngine
from engine.traffic import TrafficEngine
from engine.incidents import IncidentEngine
from engine.emergency import EmergencyVehicleEngine


class EdgeUpdater:

    def __init__(self, graph):

        self.graph = graph

        self.cost_engine = DynamicCostEngine()
        self.traffic_engine = TrafficEngine()
        self.incident_engine = IncidentEngine()
        self.emergency_engine = EmergencyVehicleEngine()

    def _get_edge(self, u, v):

        edge_data = self.graph[u][v]

        if self.graph.is_multigraph():
            return edge_data[0]

        return edge_data

    def set_emergency_mode(
        self,
        enabled=True,
    ):

        self.emergency_engine.set_mode(
            enabled
        )

    def emergency_mode_enabled(self):

        return (
            self.emergency_engine
            .is_emergency_mode()
        )

    def update_edge(
        self,
        u,
        v,
        traffic_level="free",
        weather_penalty=0.0,
        flood_penalty=0.0,
        incident_type="none",
        emergency_mode=False,
        road_risk=0.0,
    ):

        self.set_emergency_mode(
            emergency_mode
        )

        edge = self._get_edge(u, v)

        travel_time = float(
            edge.get(
                "travel_time",
                edge.get(
                    "length",
                    1.0,
                ),
            )
        )

        traffic_cost = (
            self.traffic_engine
            .segment_penalty(
                travel_time,
                u,
                v,
                traffic_level,
            )
        )

        incident_cost = float(
            self.incident_engine.get_penalty(
                travel_time,
                incident_type,
            )
        )

        if (
            traffic_cost == float("inf")
            or incident_cost == float("inf")
        ):

            edge["q_cost"] = float("inf")

            edge["cost_breakdown"] = {
                "travel_time": travel_time,
                "traffic": traffic_cost,
                "weather": float(
                    weather_penalty
                ),
                "flood": float(
                    flood_penalty
                ),
                "incident": incident_cost,
                "emergency": 0.0,
                "total": float("inf"),
            }

            edge["traffic_level"] = (
                traffic_level
            )

            edge["incident_type"] = (
                incident_type
            )

            edge["emergency_mode"] = (
                emergency_mode
            )

            edge["road_risk"] = road_risk

            return float("inf")

        emergency_penalty = float(
            self.emergency_engine
            .calculate_priority_penalty(
                travel_time,
                road_risk,
            )
        )

        base_cost = float(
            self.cost_engine.calculate(
                travel_time=travel_time,
                traffic_penalty=traffic_cost,
                weather_penalty=weather_penalty,
                flood_penalty=flood_penalty,
                incident_penalty=incident_cost,
                emergency_mode=emergency_mode,
            )
        )

        total_cost = (
            base_cost
            + emergency_penalty
        )

        edge["q_cost"] = total_cost

        edge["travel_time_cost"] = (
            travel_time
        )

        edge["traffic_cost"] = (
            traffic_cost
        )

        edge["weather_cost"] = float(
            weather_penalty
        )

        edge["flood_cost"] = float(
            flood_penalty
        )

        edge["incident_cost"] = (
            incident_cost
        )

        edge["emergency_cost"] = (
            emergency_penalty
        )

        edge["road_risk"] = float(
            road_risk
        )

        edge["cost_breakdown"] = {
            "travel_time": travel_time,
            "traffic": traffic_cost,
            "weather": float(
                weather_penalty
            ),
            "flood": float(
                flood_penalty
            ),
            "incident": incident_cost,
            "emergency": emergency_penalty,
            "total": total_cost,
        }

        edge["traffic_level"] = (
            traffic_level
        )

        edge["incident_type"] = (
            incident_type
        )

        edge["emergency_mode"] = (
            emergency_mode
        )

        edge["emergency_penalty"] = (
            emergency_penalty
        )

        return total_cost