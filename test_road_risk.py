from weather.weather_data import WeatherData
from hazards.hazard_engine import analyze_weather
from hazards.road_risk import apply_hazard_penalty


# -------------------------------------------------
# NORMAL CONDITIONS
# -------------------------------------------------

normal_weather = WeatherData(
    temperature_c=35,
    precipitation_probability=0,
    precipitation_mm=0,
    wind_speed_kmh=15,
    visibility_km=20,
)

normal_hazards = analyze_weather(
    normal_weather
)

normal_cost = apply_hazard_penalty(
    10.0,
    normal_hazards
)


# -------------------------------------------------
# SEVERE CONDITIONS
# -------------------------------------------------

severe_weather = WeatherData(
    temperature_c=42,
    precipitation_probability=95,
    precipitation_mm=25,
    wind_speed_kmh=70,
    visibility_km=1,
)

severe_hazards = analyze_weather(
    severe_weather
)

severe_cost = apply_hazard_penalty(
    10.0,
    severe_hazards
)


# -------------------------------------------------
# RESULTS
# -------------------------------------------------

print("# ROAD RISK TEST")
print("================")

print()
print("Normal conditions")
print("Hazards:", len(normal_hazards))
print("Road cost:", round(normal_cost, 3))

print()
print("Severe conditions")
print("Hazards:", len(severe_hazards))
print("Road cost:", round(severe_cost, 3))

print()
print(
    "Additional hazard penalty:",
    round(severe_cost - normal_cost, 3)
)