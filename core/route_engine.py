"""
Route Engine — Thermal Route Scoring
=====================================
Loads demo routes, fetches FortyGuard temperature data
for each waypoint, and scores routes using the battery model.
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
    return [v["city"] + ", " + v["state"] for v in CITY_DATA.values()]


def get_city_key(city_display: str) -> str:
    for key, val in CITY_DATA.items():
        if f"{val['city']}, {val['state']}" == city_display:
            return key
    return list(CITY_DATA.keys())[0]


def score_routes(city_key: str, vehicle_key: str,
                 client: FortyGuardClient) -> dict:
    """
    Main route scoring function.
    1. Load routes for the city
    2. Fetch FortyGuard temperature + satellite data per route
    3. Apply battery degradation model
    4. Return scored comparison
    """
    city = CITY_DATA[city_key]
    routes_raw = city["routes"]

    # Fetch satellite data for shade score (one call per city)
    city_location = f"{city['center'][0]},{city['center'][1]}"
    satellite = client.get_satellite(city_location)
    env = client.get_env_params(city_location, analysis_layer="persistence")
    solar = env.get("solar_irradiance_wm2", 800)

    routes_scored = []
    for route_key, route_data in routes_raw.items():
        # Use pre-defined temps (reliable for demo) or query API per waypoint
        if client.demo_mode:
            segment_temps = route_data["segment_temps_f"]
            avg_temp = route_data["avg_temp_f"]
            shade = route_data["shade_pct"]
        else:
            # Live API: query each waypoint
            segment_temps = client.get_route_segment_temps(
                route_data["waypoints"], analysis_layer="exceedance"
            )
            avg_temp = sum(segment_temps) / len(segment_temps)
            shade = satellite.get("vegetation_pct", 10)

        routes_scored.append({
            "key": route_key,
            "name": route_data["name"],
            "description": route_data["description"],
            "distance_miles": route_data["distance_miles"],
            "duration_minutes": route_data["duration_minutes"],
            "avg_temp_f": avg_temp,
            "shade_pct": shade,
            "segment_temps": segment_temps,
            "waypoints": route_data["waypoints"],
            "color": route_data["color"],
            "risk_level": route_data["risk_level"]
        })

    comparison = battery_model.compare_routes(routes_scored, vehicle_key, solar)
    comparison["city"] = city["city"]
    comparison["state"] = city["state"]
    comparison["center"] = city["center"]
    comparison["satellite"] = satellite
    comparison["env_params"] = env
    comparison["solar_irradiance_wm2"] = solar
    comparison["route_details"] = routes_scored

    return comparison


def get_forecast_schedule(city_key: str, client: FortyGuardClient) -> list:
    """
    Fetch 12-hour temperature forecast for workload planning.
    Max 12 hours — enforced by client.
    """
    city = CITY_DATA[city_key]
    location = f"{city['center'][0]},{city['center'][1]}"
    return client.get_forecast(location, hours_ahead=12)


def multi_city_snapshot(vehicle_key: str, client: FortyGuardClient) -> list:
    """
    Snapshot of thermal risk across all supported cities.
    Used for fleet manager city-comparison dashboard.
    """
    results = []
    for city_key, city in CITY_DATA.items():
        location = f"{city['center'][0]},{city['center'][1]}"
        heatmap = client.get_heatmap(location, analysis_layer="snapshot")
        env = client.get_env_params(location, analysis_layer="persistence")
        temp = heatmap.get("temperature_f", 100)
        factor = battery_model.degradation_factor(temp)

        results.append({
            "city_key": city_key,
            "city": city["city"],
            "state": city["state"],
            "center": city["center"],
            "temp_f": temp,
            "risk_level": heatmap.get("risk_level", "moderate"),
            "degradation_factor": factor,
            "heat_index_f": env.get("heat_index_f", temp + 5),
            "persistence_hours": env.get("persistence_hours", 6),
            "color": battery_model.risk_color(temp)
        })

    results.sort(key=lambda x: x["temp_f"], reverse=True)
    return results
