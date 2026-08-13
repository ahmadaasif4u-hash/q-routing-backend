from weather.weather_data import WeatherData
from hazards.hazard_engine import analyze_weather


severe_weather = WeatherData(
    temperature_c=42,
    precipitation_probability=95,
    precipitation_mm=25,
    wind_speed_kmh=70,
    visibility_km=1,
    humidity_percent=90,
)


hazards = analyze_weather(severe_weather)


print("# SEVERE WEATHER HAZARD TEST")
print("=============================")

print("Rain probability:", severe_weather.precipitation_probability, "%")
print("Rainfall:", severe_weather.precipitation_mm, "mm")
print("Wind:", severe_weather.wind_speed_kmh, "km/h")
print("Visibility:", severe_weather.visibility_km, "km")

print()
print("# DETECTED HAZARDS")
print("===================")


for hazard in hazards:

    print()
    print("Hazard:", hazard.hazard)
    print("Risk:", round(hazard.risk_score, 3))
    print("Severity:", hazard.severity)
    print("Confidence:", hazard.confidence)
    print("Reason:", hazard.reason)