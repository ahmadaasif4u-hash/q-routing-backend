class IncidentEngine:
    """
    Handles temporary incidents affecting roads.
    """

    INCIDENT_PENALTIES = {
        "none": 0.0,
        "minor_accident": 0.30,
        "major_accident": 0.70,
        "construction": 0.50,
        "obstruction": 0.60,
        "emergency_closure": float("inf"),
    }

    def get_penalty(
        self,
        base_travel_time: float,
        incident_type: str,
    ) -> float:
        """
        Convert an incident into a routing penalty.
        """

        incident = incident_type.lower().strip()

        if incident not in self.INCIDENT_PENALTIES:
            raise ValueError(
                f"Unknown incident type: {incident_type}"
            )

        multiplier = self.INCIDENT_PENALTIES[
            incident
        ]

        if multiplier == float("inf"):
            return float("inf")

        return base_travel_time * multiplier

    def is_closed(
        self,
        incident_type: str,
    ) -> bool:
        """
        Check whether an incident makes
        a road completely unavailable.
        """

        return (
            incident_type.lower().strip()
            == "emergency_closure"
        )