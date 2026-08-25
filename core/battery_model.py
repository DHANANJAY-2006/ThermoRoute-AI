"""
Battery Degradation Model — Arrhenius Kinetics
===============================================
The electrochemical kinetics model of ThermoRoute AI.

Based on the Arrhenius relationship modeling lithium-ion battery capacity loss
and SEI layer growth as a function of temperature and operating stress.

Electrochemical Relationship:
  Degradation Rate Multiplier = 2 ^ ((T_effective - 77°F) / 18°F)
  At 112°F (Phoenix ambient roadway): 3.85x degradation rate vs 77°F baseline.
"""

import math
import json
import os


def _load_ev_specs() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "ev_specs.json")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


EV_SPECS = _load_ev_specs()

# Temperature parameters
BASELINE_TEMP_F = 77.0     # 25°C — Li-ion optimal operating temperature
DOUBLING_INTERVAL_F = 18.0  # Every 18°F (10°C) above baseline doubles aging rate
SOLAR_LOAD_FACTOR = 0.008   # Solar irradiance absorption coefficient


class BatteryDegradationModel:
    """
    Calculates electrochemical degradation multipliers and capital depreciation costs.
    """

    def degradation_factor(self, temp_f: float,
                            solar_irradiance_wm2: float = 0) -> float:
        """
        Arrhenius degradation multiplier.
        """
        solar_temp_add = (solar_irradiance_wm2 / 100) * SOLAR_LOAD_FACTOR * 100
        effective_temp = temp_f + solar_temp_add
        temp_above = max(0.0, effective_temp - BASELINE_TEMP_F)
        return round(2 ** (temp_above / DOUBLING_INTERVAL_F), 3)

    def annual_degradation_cost(self, avg_temp_f: float,
                                 vehicle_key: str,
                                 solar_irradiance_wm2: float = 0,
                                 daily_drive_hours: float = 8.0) -> dict:
        """
        Calculates annual depreciation in replacement cost.
        """
        specs = EV_SPECS.get(vehicle_key, list(EV_SPECS.values())[0])
        replacement_cost = specs["battery_replacement_cost_usd"]
        lifespan_years = specs["nominal_cycle_life_years"]

        factor = self.degradation_factor(avg_temp_f, solar_irradiance_wm2)
        baseline_factor = self.degradation_factor(BASELINE_TEMP_F)

        baseline_annual = replacement_cost / lifespan_years
        heat_annual = baseline_annual * factor
        extra_annual = heat_annual - baseline_annual
        effective_lifespan = lifespan_years / factor

        return {
            "vehicle": specs["name"],
            "avg_temp_f": avg_temp_f,
            "degradation_factor": factor,
            "baseline_factor": round(baseline_factor, 3),
            "extra_multiplier": round(factor / baseline_factor, 2),
            "battery_replacement_cost": replacement_cost,
            "nominal_lifespan_years": lifespan_years,
            "effective_lifespan_years": round(effective_lifespan, 1),
            "baseline_annual_cost_usd": round(baseline_annual, 2),
            "heat_annual_cost_usd": round(heat_annual, 2),
            "extra_annual_cost_usd": round(extra_annual, 2),
            "solar_irradiance_wm2": solar_irradiance_wm2,
            "solar_temp_addition_f": round(
                (solar_irradiance_wm2 / 100) * SOLAR_LOAD_FACTOR * 100, 1
            )
        }

    def compare_routes(self, routes: list, vehicle_key: str,
                       solar_irradiance_wm2: float = 0) -> dict:
        """
        Evaluates and ranks candidate corridors by annual battery degradation cost.
        Preserves all routing, spatial, and telemetry metadata.
        """
        results = []
        for route in routes:
            temp = route["avg_temp_f"]
            shade = route.get("shade_pct", 0)
            shade_reduction = (shade / 100) * 8.0
            effective_temp = temp - shade_reduction

            cost_data = self.annual_degradation_cost(
                effective_temp, vehicle_key, solar_irradiance_wm2
            )
            results.append({
                "name": route["name"],
                "route_name": route["name"],
                "route_key": route.get("key", route["name"]),
                "description": route.get("description", ""),
                "avg_temp_f": round(temp, 1),
                "effective_temp_f": round(effective_temp, 1),
                "shade_pct": shade,
                "distance_miles": route.get("distance_miles", 0),
                "duration_minutes": route.get("duration_minutes", 0),
                "waypoints": route.get("waypoints", []),
                "segment_temps": route.get("segment_temps", []),
                "color": route.get("color", "#38bdf8"),
                "degradation_factor": cost_data["degradation_factor"],
                "annual_cost_usd": cost_data["heat_annual_cost_usd"],
                "extra_cost_usd": cost_data["extra_annual_cost_usd"],
                "effective_lifespan_years": cost_data["effective_lifespan_years"],
                "risk_level": self._risk_level(temp)
            })

        results.sort(key=lambda x: x["annual_cost_usd"])
        recommended = results[0]
        worst = results[-1]
        savings_per_van = max(0.0, worst["annual_cost_usd"] - recommended["annual_cost_usd"])

        return {
            "routes": results,
            "recommended_route": recommended["name"],
            "savings_per_van_usd": round(savings_per_van, 2),
            "savings_pct": round(
                savings_per_van / worst["annual_cost_usd"] * 100, 1
            ) if worst["annual_cost_usd"] > 0 else 0.0,
        }

    def fleet_savings(self, savings_per_van: float, fleet_size: int) -> dict:
        annual_fleet = savings_per_van * fleet_size
        return {
            "fleet_size": fleet_size,
            "savings_per_van_usd": round(savings_per_van, 2),
            "annual_fleet_savings_usd": round(annual_fleet, 2),
            "monthly_fleet_savings_usd": round(annual_fleet / 12, 2),
            "five_year_savings_usd": round(annual_fleet * 5, 2),
        }

    def _risk_level(self, temp_f: float) -> str:
        if temp_f >= 110:
            return "CRITICAL"
        elif temp_f >= 100:
            return "ELEVATED"
        elif temp_f >= 90:
            return "MODERATE"
        else:
            return "NOMINAL"

    def risk_color(self, temp_f: float) -> str:
        if temp_f >= 110:
            return "#ef4444"
        elif temp_f >= 100:
            return "#f97316"
        elif temp_f >= 90:
            return "#eab308"
        else:
            return "#22c55e"
