from maps.geocoder import geocode_place


results = geocode_place(
    "Sheikh Zayed Road, Abu Dhabi",
    limit=10,
)


print("# GLOBAL GEOCODING TEST")
print("=======================")

print("Results found:", len(results))

for i, result in enumerate(results, 1):

    print()
    print("RESULT", i)
    print("Latitude:", result["latitude"])
    print("Longitude:", result["longitude"])
    print("Type:", result["type"])
    print("Place:", result["display_name"])