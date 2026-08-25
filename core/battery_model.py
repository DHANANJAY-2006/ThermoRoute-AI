"""
Battery Degradation Model — Arrhenius Kinetics
===============================================
The core invention of ThermoRoute AI.

Based on the Arrhenius equation used by EV manufacturers (Tesla, GM, Rivian)
to model lithium-ion battery degradation as a function of temperature.

Key insight:
  Every 10°C (18°F) above 25°C (77°F) → battery degrades 2× faster
  At Phoenix 112°F = 44.4°C → degrades 3.78× faster than at 77°F baseline

Sources:
  - Arrhenius, S. (1889) kinetics equation (public domain science)
  - Published Li-ion degradation research (Wang et al., 2011; Vetter et al., 2005)
  - Industry rule of thumb: Ea ≈ 0.6 eV for LFP/NMC chemistry
"""

import math
import json
import os


def _load_ev_specs() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "ev_specs.json")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


EV_SPECS = _load_ev_specs()

# Temperature constants
BASELINE_TEMP_F = 77.0     # 25°C — Li-ion optimal temperature
DOUBLING_INTERVAL_F = 18.0  # Every 18°F above baseline → 2× degradation rate
SOLAR_LOAD_FACTOR = 0.008   # Each 100 W/m² of irradiance adds ~0.8°F effective battery temp


class BatteryDegradationModel:
    """
    Calculates battery degradation rate and annual cost
    based on FortyGuard temperature data.
    """

    def degradation_factor(self, temp_f: float,
                            solar_irradiance_wm2: float = 0) -> float:
        """
        Arrhenius-simplified degradation multiplier.

        Formula: factor = 2 ^ ((effective_temp - baseline) / doubling_interval)

        Solar irradiance adds to effective battery temperature
        (direct sun heats the battery case beyond ambient air temp).

        Returns:
          1.0  = baseline (no extra degradation, 77°F)
          2.0  = 2× faster (95°F)
          3.78 = 3.78× faster (112°F Phoenix)
          7.13 = 7× faster (130°F extreme)
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
        Translate temperature → annual dollar cost of battery degradation.

        Returns full breakdown dict.
        """
        specs = EV_SPECS[vehicle_key]
        replacement_cost = specs["battery_replacement_cost_usd"]
        lifespan_years = specs["nominal_cycle_life_years"]

        factor = self.degradation_factor(avg_temp_f, solar_irradiance_wm2)
        baseline_factor = self.degradation_factor(BASELINE_TEMP_F)

        # Baseline annual cost (what you'd pay in ideal conditions)
        baseline_annual = replacement_cost / lifespan_years

        # Heat-adjusted annual cost
        heat_annual = baseline_annual * factor

        # Extra cost due to heat
        extra_annual = heat_annual - baseline_annual

        # Effective battery lifespan under heat
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
        Compare multiple routes by annual battery degradation cost.

        routes: list of dicts with keys: name, avg_temp_f, distance_miles, shade_pct
        Returns recommended route + savings vs worst route.
        """
        results = []
        for route in routes:
            temp = route["avg_temp_f"]
            shade = route.get("shade_pct", 0)
            # Shaded roads are effectively cooler — apply shade reduction
            shade_reduction = (shade / 100) * 8.0  # max 8°F reduction at 100% shade
            effective_temp = temp - shade_reduction

            cost_data = self.annual_degradation_cost(
                effective_temp, vehicle_key, solar_irradiance_wm2
            )
            results.append({
                "route_name": route["name"],
                "route_key": route.get("key", route["name"]),
                "avg_temp_f": temp,
                "effective_temp_f": round(effective_temp, 1),
                "shade_pct": shade,
                "distance_miles": route.get("distance_miles", 0),
                "degradation_factor": cost_data["degradation_factor"],
                "annual_cost_usd": cost_data["heat_annual_cost_usd"],
                "extra_cost_usd": cost_data["extra_annual_cost_usd"],
                "effective_lifespan_years": cost_data["effective_lifespan_years"],
                "risk_level": self._risk_level(temp)
            })

        results.sort(key=lambda x: x["annual_cost_usd"])
        recommended = results[0]
        worst = results[-1]
        savings_per_van = worst["annual_cost_usd"] - recommended["annual_cost_usd"]

        return {
            "routes": results,
            "recommended_route": recommended["route_name"],
            "savings_per_van_usd": round(savings_per_van, 2),
            "savings_pct": round(
                savings_per_van / worst["annual_cost_usd"] * 100, 1
            ) if worst["annual_cost_usd"] > 0 else 0,
        }

    def fleet_savings(self, savings_per_van: float, fleet_size: int) -> dict:
        """Scale per-van savings to full fleet."""
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
            return "🔴 Critical"
        elif temp_f >= 100:
            return "🟠 High"
        elif temp_f >= 90:
            return "🟡 Moderate"
        else:
            return "🟢 Low"

    def risk_color(self, temp_f: float) -> str:
        if temp_f >= 110:
            return "#ef4444"
        elif temp_f >= 100:
            return "#f97316"
        elif temp_f >= 90:
            return "#eab308"
        else:
            return "#22c55e"
