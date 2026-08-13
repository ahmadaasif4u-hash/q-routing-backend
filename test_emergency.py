from engine.emergency import EmergencyVehicleEngine


engine = EmergencyVehicleEngine()

base_time = 10.0
road_risk = 0.8


print("# EMERGENCY VEHICLE ENGINE TEST")
print("===============================")

print()
print("Emergency mode:", engine.is_emergency_mode())

normal_penalty = engine.calculate_priority_penalty(
    base_time,
    road_risk,
)

print("Normal penalty:", normal_penalty)


engine.set_mode(True)

print()
print("Emergency mode:", engine.is_emergency_mode())

emergency_penalty = engine.calculate_priority_penalty(
    base_time,
    road_risk,
)

print("Emergency penalty:", emergency_penalty)