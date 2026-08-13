from typing import List

from hazards.hazard_engine import HazardResult


def calculate_hazard_penalty(
    hazards: List[HazardResult]
) -> float:
    """
    Convert detected hazards into a routing penalty.

    The penalty is intentionally separate from the
    hazard engine. This allows the routing system to
    decide how strongly each hazard should influence
    route selection.
    """

    penalty = 0.0

    for hazard in hazards:

        if hazard.hazard == "heavy_rain":
            penalty += 20 * hazard.risk_score

        elif hazard.hazard == "strong_wind":
            penalty += 12 * hazard.risk_score

        elif hazard.hazard == "low_visibility":
            penalty += 15 * hazard.risk_score

    return penalty


def apply_hazard_penalty(
    base_cost: float,
    hazards: List[HazardResult]
) -> float:
    """
    Add hazard-related cost to a road.
    """

    penalty = calculate_hazard_penalty(hazards)

    return base_cost + penalty