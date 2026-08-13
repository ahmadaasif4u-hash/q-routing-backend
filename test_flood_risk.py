from hazards.flood_risk import (
    calculate_flood_risk,
    flood_penalty,
)


# -------------------------------------------------
# CASE 1: NORMAL ROAD
# -------------------------------------------------

normal_risk = calculate_flood_risk(
    rainfall_mm=0,
    elevation_m=50,
    drainage_factor=0.1,
    water_proximity_factor=0.1,
)

normal_cost = flood_penalty(
    10.0,
    normal_risk,
)


# -------------------------------------------------
# CASE 2: HEAVY RAIN
# -------------------------------------------------

heavy_rain_risk = calculate_flood_risk(
    rainfall_mm=25,
    elevation_m=20,
    drainage_factor=0.5,
    water_proximity_factor=0.5,
)

heavy_rain_cost = flood_penalty(
    10.0,
    heavy_rain_risk,
)


# -------------------------------------------------
# CASE 3: EXTREME FLOOD CONDITIONS
# -------------------------------------------------

extreme_risk = calculate_flood_risk(
    rainfall_mm=50,
    elevation_m=5,
    drainage_factor=0.9,
    water_proximity_factor=0.9,
)

extreme_cost = flood_penalty(
    10.0,
    extreme_risk,
)


# -------------------------------------------------
# RESULTS
# -------------------------------------------------

print("# FLOOD RISK TEST")
print("=================")

print()
print("Normal road")
print("Flood risk:", round(normal_risk, 3))
print("Road cost:", normal_cost)

print()
print("Heavy rain")
print("Flood risk:", round(heavy_rain_risk, 3))
print("Road cost:", round(heavy_rain_cost, 3))

print()
print("Extreme conditions")
print("Flood risk:", round(extreme_risk, 3))
print("Road cost:", extreme_cost)