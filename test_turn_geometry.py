from engine.safety_alerts import SafetyAlertEngine


engine = SafetyAlertEngine()


print("# TURN GEOMETRY TEST")
print("====================")


# Road approaching a 90-degree turn
previous_point = (25.2000, 55.3000)
current_point = (25.2000, 55.3010)
next_point = (25.2010, 55.3010)


angle = engine.calculate_turn_angle(
    previous_point,
    current_point,
    next_point,
)


print()
print("Calculated turn angle:")
print(round(angle, 2), "degrees")


alert = engine.sharp_turn_alert(
    turn_angle=angle,
    distance_ahead=120,
)


print()
print("Generated alert:")
print(alert)