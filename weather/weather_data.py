from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherData:
    temperature_c: Optional[float] = None
    precipitation_probability: Optional[float] = None
    precipitation_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    visibility_km: Optional[float] = None
    humidity_percent: Optional[float] = None
    thunderstorm_probability: Optional[float] = None
    snowfall_probability: Optional[float] = None
    timestamp: Optional[str] = None


def validate_weather(data: WeatherData) -> bool:

    if data.precipitation_probability is not None:
        if not 0 <= data.precipitation_probability <= 100:
            return False

    if data.humidity_percent is not None:
        if not 0 <= data.humidity_percent <= 100:
            return False

    if data.wind_speed_kmh is not None:
        if data.wind_speed_kmh < 0:
            return False

    if data.visibility_km is not None:
        if data.visibility_km < 0:
            return False

    if data.precipitation_mm is not None:
        if data.precipitation_mm < 0:
            return False

    if data.thunderstorm_probability is not None:
        if not 0 <= data.thunderstorm_probability <= 100:
            return False

    if data.snowfall_probability is not None:
        if not 0 <= data.snowfall_probability <= 100:
            return False

    return True