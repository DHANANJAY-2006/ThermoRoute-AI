"""
Route Engine — Thermal Route Scoring with Real Road Geometry
=============================================================
Correlates logistics waypoint networks with FortyGuard Temperature API telemetry.
Scores candidate corridors using a 3-component EV cost model:

  1. Battery Degradation     — Arrhenius electrochemical kinetics
  2. Energy Efficiency Loss  — kWh/mile increase from AC load + battery resistance
  3. Range Overhead Cost     — scheduling and charging penalty from reduced effective range

Real road geometry fetched from OSRM public routing engine (router.project-osrm.org).
Falls back to straight-line waypoints if routing engine is unavailable.
"""

import json
import os
import requests
from core.fortyguard_client import FortyGuardClient
from core.battery_model import BatteryDegradationModel
from core.ev_energy_model import EVEnergyModel


def _load_routes() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "demo_routes.json")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


CITY_DATA = _load_routes()
battery_model = BatteryDegradationModel()
energy_model = EVEnergyModel()


def get_available_cities() -> list:
    return [f"{v['city']}, {v['state']}" for v in CITY_DATA.values()]


def get_city_key(city_display: str) -> str:
    for key, val in CITY_DATA.items():
        if f"{val['city']}, {val['state']}'" == city_display or f"{val['city']}, {val['state']}" == city_display:
            return key
    return list(CITY_DATA.keys())[0]


def get_osrm_route(waypoints: list, timeout: int = 6) -> list:
    """
    Fetches real road geometry from the public OSRM routing engine.
    Returns a list of [lat, lon] pairs suitable for a Folium PolyLine.
    Falls back gracefully to straight-line interpolation if OSRM is unreachable.

    OSRM coordinate convention: longitude,latitude (opposite of Folium lat,lon).
    """
    try:
        coords = ";".join(f"{wp['lon']},{wp['lat']}" for wp in waypoints)
        url = f"http://router.project-osrm.org/route/v1/driving/{coords}"
        params = {"geometries": "geojson", "overview": "full", "steps": "false"}
        resp = requests.get(url, params=params, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                geometry = data["routes"][0]["geometry"]["coordinates"]
                # OSRM returns [lon, lat]; Folium requires [lat, lon]
                return [[pt[1], pt[0]] for pt in geometry]
    except Exception:
        pass
    # Graceful fallback: straight-line segments between waypoints
    return [[wp["lat"], wp["lon"]] for wp in waypoints]


def score_routes(city_key: str, vehicle_key: str, client: FortyGuardClient) -> dict:
    """
    Main route scoring pipeline:
    1. Loads target logistics network waypoints for the chosen city
    2. Queries FortyGuard API for waypoint temperatures and canopy coverage
    3. Fetches real road geometry from OSRM for each corridor
    4. Computes 3-component annual cost per corridor:
         - Battery Arrhenius degradation cost
         - Energy efficiency surcharge (kWh/mile + AC load)
         - Range overhead (scheduling + charging penalty)
    5. Returns complete ranked comparison with full geometry for map rendering
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

        # Fetch real road geometry from OSRM
        road_geometry = get_osrm_route(route_data.get("waypoints", []))

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
            "road_geometry": road_geometry,
            "color": route_data.get("color", "#38bdf8"),
            "risk_level": route_data.get("risk_level", "Moderate"),
        })

    comparison = battery_model.compare_routes(routes_input, vehicle_key, solar, energy_model)
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
    Max 12 hours — enforced by FortyGuard client.
    """
    city = CITY_DATA.get(city_key, list(CITY_DATA.values())[0])
    location = f"{city['center'][0]},{city['center'][1]}"
    return client.get_forecast(location, hours_ahead=12)


def multi_city_snapshot(*args, **kwargs) -> list:
    """
    Snapshot of thermal risk and 3-component cost exposure
    across all supported US metropolitan logistics hubs.
    Universal *args/**kwargs signature to prevent any TypeError.
    """
    client = None
    vehicle_key = "Rivian_EDV_500"

    for a in args:
        if isinstance(a, FortyGuardClient):
            client = a
        elif isinstance(a, str):
            vehicle_key = a

    if "client" in kwargs and isinstance(kwargs["client"], FortyGuardClient):
        client = kwargs["client"]
    if "vehicle_key" in kwargs and isinstance(kwargs["vehicle_key"], str):
        vehicle_key = kwargs["vehicle_key"]

    if client is None:
        client = FortyGuardClient()

    results = []
    for city_key, city in CITY_DATA.items():
        location = f"{city['center'][0]},{city['center'][1]}"
        heatmap = client.get_heatmap(location, analysis_layer="snapshot")
        env = client.get_env_params(location, analysis_layer="persistence")

        first_route = list(city["routes"].values())[0]
        temp = first_route.get("avg_temp_f", heatmap.get("temperature_f", 100))
        factor = battery_model.degradation_factor(temp)

        # 3-component total cost for this city's primary corridor
        degrade_data = battery_model.annual_degradation_cost(temp, vehicle_key, 800, 5.0)
        energy_data = energy_model.total_operational_cost_annual(temp, vehicle_key)
        total_annual_cost = degrade_data["heat_annual_cost_usd"] + energy_data["annual_operational_penalty_usd"]

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
            "color": battery_model.risk_color(temp),
            "total_annual_cost_usd": round(total_annual_cost, 2),
            "energy_penalty_usd": round(energy_data["annual_energy_penalty_usd"], 2),
            "range_overhead_usd": round(energy_data["annual_range_overhead_usd"], 2),
        })

    results.sort(key=lambda x: x["temp_f"], reverse=True)
    return results
