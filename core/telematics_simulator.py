"""
Fleet Telematics & In-Flight Rerouting Simulator
=================================================
Simulates real-time commercial EV telematics data streams for active fleet units.
Provides automated in-flight thermal risk detection and corridor rerouting triggers.
"""

import math
import random
from datetime import datetime


ACTIVE_FLEET_VEHICLES = [
    {
        "id": "VAN-101",
        "model": "Rivian EDV 500",
        "operator": "Amazon Logistics",
        "driver": "Marcus Vance",
        "lat": 33.4484,
        "lon": -112.0645,
        "target_lat": 33.5102,
        "target_lon": -112.0728,
        "active_corridor": "Route A (Central Urban Core)",
        "ambient_road_temp_f": 113.8,
        "pack_internal_temp_f": 109.5,
        "soc_pct": 74,
        "speed_mph": 24,
        "packages_remaining": 42,
        "status": "CRITICAL EXPOSURE",
        "reroute_available": True,
        "recommended_reroute": "Divert to I-10 / Loop 101 Freeway Bypass (95.9°F)"
    },
    {
        "id": "VAN-102",
        "model": "Mercedes eSprinter",
        "operator": "DHL Express",
        "driver": "Elena Rostova",
        "lat": 33.4350,
        "lon": -112.1150,
        "target_lat": 33.5102,
        "target_lon": -112.0728,
        "active_corridor": "Route C (Highway Bypass)",
        "ambient_road_temp_f": 95.8,
        "pack_internal_temp_f": 89.2,
        "soc_pct": 81,
        "speed_mph": 58,
        "packages_remaining": 38,
        "status": "OPTIMAL TRANSIT",
        "reroute_available": False,
        "recommended_reroute": "Maintain active corridor"
    },
    {
        "id": "VAN-103",
        "model": "Ford E-Transit",
        "operator": "FedEx Ground",
        "driver": "David Chen",
        "lat": 33.4658,
        "lon": -112.1001,
        "target_lat": 33.5102,
        "target_lon": -112.0728,
        "active_corridor": "Route B (19th Ave Arterial)",
        "ambient_road_temp_f": 104.8,
        "pack_internal_temp_f": 98.4,
        "soc_pct": 62,
        "speed_mph": 34,
        "packages_remaining": 29,
        "status": "ELEVATED RISK",
        "reroute_available": True,
        "recommended_reroute": "Assess Highway Bypass at next major junction"
    },
    {
        "id": "VAN-104",
        "model": "BrightDrop EV600",
        "operator": "FedEx Express",
        "driver": "Sarah Jenkins",
        "lat": 33.4285,
        "lon": -112.0450,
        "target_lat": 33.5102,
        "target_lon": -112.0728,
        "active_corridor": "Route C (Highway Bypass)",
        "ambient_road_temp_f": 96.2,
        "pack_internal_temp_f": 90.1,
        "soc_pct": 88,
        "speed_mph": 55,
        "packages_remaining": 54,
        "status": "OPTIMAL TRANSIT",
        "reroute_available": False,
        "recommended_reroute": "Maintain active corridor"
    },
    {
        "id": "VAN-105",
        "model": "Rivian EDV 500",
        "operator": "Amazon Logistics",
        "driver": "James Walker",
        "lat": 33.4532,
        "lon": -112.0740,
        "target_lat": 33.5102,
        "target_lon": -112.0728,
        "active_corridor": "Route A (Central Urban Core)",
        "ambient_road_temp_f": 114.2,
        "pack_internal_temp_f": 111.2,
        "soc_pct": 53,
        "speed_mph": 18,
        "packages_remaining": 61,
        "status": "CRITICAL EXPOSURE",
        "reroute_available": True,
        "recommended_reroute": "Immediate diversion to 19th Ave Arterial corridor"
    },
    {
        "id": "VAN-106",
        "model": "Mercedes eSprinter",
        "operator": "DHL Express",
        "driver": "Tariq Mansour",
        "lat": 33.4795,
        "lon": -112.0735,
        "target_lat": 33.5102,
        "target_lon": -112.0728,
        "active_corridor": "Route A (Central Urban Core)",
        "ambient_road_temp_f": 111.5,
        "pack_internal_temp_f": 107.8,
        "soc_pct": 68,
        "speed_mph": 22,
        "packages_remaining": 31,
        "status": "CRITICAL EXPOSURE",
        "reroute_available": True,
        "recommended_reroute": "Divert East to 7th St Tree Canopy corridor"
    }
]


def get_live_telematics_stream() -> list:
    """
    Returns active vehicle telematics with real-time sensor parameters.
    """
    return [v.copy() for v in ACTIVE_FLEET_VEHICLES]


def trigger_dynamic_reroute(vehicle_id: str) -> dict:
    """
    Executes autonomous corridor diversion for a targeted fleet vehicle.
    """
    for v in ACTIVE_FLEET_VEHICLES:
        if v["id"] == vehicle_id:
            v["active_corridor"] = "Route C (Highway Bypass - Diverted)"
            v["ambient_road_temp_f"] = 96.0
            v["pack_internal_temp_f"] = 91.5
            v["status"] = "REROUTED // OPTIMIZED"
            v["reroute_available"] = False
            v["recommended_reroute"] = "Active on optimized thermal corridor"
            return {
                "success": True,
                "vehicle_id": vehicle_id,
                "new_corridor": v["active_corridor"],
                "projected_temp_reduction_f": 17.8,
                "projected_pack_lifespan_extension_years": 1.9,
                "timestamp": datetime.now().strftime("%H:%M:%S UTC")
            }
    return {"success": False, "error": "Vehicle ID not found"}
