import requests

from weather.weather_data import (
    WeatherData,
    validate_weather,
)


def get_weather(latitude: float, longitude: float) -> WeatherData:
    """
    Retrieve forecast data for a geographic location.

    Uses Open-Meteo, which provides weather forecast
    data without requiring an API key.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "hourly": (
            "precipitation_probability,"
            "precipitation,"
            "visibility,"
            "wind_speed_10m"
        ),
        "forecast_days": 2,
        "timezone": "auto",
    }

    response = requests.get(
        url,
        params=parameters,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    current = data.get("current", {})
    hourly = data.get("hourly", {})

    precipitation_probability = None
    visibility_km = None

    probabilities = hourly.get(
        "precipitation_probability"
    )

    visibilities = hourly.get("visibility")

    if probabilities:
        precipitation_probability = probabilities[0]

    if visibilities:
        visibility_km = visibilities[0] / 1000


    weather = WeatherData(
        temperature_c=current.get(
            "temperature_2m"
        ),

        precipitation_probability=(
            precipitation_probability
        ),

        precipitation_mm=current.get(
            "precipitation"
        ),

        wind_speed_kmh=current.get(
            "wind_speed_10m"
        ),

        visibility_km=visibility_km,
    )


    if not validate_weather(weather):
        raise ValueError(
            "Weather source returned invalid data."
        )

    return weather