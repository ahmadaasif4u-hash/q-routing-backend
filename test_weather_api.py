from weather.weather_api import get_weather


# Dubai test coordinates
latitude = 25.2048
longitude = 55.2708


weather = get_weather(
    latitude,
    longitude
)


print("# REAL WEATHER API TEST")
print("========================")

print(
    "Temperature:",
    weather.temperature_c,
    "°C"
)

print(
    "Precipitation probability:",
    weather.precipitation_probability,
    "%"
)

print(
    "Precipitation:",
    weather.precipitation_mm,
    "mm"
)

print(
    "Wind speed:",
    weather.wind_speed_kmh,
    "km/h"
)

print(
    "Visibility:",
    weather.visibility_km,
    "km"
)