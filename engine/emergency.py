class EmergencyVehicleEngine:
    """
    Adjusts routing priorities for emergency vehicles.
    """

    def __init__(self):
        self.enabled = False

    def set_mode(self, enabled=True):
        self.enabled = bool(enabled)

    def calculate_priority_penalty(
        self,
        base_travel_time: float,
        road_risk: float = 0.0,
    ) -> float:
        """
        Calculate the additional routing cost caused by
        road risk while emergency mode is active.
        """

        if not self.enabled:
            return 0.0

        risk = max(
            0.0,
            min(1.0, float(road_risk))
        )

        # Emergency vehicles strongly prioritize
        # reaching the destination quickly, while still
        # accounting for dangerous roads.
        return base_travel_time * risk * 0.50

    def is_emergency_mode(self):
        return self.enabled