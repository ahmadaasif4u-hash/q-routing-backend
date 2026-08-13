import requests

from weather.weather_data import (
    WeatherData,
    validate_weather,
)


# Last successfully retrieved weather data.
# This lets routing continue if Open-Meteo is temporarily unavailable.
_last_weather = None


def _fallback_weather() -> WeatherData:
    """
    Safe fallback used when the external weather service
    is temporarily unavailable.
    """

    return WeatherData(
        temperature_c=None,
        precipitation_probability=0,
        precipitation_mm=0.0,
        wind_speed_kmh=0.0,
        visibility_km=100.0,
    )


def get_weather(latitude: float, longitude: float) -> WeatherData:
    """
    Retrieve weather data from Open-Meteo.

    If Open-Meteo is unavailable or rate-limited,
    routing continues using the last successful weather
    result or a safe fallback.
    """

    global _last_weather

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

    try:
        response = requests.get(
            url,
            params=parameters,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        precipitation_probability = 0
        visibility_km = 100.0

        probabilities = hourly.get(
            "precipitation_probability"
        )

        visibilities = hourly.get(
            "visibility"
        )

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
                "precipitation",
                0.0
            ),

            wind_speed_kmh=current.get(
                "wind_speed_10m",
                0.0
            ),

            visibility_km=visibility_km,
        )

        if validate_weather(weather):
            _last_weather = weather
            return weather

        print(
            "WARNING: Open-Meteo returned invalid "
            "weather data. Using fallback."
        )

    except requests.RequestException as error:
        print(
            f"WARNING: Weather service unavailable: "
            f"{error}"
        )

    except (ValueError, KeyError, TypeError) as error:
        print(
            f"WARNING: Weather data could not be "
            f"processed: {error}"
        )

    # Prefer the last successful weather result.
    if _last_weather is not None:
        print(
            "Using cached weather data."
        )
        return _last_weather

    # No previous weather data exists.
    print(
        "Using safe fallback weather data."
    )

    return _fallback_weather()

