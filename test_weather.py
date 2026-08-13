from weather.weather_data import (
    WeatherData,
    validate_weather,
)


print("# WEATHER VALIDATION TEST")
print()


# Valid weather data
valid = WeatherData(
    temperature_c=35,
    precipitation_probability=0,
    precipitation_mm=0,
    wind_speed_kmh=20,
    visibility_km=10,
    humidity_percent=50,
)

print(
    "Valid data:",
    validate_weather(valid)
)


# Invalid rain probability
invalid_rain = WeatherData(
    precipitation_probability=150
)

print(
    "Invalid rain probability:",
    validate_weather(invalid_rain)
)


# Invalid wind speed
invalid_wind = WeatherData(
    wind_speed_kmh=-10
)

print(
    "Invalid wind speed:",
    validate_weather(invalid_wind)
)