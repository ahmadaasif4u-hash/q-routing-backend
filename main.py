import os
import time
import threading
from typing import Optional

import osmnx as ox

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from maps.graph_manager import GraphManager
from engine.q_router import QRouter
from engine.edge_updater import EdgeUpdater
from engine.route_safety import RouteSafetyAnalyzer
from engine.hazards import HazardEngine
from engine.weather import WeatherEngine


# ============================================================
# Q-ROUTING API
# ============================================================

app = FastAPI(
    title="Q-Routing API",
    description="Universal predictive navigation and emergency routing backend",
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GLOBAL ENGINES
# ============================================================

GRAPH_MANAGER = GraphManager()
WEATHER_ENGINE = WeatherEngine()

REQUEST_LOCK = threading.Lock()

MAX_ROUTE_DISTANCE_KM = 50
MAX_HAZARD_RADIUS_M = 5000
REQUEST_COOLDOWN_SECONDS = 0.5

_last_request_time = 0.0


# ============================================================
# REQUEST MODEL
# ============================================================

class RouteRequest(BaseModel):

    start_lat: float = Field(..., ge=-90, le=90)
    start_lon: float = Field(..., ge=-180, le=180)

    destination_lat: float = Field(..., ge=-90, le=90)
    destination_lon: float = Field(..., ge=-180, le=180)

    emergency_mode: bool = False

    traffic_level: str = "free"

    flood_penalty: float = Field(
        default=0.0,
        ge=0,
        le=100000,
    )

    incident_type: str = "none"

    road_risk: float = Field(
        default=0.0,
        ge=0,
        le=100000,
    )

    hazard_lat: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )

    hazard_lon: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )

    hazard_type: str = "none"

    hazard_penalty: float = Field(
        default=0.0,
        ge=0,
        le=100000,
    )

    hazard_closed: bool = False

    hazard_radius_m: float = Field(
        default=250.0,
        ge=0,
        le=MAX_HAZARD_RADIUS_M,
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_request(request: RouteRequest):

    valid_traffic_levels = {
        "free",
        "light",
        "moderate",
        "heavy",
        "severe",
        "closed",
    }

    if request.traffic_level not in valid_traffic_levels:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid traffic_level. "
                "Use free, light, moderate, heavy, severe, or closed."
            ),
        )

    if request.hazard_type == "none":

        if (
            request.hazard_lat is not None
            or request.hazard_lon is not None
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "hazard_lat and hazard_lon require "
                    "a valid hazard_type."
                ),
            )

    if request.hazard_type != "none":

        if (
            request.hazard_lat is None
            or request.hazard_lon is None
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "hazard_lat and hazard_lon are required "
                    "when hazard_type is specified."
                ),
            )


# ============================================================
# REQUEST RATE PROTECTION
# ============================================================

def check_request_rate():

    global _last_request_time

    with REQUEST_LOCK:

        current_time = time.time()

        if (
            current_time - _last_request_time
            < REQUEST_COOLDOWN_SECONDS
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Requests are arriving too quickly. "
                    "Please wait briefly and try again."
                ),
            )

        _last_request_time = current_time


# ============================================================
# GRAPH INITIALISATION
# ============================================================

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


# ============================================================
# EDGE UPDATES
# ============================================================

def update_all_edges(
    graph,
    edge_updater,
    request,
    weather_penalty,
):

    for u, v, key in graph.edges(
        keys=True
    ):

        edge_updater.update_edge(
            u,
            v,
            traffic_level=request.traffic_level,
            weather_penalty=weather_penalty,
            flood_penalty=request.flood_penalty,
            incident_type=request.incident_type,
            emergency_mode=request.emergency_mode,
            road_risk=request.road_risk,
        )


# ============================================================
# EDGE DISTANCE
# ============================================================

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


# ============================================================
# ROUTE DISTANCE
# ============================================================

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


# ============================================================
# ROUTE COORDINATES
# ============================================================

def build_route_coordinates(
    graph,
    route,
):

    coordinates = []

    for node in route:

        node_data = graph.nodes[node]

        coordinates.append(
            {
                "latitude": float(
                    node_data["y"]
                ),
                "longitude": float(
                    node_data["x"]
                ),
            }
        )

    return coordinates


# ============================================================
# ROUTE SUMMARY
# ============================================================

def route_summary(
    graph,
    route_data,
):

    route = route_data["route"]

    return {
        "route_nodes": len(route),

        "route_distance_m": (
            calculate_route_distance(
                graph,
                route,
            )
        ),

        "route_cost": float(
            route_data["total_cost"]
        ),
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "project": "Q-Routing",
        "status": "online",
        "version": "2.0.0",
        "scope": "global",
        "routing": "enabled",
        "weather": "enabled",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "road_network": "global",
        "routing_engine": "online",
        "weather_engine": "online",
        "api_version": "2.0.0",
    }


# ============================================================
# ROUTE ENDPOINT
# ============================================================

@app.post("/route")
def calculate_route(
    request: RouteRequest,
):

    check_request_rate()

    validate_request(request)

    try:

        print(
            "=========================================="
        )

        print(
            "Q-ROUTING REQUEST"
        )

        print(
            f"Start: "
            f"{request.start_lat}, "
            f"{request.start_lon}"
        )

        print(
            f"Destination: "
            f"{request.destination_lat}, "
            f"{request.destination_lon}"
        )

        print(
            f"Emergency: "
            f"{request.emergency_mode}"
        )

        print(
            "=========================================="
        )

        # ----------------------------------------------------
        # LOAD ROAD NETWORK
        # ----------------------------------------------------

        print(
            "Loading road network..."
        )

        graph = GRAPH_MANAGER.get_graph(
            request.start_lat,
            request.start_lon,
        )

        print(
            "Road network loaded."
        )

        # ----------------------------------------------------
        # CREATE ENGINES
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # INITIALISE EDGES
        # ----------------------------------------------------

        initialise_edges(graph)

        # ----------------------------------------------------
        # WEATHER
        # ----------------------------------------------------

        weather = WEATHER_ENGINE.get_weather(
            request.start_lat,
            request.start_lon,
        )

        weather_penalty = (
            WEATHER_ENGINE.calculate_penalty(
                weather
            )
        )

        # ----------------------------------------------------
        # UPDATE ROAD CONDITIONS
        # ----------------------------------------------------

        update_all_edges(
            graph,
            edge_updater,
            request,
            weather_penalty,
        )

        # ----------------------------------------------------
        # HAZARD
        # ----------------------------------------------------

        hazard_result = None

        if (
            request.hazard_lat is not None
            and request.hazard_lon is not None
            and request.hazard_type != "none"
        ):

            print(
                "Applying hazard..."
            )

            hazard_result = (
                hazard_engine.apply_hazard(
                    latitude=request.hazard_lat,
                    longitude=request.hazard_lon,
                    penalty=request.hazard_penalty,
                    hazard_type=request.hazard_type,
                    closed=request.hazard_closed,
                    radius_m=request.hazard_radius_m,
                )
            )

        # ----------------------------------------------------
        # FIND START NODE
        # ----------------------------------------------------

        start_node = (
            ox.distance.nearest_nodes(
                graph,
                X=request.start_lon,
                Y=request.start_lat,
            )
        )

        # ----------------------------------------------------
        # FIND DESTINATION NODE
        # ----------------------------------------------------

        destination_node = (
            ox.distance.nearest_nodes(
                graph,
                X=request.destination_lon,
                Y=request.destination_lat,
            )
        )

        # ----------------------------------------------------
        # CALCULATE ROUTES
        # ----------------------------------------------------

        print(
            "Calculating routes..."
        )

        alternatives = (
            router.calculate_alternatives(
                start_node,
                destination_node,
            )
        )

        if not alternatives:
            raise HTTPException(
                status_code=404,
                detail="No route could be calculated.",
            )

        if "optimized" not in alternatives:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Routing engine did not return "
                    "an optimized route."
                ),
            )

        result = alternatives["optimized"]

        route = result["route"]

        # ----------------------------------------------------
        # ROUTE DISTANCE
        # ----------------------------------------------------

        route_distance = (
            calculate_route_distance(
                graph,
                route,
            )
        )

        # ----------------------------------------------------
        # SAFETY ANALYSIS
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # ROUTE COORDINATES
        # ----------------------------------------------------

        route_coordinates = (
            build_route_coordinates(
                graph,
                route,
            )
        )

        # ----------------------------------------------------
        # ALTERNATIVE SUMMARIES
        # ----------------------------------------------------

        fastest_summary = route_summary(
            graph,
            alternatives["fastest"],
        )

        safest_summary = route_summary(
            graph,
            alternatives["safest"],
        )

        optimized_summary = route_summary(
            graph,
            alternatives["optimized"],
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        print(
            "Route calculated successfully."
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
                    weather_penalty
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

            "weather": weather,

            "hazard": hazard_result,

            "start": {

                "latitude": (
                    request.start_lat
                ),

                "longitude": (
                    request.start_lon
                ),
            },

            "destination": {

                "latitude": (
                    request.destination_lat
                ),

                "longitude": (
                    request.destination_lon
                ),
            },

            "alternatives": {

                "fastest": fastest_summary,

                "safest": safest_summary,

                "optimized": optimized_summary,
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

    except HTTPException:
        raise

    except Exception as error:

        print(
            "Q-Routing ERROR:"
        )

        print(
            str(error)
        )

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Routing request failed.",
                "error": str(error),
            },
        )