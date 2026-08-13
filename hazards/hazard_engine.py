from dataclasses import dataclass
from typing import List

from weather.weather_data import WeatherData


@dataclass
class HazardResult:
    hazard: str
    risk_score: float
    severity: str
    confidence: float
    reason: str


def classify_severity(score: float) -> str:
    if score < 0.25:
        return "low"

    if score < 0.50:
        return "moderate"

    if score < 0.75:
        return "high"

    return "extreme"


def analyze_weather(weather: WeatherData) -> List[HazardResult]:

    results = []


    # -------------------------------------------------
    # HEAVY RAIN
    # -------------------------------------------------

    rain_probability = (
        weather.precipitation_probability or 0
    )

    rainfall = (
        weather.precipitation_mm or 0
    )


    rain_score = 0.0

    if rain_probability >= 70:
        rain_score += 0.35

    if rain_probability >= 90:
        rain_score += 0.20

    if rainfall >= 5:
        rain_score += 0.20

    if rainfall >= 20:
        rain_score += 0.25


    rain_score = min(rain_score, 1.0)


    if rain_score > 0:

        results.append(
            HazardResult(
                hazard="heavy_rain",
                risk_score=rain_score,
                severity=classify_severity(
                    rain_score
                ),
                confidence=0.80,
                reason=(
                    "Rain probability and/or "
                    "precipitation indicate "
                    "potential road impact."
                ),
            )
        )


    # -------------------------------------------------
    # STRONG WIND
    # -------------------------------------------------

    wind = (
        weather.wind_speed_kmh or 0
    )


    wind_score = 0.0

    if wind >= 40:
        wind_score = 0.35

    if wind >= 60:
        wind_score = 0.60

    if wind >= 80:
        wind_score = 0.85


    if wind_score > 0:

        results.append(
            HazardResult(
                hazard="strong_wind",
                risk_score=wind_score,
                severity=classify_severity(
                    wind_score
                ),
                confidence=0.85,
                reason=(
                    "Wind speed may reduce "
                    "vehicle stability and "
                    "increase road risk."
                ),
            )
        )


    # -------------------------------------------------
    # LOW VISIBILITY
    # -------------------------------------------------

    visibility = (
        weather.visibility_km
    )


    if visibility is not None:

        visibility_score = 0.0

        if visibility < 5:
            visibility_score = 0.40

        if visibility < 2:
            visibility_score = 0.70

        if visibility < 1:
            visibility_score = 0.90


        if visibility_score > 0:

            results.append(
                HazardResult(
                    hazard="low_visibility",
                    risk_score=visibility_score,
                    severity=classify_severity(
                        visibility_score
                    ),
                    confidence=0.90,
                    reason=(
                        "Reduced visibility "
                        "may increase driving risk."
                    ),
                )
            )


    return results