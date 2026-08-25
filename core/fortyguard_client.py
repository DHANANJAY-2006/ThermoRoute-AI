"""
FortyGuard Temperature API Client
===================================
Wraps all 6 FortyGuard Temperature API endpoints.
Implements the mandatory async submit-and-poll pattern.

KEY RULES (from hackathon docs):
- API is ASYNC: submit task → get activity_id → poll /v1/status/{id}
- US locations ONLY — non-US returns no data
- Data: Jan 1 2021 → present + 12hr forecast max
- Analysis layers: "snapshot" | "exceedance" | "persistence"
- Failed calls = 0 credits consumed
"""

import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# Demo data — used when DEMO_MODE=true or API key missing
# Simulates realistic FortyGuard API responses
# ─────────────────────────────────────────────
DEMO_HEATMAP = {
    "status": "completed",
    "result": {
        "location": "Phoenix, AZ",
        "analysis_layer": "exceedance",
        "temperature_f": 112.0,
        "risk_level": "extreme",
        "exceedance_pct": 78.4,
        "resolution": "10mi²",
        "measured_at": "2m above ground",
        "geojson": {
            "type": "FeatureCollection",
            "features": []
        }
    }
}

DEMO_ENV_PARAMS = {
    "status": "completed",
    "result": {
        "location": "Phoenix, AZ",
        "heat_index_f": 118.0,
        "solar_irradiance_wm2": 950.0,
        "aqi": 42,
        "humidity_pct": 14.0,
        "wind_speed_mph": 8.2,
        "analysis_layer": "persistence",
        "persistence_hours": 9.3
    }
}

DEMO_SATELLITE = {
    "status": "completed",
    "result": {
        "location": "Phoenix, AZ",
        "vegetation_pct": 8.2,
        "building_pct": 43.1,
        "pavement_pct": 38.7,
        "water_pct": 0.4,
        "other_pct": 9.6,
        "green_shield_score": 16.4
    }
}

DEMO_STREETVIEW = {
    "status": "completed",
    "result": {
        "location": "Phoenix, AZ",
        "ground_temp_f": 114.2,
        "surface_type": "asphalt",
        "shade_coverage_pct": 8.0,
        "image_url": None
    }
}

DEMO_HEAT_INTELLIGENCE = {
    "status": "completed",
    "result": {
        "location": "Phoenix, AZ",
        "report_type": "multi_dimensional",
        "geographic_risk": "extreme",
        "environmental_risk": "extreme",
        "urban_risk": "critical",
        "overall_risk_score": 94.2,
        "pdf_url": None,
        "summary": (
            "Phoenix, AZ presents critical thermal conditions for fleet operations. "
            "Ambient temperature of 112°F combined with 8% vegetation coverage and "
            "high solar irradiance creates a high-risk environment for EV battery degradation. "
            "Immediate route optimization recommended to reduce battery thermal stress."
        )
    }
}


class FortyGuardClient:
    """
    FortyGuard Temperature API client.
    Supports both live API mode and demo mode.
    """

    BASE_URL = "https://api.fortyguard.com"
    POLL_INTERVAL_S = 5
    MAX_POLL_ATTEMPTS = 72   # 6 minutes max

    def __init__(self):
        self.api_key = os.getenv("FORTYGUARD_API_KEY", "")
        demo_env = os.getenv("DEMO_MODE", "true").lower()
        self.demo_mode = demo_env == "true" or not self.api_key or self.api_key == "your_api_key_here"

        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    # ── Internal helpers ──────────────────────────────────────

    def _submit(self, endpoint: str, payload: dict) -> str:
        """POST to endpoint, return activity_id."""
        resp = requests.post(
            f"{self.BASE_URL}{endpoint}",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()["activity_id"]

    def _poll(self, activity_id: str) -> dict:
        """
        Poll GET /v1/status/{activity_id} until completed or failed.
        Only successful tasks consume credits — failed = 0 credits.
        """
        for _ in range(self.MAX_POLL_ATTEMPTS):
            resp = requests.get(
                f"{self.BASE_URL}/v1/status/{activity_id}",
                headers=self.headers,
                timeout=15
            )
            data = resp.json()
            status = data.get("status")

            if status == "completed":
                return data.get("result", data)
            elif status == "failed":
                raise RuntimeError(f"FortyGuard task failed: {data.get('error', 'unknown')}")

            time.sleep(self.POLL_INTERVAL_S)

        raise TimeoutError("FortyGuard task timed out after 6 minutes")

    def _run(self, endpoint: str, payload: dict) -> dict:
        """Submit + poll pattern wrapper."""
        activity_id = self._submit(endpoint, payload)
        return self._poll(activity_id)

    # ── Endpoint 1: Heatmap ───────────────────────────────────

    def get_heatmap(self, location: str, analysis_layer: str = "exceedance",
                    timestamp: str = "now") -> dict:
        """
        POST /v1/heatmap
        Returns high-resolution GeoJSON thermal map for the area.

        analysis_layer options:
          "snapshot"   — temperature at a single moment (use for current conditions)
          "exceedance" — % of time above threshold (use for cost/risk calculations)
          "persistence"— sustained heat periods (use for heatwave/battery stress)

        US-only. Forecast max 12 hours ahead.
        """
        if self.demo_mode:
            result = DEMO_HEATMAP["result"].copy()
            result["location"] = location
            result["analysis_layer"] = analysis_layer
            return result

        return self._run("/v1/heatmap", {
            "location": location,
            "analysis_layer": analysis_layer,
            "timestamp": timestamp
        })

    def get_route_segment_temps(self, waypoints: list,
                                analysis_layer: str = "exceedance") -> list:
        """
        Query heatmap for each waypoint along a route.
        Returns list of temperatures per segment.
        US-only locations required.
        """
        temps = []
        for wp in waypoints:
            location = f"{wp['lat']},{wp['lon']}"
            result = self.get_heatmap(location, analysis_layer)

            # In demo mode, add slight variation per waypoint
            if self.demo_mode:
                import random
                base_temp = result.get("temperature_f", 110)
                temp = base_temp + random.uniform(-4, 4)
                temps.append(round(temp, 1))
            else:
                temps.append(result.get("temperature_f", 100))

        return temps

    # ── Endpoint 2: Satellite ─────────────────────────────────

    def get_satellite(self, location: str) -> dict:
        """
        POST /v1/satellite
        Returns per-class coverage: vegetation %, building %, pavement %.
        Used for: Vegetation Shield Score (more vegetation = cooler route).
        """
        if self.demo_mode:
            result = DEMO_SATELLITE["result"].copy()
            result["location"] = location
            return result

        return self._run("/v1/satellite", {"location": location})

    # ── Endpoint 3: Streetview ────────────────────────────────

    def get_streetview(self, location: str) -> dict:
        """
        POST /v1/streetview
        Returns ground-level street view segmentation analysis.
        Used for: Visualising hot vs cool road segments at ground level.
        """
        if self.demo_mode:
            result = DEMO_STREETVIEW["result"].copy()
            result["location"] = location
            return result

        return self._run("/v1/streetview", {"location": location})

    # ── Endpoint 4: Heat Intelligence ────────────────────────

    def get_heat_intelligence(self, location: str) -> dict:
        """
        POST /v1/heat_intelligence
        Returns multi-dimensional report (Geographic, Environmental, Urban).
        Used for: Auto-generated executive fleet thermal risk report.
        """
        if self.demo_mode:
            result = DEMO_HEAT_INTELLIGENCE["result"].copy()
            result["location"] = location
            return result

        return self._run("/v1/heat_intelligence", {"location": location})

    # ── Endpoint 5: Environmental Parameters ─────────────────

    def get_env_params(self, location: str,
                       analysis_layer: str = "persistence") -> dict:
        """
        POST /v1/env_params
        Returns: heat index, AQI, solar irradiance, humidity, wind.
        Used for: Solar load on battery case + effective battery temperature.
        analysis_layer = "persistence" to capture sustained heat periods.
        """
        if self.demo_mode:
            result = DEMO_ENV_PARAMS["result"].copy()
            result["location"] = location
            result["analysis_layer"] = analysis_layer
            return result

        return self._run("/v1/env_params", {
            "location": location,
            "analysis_layer": analysis_layer
        })

    # ── Endpoint 6: Status (used internally by _poll) ─────────
    # GET /v1/status/{activity_id} — used in _poll() above

    # ── System: Credit Usage ──────────────────────────────────

    def get_credit_usage(self) -> dict:
        """
        POST /v1/system/fetch-api-key-usage
        Monitor API credit consumption responsibly.
        """
        if self.demo_mode:
            return {"credits_used": 0, "credits_remaining": 999999, "demo_mode": True}

        resp = requests.post(
            f"{self.BASE_URL}/v1/system/fetch-api-key-usage",
            headers=self.headers,
            timeout=15
        )
        return resp.json()

    # ── Forecast (12-hour max) ────────────────────────────────

    def get_forecast(self, location: str, hours_ahead: int = 12) -> list:
        """
        Get temperature forecast — MAX 12 HOURS AHEAD ONLY.
        API rejects anything beyond 12 hours.
        Used for: Workload planning and proactive rerouting.
        """
        if hours_ahead > 12:
            raise ValueError(
                f"FortyGuard API only supports forecasts up to 12 hours ahead. "
                f"Requested {hours_ahead} hours."
            )

        if self.demo_mode:
            import math
            base = 112.0
            hours = list(range(hours_ahead))
            # Realistic diurnal curve (peaks around hour 3-4 = 3PM)
            return [
                round(base + 4 * math.sin((h - 2) * math.pi / 6) - h * 0.5, 1)
                for h in hours
            ]

        return self._run("/v1/heatmap", {
            "location": location,
            "forecast_hours": hours_ahead,
            "analysis_layer": "snapshot"
        })

    @property
    def mode(self) -> str:
        return "[Demo Mode]" if self.demo_mode else "[Live API]"
