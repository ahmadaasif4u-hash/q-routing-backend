from engine.traffic import TrafficEngine


engine = TrafficEngine()

base_time = 10.0

levels = [
    "free",
    "light",
    "moderate",
    "heavy",
    "severe",
    "closed",
]

print("# TRAFFIC ENGINE TEST")
print("=====================")

for level in levels:

    penalty = engine.calculate_penalty(
        base_time,
        level,
    )

    adjusted = engine.adjusted_travel_time(
        base_time,
        level,
    )

    print()
    print("Traffic:", level)
    print("Penalty:", penalty)
    print("Adjusted travel time:", adjusted)