import re
import requests

from rapidfuzz.fuzz import token_set_ratio

from maps.geocoder import geocode_place
from maps.places_search import search_places


def normalize(text):
    return re.sub(
        r"[^a-z0-9\s]",
        " ",
        str(text).lower(),
    )


def score_result(query, result, preferred_city=None):
    query_score = token_set_ratio(
        normalize(query),
        normalize(
            " ".join(
                str(result.get(key, ""))
                for key in [
                    "name",
                    "display_name",
                    "city",
                    "state",
                    "country",
                ]
            )
        ),
    )

    location_bonus = 0

    if preferred_city:
        city = normalize(
            result.get("city", "")
        )

        preferred = normalize(
            preferred_city
        )

        if preferred in city or city in preferred:
            location_bonus = 100

    return query_score + location_bonus


def search_overpass(
    query,
    limit=10,
    latitude=None,
    longitude=None,
    radius=25000,
):
    url = (
        "https://overpass-api.de/api/interpreter"
    )

    escaped = query.replace(
        '"',
        '\\"',
    )

    if latitude is not None and longitude is not None:

        area_query = f"""
        (
          nwr["name"~"{escaped}",i]
          (around:{radius},{latitude},{longitude});
        );
        """

    else:

        area_query = f"""
        (
          nwr["name"~"{escaped}",i];
        );
        """

    overpass_query = f"""
    [out:json][timeout:30];
    {area_query}
    out center {limit};
    """

    try:

        response = requests.post(
            url,
            data=overpass_query,
            timeout=40,
        )

        response.raise_for_status()

        data = response.json()

    except Exception:

        return []

    results = []

    for element in data.get(
        "elements",
        [],
    ):

        tags = element.get(
            "tags",
            {},
        )

        center = element.get(
            "center",
            {},
        )

        lat = element.get(
            "lat",
            center.get("lat"),
        )

        lon = element.get(
            "lon",
            center.get("lon"),
        )

        if lat is None or lon is None:
            continue

        results.append(
            {
                "latitude": float(lat),
                "longitude": float(lon),
                "name": tags.get(
                    "name",
                    query,
                ),
                "display_name": tags.get(
                    "name",
                    query,
                ),
                "type": element.get(
                    "type"
                ),
                "city": tags.get(
                    "addr:city"
                ),
                "country": None,
                "source": "overpass",
            }
        )

    return results


def remove_duplicates(results):

    unique = []
    seen = set()

    for result in results:

        try:

            key = (
                round(
                    float(
                        result["latitude"]
                    ),
                    5,
                ),
                round(
                    float(
                        result["longitude"]
                    ),
                    5,
                ),
            )

        except Exception:
            continue

        if key in seen:
            continue

        seen.add(key)

        unique.append(result)

    return unique


def global_search(
    query,
    limit=10,
    preferred_city=None,
    latitude=None,
    longitude=None,
):

    results = []

    # Geoapify
    try:

        geo_results = search_places(
            query,
            limit=10,
        )

        for result in geo_results:

            result["source"] = (
                "geoapify"
            )

            results.append(result)

    except Exception:
        pass

    # Nominatim
    try:

        osm_results = geocode_place(
            query,
            limit=10,
        )

        for result in osm_results:

            result["source"] = (
                "nominatim"
            )

            results.append(result)

    except Exception:
        pass

    # Nearby Overpass
    results.extend(
        search_overpass(
            query,
            limit=10,
            latitude=latitude,
            longitude=longitude,
        )
    )

    results = remove_duplicates(
        results
    )

    for result in results:

        result["_score"] = score_result(
            query,
            result,
            preferred_city,
        )

    results.sort(
        key=lambda x: x["_score"],
        reverse=True,
    )

    for result in results:

        result.pop(
            "_score",
            None,
        )

    return results[:limit]