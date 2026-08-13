from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class Road:
    """
    Represents a road connecting two locations in the routing graph.
    """
    destination: str
    travel_time: float
    distance: float
    traffic_factor: float = 1.0
    hazard_factor: float = 0.0
    predicted_delay: float = 0.0
    closed: bool = False

    def dynamic_cost(self) -> float:
        """
        Calculates the current cost of travelling through this road.

        Lower cost = better road.

        This is the first version of the Q-Routing cost function.
        We will refine the mathematical model later using real data.
        """

        if self.closed:
            return math.inf

        traffic_penalty = self.travel_time * max(0.0, self.traffic_factor - 1.0)

        hazard_penalty = self.travel_time * self.hazard_factor

        return (
            self.travel_time
            + traffic_penalty
            + hazard_penalty
            + self.predicted_delay
        )


@dataclass
class RoutingGraph:
    """
    Dynamic graph representing the road network.
    """

    roads: Dict[str, List[Road]] = field(default_factory=dict)

    def add_road(
        self,
        origin: str,
        destination: str,
        travel_time: float,
        distance: float,
        traffic_factor: float = 1.0,
        hazard_factor: float = 0.0,
        predicted_delay: float = 0.0,
        closed: bool = False,
    ) -> None:

        road = Road(
            destination=destination,
            travel_time=travel_time,
            distance=distance,
            traffic_factor=traffic_factor,
            hazard_factor=hazard_factor,
            predicted_delay=predicted_delay,
            closed=closed,
        )

        self.roads.setdefault(origin, []).append(road)


class QRoutingEngine:
    """
    Initial Q-Routing engine.

    This version provides the foundation for:
    - Dynamic road costs
    - Hazard penalties
    - Predicted delays
    - Road closures

    More advanced Q-learning will be added after the
    dynamic routing foundation is tested.
    """

    def __init__(self, graph: RoutingGraph):
        self.graph = graph

    def shortest_dynamic_route(
        self,
        start: str,
        destination: str,
    ) -> Optional[dict]:

        distances = {node: math.inf for node in self.graph.roads}
        distances[start] = 0.0

        previous = {}
        visited = set()

        # Include destination even if it has no outgoing roads.
        distances.setdefault(destination, math.inf)

        while True:
            current = None
            current_distance = math.inf

            for node, distance in distances.items():
                if node not in visited and distance < current_distance:
                    current = node
                    current_distance = distance

            if current is None:
                break

            if current == destination:
                break

            visited.add(current)

            for road in self.graph.roads.get(current, []):

                if road.closed:
                    continue

                cost = road.dynamic_cost()
                new_distance = current_distance + cost

                if new_distance < distances.get(
                    road.destination,
                    math.inf
                ):
                    distances[road.destination] = new_distance
                    previous[road.destination] = (
                        current,
                        road
                    )

        if distances.get(destination, math.inf) == math.inf:
            return None

        path = []
        current = destination

        while current != start:
            if current not in previous:
                return None

            previous_node, road = previous[current]

            path.append({
                "from": previous_node,
                "to": current,
                "travel_time": road.travel_time,
                "distance": road.distance,
                "dynamic_cost": road.dynamic_cost(),
            })

            current = previous_node

        path.reverse()

        return {
            "start": start,
            "destination": destination,
            "total_cost": round(distances[destination], 3),
            "route": path,
        }