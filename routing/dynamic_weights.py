from dataclasses import dataclass


@dataclass
class RoadConditions:
    """
    Dynamic conditions affecting a road segment.

    All values are designed to be updated as new
    real-world information becomes available.
    """

    traffic_multiplier: float = 1.0

    predicted_delay_minutes: float = 0.0

    hazard_risk: float = 0.0

    road_closure: bool = False

    emergency_priority: bool = False


def calculate_dynamic_cost(
    base_travel_time: float,
    conditions: RoadConditions,
) -> float:
    """
    Calculate the dynamic routing cost of a road segment.

    Lower cost means the road is more attractive.

    This is the initial mathematical model.
    We will later calibrate the coefficients using
    real traffic, weather and hazard data.
    """

    if conditions.road_closure:
        return float("inf")

    traffic_cost = (
        base_travel_time
        * conditions.traffic_multiplier
    )

    prediction_cost = (
        conditions.predicted_delay_minutes
    )

    safety_cost = (
        base_travel_time
        * conditions.hazard_risk
    )

    emergency_factor = 1.0

    if conditions.emergency_priority:
        # Emergency vehicles prioritize speed strongly.
        emergency_factor = 0.75

    total_cost = (
        traffic_cost
        + prediction_cost
        + safety_cost
    )

    return total_cost * emergency_factor