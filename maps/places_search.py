import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEOAPIFY_API_KEY")

BASE_URL = "https://api.geoapify.com/v1/geocode/search"


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return set(text.split())


def search_places(query, limit=10):

    if not API_KEY:
        raise RuntimeError(
            "GEOAPIFY_API_KEY is not configured"
        )

    params = {
        "text": query,
        "limit": 10,
        "apiKey": API_KEY,
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    query_words = normalize(query)

    results = []

    for feature in data.get("features", []):

        properties = feature.get(
            "properties",
            {},
        )

        display_name = properties.get(
            "formatted",
            "",
        )

        name = properties.get(
            "name",
            "",
        )

        city = properties.get(
            "city",
            "",
        )

        state = properties.get(
            "state",
            "",
        )

        country = properties.get(
            "country",
            "",
        )

        searchable = normalize(
            f"{name} {display_name} "
            f"{city} {state} {country}"
        )

        score = len(
            query_words & searchable
        )

        results.append(
            {
                "latitude": properties.get(
                    "lat"
                ),
                "longitude": properties.get(
                    "lon"
                ),
                "name": name,
                "display_name": display_name,
                "type": properties.get(
                    "result_type"
                ),
                "country": country,
                "city": city,
                "state": state,
                "postcode": properties.get(
                    "postcode"
                ),
                "_score": score,
            }
        )

    results.sort(
        key=lambda x: x["_score"],
        reverse=True,
    )

    for result in results:
        result.pop("_score", None)

    return results[:limit]