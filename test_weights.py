from routing.dynamic_weights import (
    RoadConditions,
    calculate_dynamic_cost,
)


print("# DYNAMIC ROAD WEIGHT TEST")
print()


# 1. Normal road
normal = RoadConditions()

normal_cost = calculate_dynamic_cost(
    base_travel_time=10,
    conditions=normal,
)

print("Normal road cost:", normal_cost)


# 2. Heavy traffic
traffic = RoadConditions(
    traffic_multiplier=2.5
)

traffic_cost = calculate_dynamic_cost(
    base_travel_time=10,
    conditions=traffic,
)

print("Heavy traffic cost:", traffic_cost)


# 3. Predicted flooding
flood = RoadConditions(
    traffic_multiplier=1.5,
    predicted_delay_minutes=20,
    hazard_risk=0.8,
)

flood_cost = calculate_dynamic_cost(
    base_travel_time=10,
    conditions=flood,
)

print("Predicted flood cost:", flood_cost)


# 4. Emergency vehicle
ambulance = RoadConditions(
    traffic_multiplier=1.5,
    predicted_delay_minutes=20,
    hazard_risk=0.8,
    emergency_priority=True,
)

ambulance_cost = calculate_dynamic_cost(
    base_travel_time=10,
    conditions=ambulance,
)

print("Ambulance cost:", ambulance_cost)


# 5. Closed road
closed = RoadConditions(
    road_closure=True
)

closed_cost = calculate_dynamic_cost(
    base_travel_time=10,
    conditions=closed,
)

print("Closed road cost:", closed_cost)