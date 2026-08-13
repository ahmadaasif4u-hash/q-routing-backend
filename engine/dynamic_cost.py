class DynamicCostEngine:
    """
    Calculates the dynamic cost of a road segment.

    The final cost combines:
    - travel time
    - traffic
    - weather
    - flooding
    - incidents
    - emergency vehicle priority
    """

    def __init__(self):

        self.weights = {
            "travel_time": 1.0,
            "traffic": 1.0,
            "weather": 1.0,
            "flood": 1.0,
            "incident": 1.0,
        }

    def calculate(
        self,
        travel_time: float,
        traffic_penalty: float = 0.0,
        weather_penalty: float = 0.0,
        flood_penalty: float = 0.0,
        incident_penalty: float = 0.0,
        emergency_mode: bool = False,
    ) -> float:
        """
        Calculate the total dynamic road cost.
        """

        cost = (
            travel_time
            * self.weights["travel_time"]
        )

        cost += (
            traffic_penalty
            * self.weights["traffic"]
        )

        cost += (
            weather_penalty
            * self.weights["weather"]
        )

        cost += (
            flood_penalty
            * self.weights["flood"]
        )

        cost += (
            incident_penalty
            * self.weights["incident"]
        )

        # Emergency vehicles prioritize travel time.
        if emergency_mode:

            cost *= 0.8

            cost += (
                traffic_penalty
                + weather_penalty
                + flood_penalty
                + incident_penalty
            ) * 0.2

        return cost