"""
Route Engine — Thermal Route Scoring
=====================================
Correlates logistics waypoint networks with FortyGuard Temperature API telemetry.
Scores candidate corridors using the Arrhenius electrochemical degradation model.
"""

import json
import os
from core.fortyguard_client import FortyGuardClient
from core.battery_model import BatteryDegradationModel


def _load_routes() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "demo_routes.json")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


CITY_DATA = _load_routes()
battery_model = BatteryDegradationModel()


def get_available_cities() -> list:
    return [f"{v['city']}, {v['state']}" for v in CITY_DATA.values()]


def get_city_key(city_display: str) -> str:
    for key, val in CITY_DATA.items():
        if f"{val['city']}, {val['state']}" == city_display:
            return key
    return list(CITY_DATA.keys())[0]


def score_routes(city_key: str, vehicle_key: str,
                 client: FortyGuardClient) -> dict:
    """
    Main route scoring pipeline:
    1. Loads target logistics network waypoints
    2. Queries FortyGuard API for waypoint temperatures and canopy coverage
    3. Evaluates electrochemical degradation per corridor
    4. Returns complete scored comparison with full metadata
    """
    city = CITY_DATA.get(city_key, list(CITY_DATA.values())[0])
    routes_raw = city["routes"]

    city_location = f"{city['center'][0]},{city['center'][1]}"
    satellite = client.get_satellite(city_location)
    env = client.get_env_params(city_location, analysis_layer="persistence")
    solar = env.get("solar_irradiance_wm2", 800)

    routes_input = []
    for route_key, route_data in routes_raw.items():
        if not client.has_live_key:
            segment_temps = route_data.get("segment_temps_f", [105.0] * 8)
            avg_temp = route_data.get("avg_temp_f", 105.0)
            shade = route_data.get("shade_pct", 15.0)
        else:
            segment_temps = client.get_route_segment_temps(
                route_data["waypoints"], analysis_layer="exceedance"
            )
            avg_temp = sum(segment_temps) / len(segment_temps) if segment_temps else 105.0
            shade = satellite.get("vegetation_pct", 15.0)

        routes_input.append({
            "key": route_key,
            "name": route_data["name"],
            "description": route_data.get("description", ""),
            "distance_miles": route_data.get("distance_miles", 8.0),
            "duration_minutes": route_data.get("duration_minutes", 30),
            "avg_temp_f": avg_temp,
            "shade_pct": shade,
            "segment_temps": segment_temps,
            "waypoints": route_data.get("waypoints", []),
            "color": route_data.get("color", "#38bdf8"),
            "risk_level": route_data.get("risk_level", "Moderate")
        })

    comparison = battery_model.compare_routes(routes_input, vehicle_key, solar)
    comparison["city"] = city["city"]
    comparison["state"] = city["state"]
    comparison["center"] = city["center"]
    comparison["satellite"] = satellite
    comparison["env_params"] = env
    comparison["solar_irradiance_wm2"] = solar
    comparison["route_details"] = comparison["routes"]

    return comparison


def get_forecast_schedule(city_key: str, client: FortyGuardClient) -> list:
    """
    Fetch 12-hour temperature forecast for workload planning.
    Max 12 hours — enforced by client.
    """
    city = CITY_DATA.get(city_key, list(CITY_DATA.values())[0])
    location = f"{city['center'][0]},{city['center'][1]}"
    return client.get_forecast(location, hours_ahead=12)


def multi_city_snapshot(vehicle_key: str, client: FortyGuardClient) -> list:
    """
    Snapshot of thermal risk across all supported US metropolitan logistics hubs.
    """
    results = []
    for city_key, city in CITY_DATA.items():
        location = f"{city['center'][0]},{city['center'][1]}"
        heatmap = client.get_heatmap(location, analysis_layer="snapshot")
        env = client.get_env_params(location, analysis_layer="persistence")
        
        # Take average of high-risk corridor in that city
        first_route = list(city["routes"].values())[0]
        temp = first_route.get("avg_temp_f", heatmap.get("temperature_f", 100))
        factor = battery_model.degradation_factor(temp)

        results.append({
            "city_key": city_key,
            "city": city["city"],
            "state": city["state"],
            "center": city["center"],
            "temp_f": temp,
            "risk_level": heatmap.get("risk_level", "moderate"),
            "degradation_factor": factor,
            "heat_index_f": env.get("heat_index_f", temp + 6),
            "persistence_hours": env.get("persistence_hours", 7.5),
            "color": battery_model.risk_color(temp)
        })

    results.sort(key=lambda x: x["temp_f"], reverse=True)
    return results
