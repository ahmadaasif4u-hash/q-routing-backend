from dataclasses import dataclass
from enum import Enum
from typing import Optional


class HazardStatus(str, Enum):
    CONFIRMED = "confirmed"
    PREDICTED = "predicted"
    REPORTED = "reported"


class HazardType(str, Enum):
    HEAVY_RAIN = "heavy_rain"
    FLOODING = "flooding"
    FLASH_FLOOD = "flash_flood"
    STRONG_WIND = "strong_wind"
    DUST_STORM = "dust_storm"
    FOG = "fog"
    HAIL = "hail"
    THUNDERSTORM = "thunderstorm"
    LANDSLIDE = "landslide"
    ROCKFALL = "rockfall"
    ROAD_SUBSIDENCE = "road_subsidence"
    SINKHOLE = "sinkhole"
    COASTAL_FLOODING = "coastal_flooding"
    FALLEN_TREE = "fallen_tree"
    WILDFIRE_SMOKE = "wildfire_smoke"
    ANIMAL_CROSSING = "animal_crossing"
    ROAD_OBSTRUCTION = "road_obstruction"


@dataclass
class Hazard:
    hazard_type: HazardType
    status: HazardStatus

    # 0.0 = no confidence
    # 1.0 = complete confidence
    confidence: float

    # Estimated additional delay in minutes
    predicted_delay: float

    # How severely the hazard affects the road
    severity: float

    description: str = ""

    def __post_init__(self):
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.severity = max(0.0, min(1.0, self.severity))
        self.predicted_delay = max(0.0, self.predicted_delay)

    def routing_penalty(self) -> float:
        """
        Calculates how strongly this hazard should influence routing.

        This is deliberately simple for version 1.
        We will later replace this with a more rigorous
        calibrated model using real data.
        """

        return (
            self.predicted_delay
            * self.severity
            * self.confidence
        )


@dataclass
class HazardAssessment:
    road_id: str
    hazard: Hazard

    def routing_penalty(self) -> float:
        return self.hazard.routing_penalty()

    def summary(self) -> dict:
        return {
            "road_id": self.road_id,
            "hazard_type": self.hazard.hazard_type.value,
            "status": self.hazard.status.value,
            "confidence": round(self.hazard.confidence, 3),
            "severity": round(self.hazard.severity, 3),
            "predicted_delay": round(
                self.hazard.predicted_delay,
                2
            ),
            "routing_penalty": round(
                self.routing_penalty(),
                2
            ),
            "description": self.hazard.description,
        }