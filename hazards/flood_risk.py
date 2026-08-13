def calculate_flood_risk(
    rainfall_mm: float,
    elevation_m: float,
    drainage_factor: float,
    water_proximity_factor: float,
) -> float:
    """
    Estimate active flood risk.

    Flood susceptibility alone does not create an
    active flood warning. A rainfall trigger is required.
    """

    # No meaningful rainfall trigger.
    if rainfall_mm <= 0:
        return 0.0

    # Rainfall contribution.
    rainfall_score = min(
        rainfall_mm / 50.0,
        1.0
    )

    # Lower elevation increases susceptibility.
    elevation_score = max(
        0.0,
        min(
            1.0 - (elevation_m / 100.0),
            1.0
        )
    )

    # Poor drainage increases susceptibility.
    drainage_score = max(
        0.0,
        min(
            drainage_factor,
            1.0
        )
    )

    # Proximity to water increases susceptibility.
    water_score = max(
        0.0,
        min(
            water_proximity_factor,
            1.0
        )
    )

    risk = (
        0.40 * rainfall_score
        + 0.20 * elevation_score
        + 0.20 * drainage_score
        + 0.20 * water_score
    )

    return max(
        0.0,
        min(risk, 1.0)
    )


def flood_penalty(
    base_cost: float,
    flood_risk: float,
) -> float:
    """
    Convert active flood risk into routing cost.
    """

    if flood_risk >= 0.90:
        return float("inf")

    if flood_risk <= 0:
        return base_cost

    penalty_multiplier = (
        1.0 + 4.0 * flood_risk
    )

    return base_cost * penalty_multiplier