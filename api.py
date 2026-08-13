import osmnx as ox
from maps.geocoder import geocode_place
from maps.places_search import search_places
from fastapi import FastAPI
from pydantic import BaseModel

from maps.graph_manager import GraphManager

from engine.global_router import route_global
from engine.q_router import QRouter
from engine.edge_updater import EdgeUpdater
from engine.route_safety import RouteSafetyAnalyzer
from engine.hazards import HazardEngine


app = FastAPI(
    title="Q-Routing API",
    description="Global dynamic emergency vehicle routing backend",
    version="2.0.0",
)


GRAPH_MANAGER = GraphManager()


class RouteRequest(BaseModel):

    start_lat: float
    start_lon: float

    destination_lat: float
    destination_lon: float

    emergency_mode: bool = False

    traffic_level: str = "free"

    weather_penalty: float = 0.0

    flood_penalty: float = 0.0

    incident_type: str = "none"

    road_risk: float = 0.0

    hazard_lat: float | None = None
    hazard_lon: float | None = None

    hazard_type: str = "none"

    hazard_penalty: float = 0.0

    hazard_closed: bool = False


def initialise_edges(graph):

    for u, v, key, data in graph.edges(
        keys=True,
        data=True,
    ):

        length = float(
            data.get(
                "length",
                1.0,
            )
        )

        data["travel_time"] = length
        data["q_cost"] = length


def update_all_edges(
    graph,
    edge_updater,
    request,
):

    for u, v, key in graph.edges(
        keys=True
    ):

        edge_updater.update_edge(
            u,
            v,
            traffic_level=request.traffic_level,
            weather_penalty=request.weather_penalty,
            flood_penalty=request.flood_penalty,
            incident_type=request.incident_type,
            emergency_mode=request.emergency_mode,
            road_risk=request.road_risk,
        )


def get_edge_distance(
    graph,
    u,
    v,
):

    edge_data = graph[u][v]

    distances = []

    for data in edge_data.values():

        distances.append(
            float(
                data.get(
                    "length",
                    0.0,
                )
            )
        )

    if not distances:
        return 0.0

    return min(distances)


def calculate_route_distance(
    graph,
    route,
):

    total = 0.0

    for u, v in zip(
        route[:-1],
        route[1:],
    ):

        total += get_edge_distance(
            graph,
            u,
            v,
        )

    return round(
        float(total),
        2,
    )


@app.get("/")
def root():

    return {
        "status": "online",
        "service": "Q-Routing",
        "version": "2.0.0",
        "coverage": "global",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "road_network": "global",
        "routing_engine": "online",
    }


@app.post("/route")
def calculate_route(
    request: RouteRequest,
):

    print(
        "Loading graph for requested route..."
    )

    graph = GRAPH_MANAGER.get_graph(
        request.start_lat,
        request.start_lon,
    )

    print("Graph selected.")

    router = QRouter(graph)

    edge_updater = EdgeUpdater(
        graph
    )

    safety_analyzer = (
        RouteSafetyAnalyzer(
            graph
        )
    )

    hazard_engine = HazardEngine(
        graph
    )

    initialise_edges(graph)

    update_all_edges(
        graph,
        edge_updater,
        request,
    )

    hazard_result = None

    if (
        request.hazard_lat is not None
        and request.hazard_lon is not None
        and request.hazard_type != "none"
    ):

        hazard_result = (
            hazard_engine.apply_hazard(
                latitude=request.hazard_lat,
                longitude=request.hazard_lon,
                penalty=request.hazard_penalty,
                hazard_type=request.hazard_type,
                closed=request.hazard_closed,
            )
        )

    start_node = (
        ox.distance.nearest_nodes(
            graph,
            X=request.start_lon,
            Y=request.start_lat,
        )
    )

    destination_node = (
        ox.distance.nearest_nodes(
            graph,
            X=request.destination_lon,
            Y=request.destination_lat,
        )
    )

    result = router.calculate_route(
        start_node,
        destination_node,
    )

    route = result["route"]

    route_distance = (
        calculate_route_distance(
            graph,
            route,
        )
    )

    safety_alerts = (
        safety_analyzer.analyze_route(
            route,
            minimum_angle=60.0,
        )
    )

    cleaned_alerts = []

    for alert in safety_alerts:

        cleaned_alerts.append(
            {
                "alert_type": alert[
                    "alert_type"
                ],
                "severity": alert[
                    "severity"
                ],
                "node": int(
                    alert["node"]
                ),
                "turn_angle": float(
                    alert["turn_angle"]
                ),
                "distance_from_start_m": float(
                    alert[
                        "distance_from_start_m"
                    ]
                ),
                "message": alert[
                    "message"
                ],
            }
        )

    route_coordinates = []

    for node in route:

        node_data = graph.nodes[node]

        route_coordinates.append(
            {
                "latitude": float(
                    node_data["y"]
                ),
                "longitude": float(
                    node_data["x"]
                ),
            }
        )

    return {

        "status": "success",

        "emergency_mode": (
            request.emergency_mode
        ),

        "conditions": {

            "traffic_level": (
                request.traffic_level
            ),

            "weather_penalty": (
                request.weather_penalty
            ),

            "flood_penalty": (
                request.flood_penalty
            ),

            "incident_type": (
                request.incident_type
            ),

            "road_risk": (
                request.road_risk
            ),
        },

        "hazard": hazard_result,

        "start": {

            "latitude": request.start_lat,

            "longitude": request.start_lon,
        },

        "destination": {

            "latitude": (
                request.destination_lat
            ),

            "longitude": (
                request.destination_lon
            ),
        },

        "route": [
            int(node)
            for node in route
        ],

        "route_coordinates": (
            route_coordinates
        ),

        "route_nodes": len(route),

        "route_distance_m": (
            route_distance
        ),

        "route_cost": float(
            result["total_cost"]
        ),

        "safety_alerts": (
            cleaned_alerts
        ),

        "safety_alert_count": (
            len(cleaned_alerts)
        ),
    }
@app.get("/geocode")
def geocode(query: str):

    geoapify_results = search_places(
        query,
        limit=10,
    )

    if geoapify_results:
        return {
            "source": "geoapify",
            "results": geoapify_results,
        }

    osm_results = geocode_place(
        query,
        limit=10,
    )

    return {
        "source": "openstreetmap",
        "results": osm_results,
    }
@app.get("/route/place")
def route_place(
    start: str,
    destination: str,
):
    start_results = geocode_place(
        start,
        limit=1,
    )

    destination_results = geocode_place(
        destination,
        limit=1,
    )

    if not start_results:
        return {
            "status": "error",
            "message": "Start location not found",
        }

    if not destination_results:
        return {
            "status": "error",
            "message": "Destination not found",
        }

    start_location = start_results[0]
    destination_location = destination_results[0]

    graph = GRAPH_MANAGER.get_graph(
        destination_location["latitude"],
        destination_location["longitude"],
    )

    initialise_edges(graph)

    result = route_global(
        start_location["latitude"],
        start_location["longitude"],
        destination_location["latitude"],
        destination_location["longitude"],
        GRAPH_MANAGER,
    )

    result["start_location"] = start_location
    result["destination_location"] = destination_location

    return result