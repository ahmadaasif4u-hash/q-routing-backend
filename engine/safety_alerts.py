import math


class SafetyAlertEngine:
    """
    Generates driver-facing safety alerts from
    road geometry and known risk conditions.
    """

    def calculate_turn_angle(
        self,
        previous_point,
        current_point,
        next_point,
    ):
        """
        Calculate the change in direction between
        three geographic points.

        Points are supplied as:
        (latitude, longitude)
        """

        lat1, lon1 = previous_point
        lat2, lon2 = current_point
        lat3, lon3 = next_point

        vector1 = (
            lon2 - lon1,
            lat2 - lat1,
        )

        vector2 = (
            lon3 - lon2,
            lat3 - lat2,
        )

        magnitude1 = math.hypot(
            vector1[0],
            vector1[1],
        )

        magnitude2 = math.hypot(
            vector2[0],
            vector2[1],
        )

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        dot_product = (
            vector1[0] * vector2[0]
            + vector1[1] * vector2[1]
        )

        cosine = (
            dot_product
            / (magnitude1 * magnitude2)
        )

        cosine = max(
            -1.0,
            min(1.0, cosine),
        )

        angle = math.degrees(
            math.acos(cosine)
        )

        return angle

    def sharp_turn_alert(
        self,
        turn_angle: float,
        distance_ahead: float,
    ):
        """
        Generate an alert when a turn is sharp.
        """

        angle = abs(turn_angle)

        if angle >= 90:
            severity = "high"

        elif angle >= 60:
            severity = "medium"

        else:
            return None

        return {
            "alert_type": "sharp_turn",
            "severity": severity,
            "turn_angle": round(
                angle,
                1,
            ),
            "distance_ahead": round(
                distance_ahead,
                1,
            ),
            "message": (
                f"Sharp turn ahead in "
                f"{round(distance_ahead)} m."
            ),
        }