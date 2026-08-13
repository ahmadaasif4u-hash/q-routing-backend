import requests


class WeatherEngine:

    def __init__(self):
        self.url = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, latitude, longitude):

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "precipitation,"
                "rain,"
                "showers,"
                "snowfall,"
                "wind_speed_10m,"
                "visibility"
            ),
            "hourly": (
                "precipitation_probability,"
                "precipitation"
            ),
            "forecast_days": 1,
        }

        response = requests.get(
            self.url,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        current = data.get(
            "current",
            {},
        )

        hourly = data.get(
            "hourly",
            {},
        )

        probabilities = hourly.get(
            "precipitation_probability",
            [],
        )

        precipitation_probability = (
            max(probabilities)
            if probabilities
            else 0
        )

        return {
            "temperature_c": current.get(
                "temperature_2m"
            ),
            "precipitation_mm": current.get(
                "precipitation"
            ),
            "rain_mm": current.get(
                "rain"
            ),
            "wind_kmh": current.get(
                "wind_speed_10m"
            ),
            "visibility_m": current.get(
                "visibility"
            ),
            "precipitation_probability": (
                precipitation_probability
            ),
        }

    def calculate_penalty(
        self,
        weather,
    ):

        penalty = 0.0

        rain = float(
            weather.get(
                "rain_mm",
                0,
            ) or 0
        )

        probability = float(
            weather.get(
                "precipitation_probability",
                0,
            ) or 0
        )

        wind = float(
            weather.get(
                "wind_kmh",
                0,
            ) or 0
        )

        visibility = float(
            weather.get(
                "visibility_m",
                10000,
            ) or 10000
        )

        if rain >= 10:
            penalty += 10

        elif rain >= 5:
            penalty += 5

        if probability >= 80:
            penalty += 5

        elif probability >= 60:
            penalty += 2

        if wind >= 60:
            penalty += 10

        elif wind >= 40:
            penalty += 5

        if visibility < 1000:
            penalty += 15

        elif visibility < 3000:
            penalty += 7

        return penalty