from engine.incidents import IncidentEngine


engine = IncidentEngine()

base_time = 10.0

incidents = [
    "none",
    "minor_accident",
    "major_accident",
    "construction",
    "obstruction",
    "emergency_closure",
]


print("# INCIDENT ENGINE TEST")
print("======================")

for incident in incidents:

    penalty = engine.get_penalty(
        base_time,
        incident,
    )

    closed = engine.is_closed(
        incident,
    )

    print()
    print("Incident:", incident)
    print("Penalty:", penalty)
    print("Road closed:", closed)