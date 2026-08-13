import requests


def geocode_place(query, limit=10):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": limit,
        "addressdetails": 1,
        "accept-language": "en",
    }

    headers = {
        "User-Agent": "Q-Routing/1.0",
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15,
    )

    response.raise_for_status()

    results = response.json()

    locations = []

    for result in results:
        locations.append(
            {
                "latitude": float(result["lat"]),
                "longitude": float(result["lon"]),
                "display_name": result["display_name"],
                "type": result.get("type"),
                "address": result.get("address", {}),
            }
        )

    return locations