from engine.safety_alerts import SafetyAlertEngine


engine = SafetyAlertEngine()


print("# SAFETY ALERT ENGINE TEST")
print("===========================")


# Sharp turn
sharp_turn = engine.sharp_turn_alert(
    turn_angle=85,
    distance_ahead=120,
)

print()
print("SHARP TURN")
print(sharp_turn)


# Accident-prone zone
accident_zone = engine.accident_zone_alert(
    risk_score=0.92,
    distance_ahead=350,
)

print()
print("ACCIDENT-PRONE ZONE")
print(accident_zone)


# Safe conditions
safe_turn = engine.sharp_turn_alert(
    turn_angle=25,
    distance_ahead=200,
)

safe_zone = engine.accident_zone_alert(
    risk_score=0.3,
    distance_ahead=500,
)

print()
print("SAFE CONDITIONS")
print("Sharp turn:", safe_turn)
print("Accident zone:", safe_zone)