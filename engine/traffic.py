import hashlib


class TrafficEngine:
    """
    Dynamic traffic engine.

    Traffic can vary between road segments so
    Q-Routing can avoid congested roads.
    """

    LEVELS = {
        "free": 0.0,
        "light": 0.10,
        "moderate": 0.30,
        "heavy": 0.60,
        "severe": 1.00,
        "closed": float("inf"),
    }

    def calculate_penalty(
        self,
        base_travel_time: float,
        traffic_level: str,
    ):

        level = traffic_level.lower().strip()

        if level not in self.LEVELS:
            raise ValueError(
                f"Unknown traffic level: {traffic_level}"
            )

        multiplier = self.LEVELS[level]

        if multiplier == float("inf"):
            return float("inf")

        return base_travel_time * multiplier

    def adjusted_travel_time(
        self,
        base_travel_time: float,
        traffic_level: str,
    ):

        penalty = self.calculate_penalty(
            base_travel_time,
            traffic_level,
        )

        if penalty == float("inf"):
            return float("inf")

        return base_travel_time + penalty

    def segment_factor(
        self,
        u,
        v,
        traffic_level,
    ):
        """
        Creates deterministic variation between
        different road segments.

        The same road always receives the same
        factor during a test.
        """

        level = traffic_level.lower().strip()

        if level == "free":
            return 0.0

        if level == "closed":
            return float("inf")

        base = self.LEVELS[level]

        key = f"{min(u,v)}:{max(u,v)}"

        digest = hashlib.md5(
            key.encode()
        ).hexdigest()

        value = int(
            digest[:8],
            16,
        )

        variation = (
            value % 100
        ) / 100.0

        factor = base * (
            0.5 + variation
        )

        return factor

    def segment_penalty(
        self,
        base_travel_time,
        u,
        v,
        traffic_level,
    ):

        factor = self.segment_factor(
            u,
            v,
            traffic_level,
        )

        if factor == float("inf"):
            return float("inf")

        return (
            base_travel_time
            * factor
        )