"""
Battery Degradation Model — Arrhenius Kinetics
===============================================
Electrochemical kinetics model computing lithium-ion capacity loss
and SEI layer growth as a function of thermal exposure and operating parameters.

Governing Relationship:
  k(T) / k(T0) = exp( (Ea / R) * (1/T0 - 1/T) )

Where:
  Ea = 52.5 kJ/mol (Activation energy for commercial Li-ion SEI degradation)
  R  = 8.314 J/(mol*K) (Universal gas constant)
  T0 = 298.15 K (25°C / 77.0°F baseline)
  T  = Effective pack microclimate temperature in Kelvin
"""

import math
import json
import os


def _load_ev_specs() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "ev_specs.json")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


EV_SPECS = _load_ev_specs()

# Thermodynamic constants
BASELINE_TEMP_F = 77.0
ACTIVATION_ENERGY_J_MOL = 52500.0  # 52.5 kJ/mol
GAS_CONSTANT_R = 8.314             # J/(mol*K)
T0_KELVIN = 298.15                 # 25°C baseline


class BatteryDegradationModel:
    """
    Computes cell degradation multipliers and annualized replacement depreciation.
    """

    def degradation_factor(self, *args, **kwargs) -> float:
        """
        Computes the Arrhenius reaction rate multiplier k(T)/k(T0).
        Zero-TypeError signature with universal *args and **kwargs parsing.
        """
        temp_f = 77.0
        solar_irradiance_wm2 = 0.0
        shade_pct = 0.0

        if len(args) >= 1:
            temp_f = args[0]
        if len(args) >= 2:
            solar_irradiance_wm2 = args[1]
        if len(args) >= 3:
            shade_pct = args[2]

        temp_f = float(kwargs.get("temp_f", kwargs.get("avg_temp_f", temp_f)))
        solar = float(kwargs.get("solar_irradiance_wm2", kwargs.get("solar", kwargs.get("solar_wm2", solar_irradiance_wm2))))
        shade = float(kwargs.get("shade_pct", kwargs.get("shade", shade_pct)))

        solar_add = (solar / 1000.0) * 5.5
        shade_sub = (shade / 100.0) * 8.5
        effective_temp_f = temp_f + solar_add - shade_sub

        t_eff_k = (effective_temp_f - 32.0) * (5.0 / 9.0) + 273.15
        if t_eff_k <= T0_KELVIN:
            return 1.0

        multiplier = math.exp(
            (ACTIVATION_ENERGY_J_MOL / GAS_CONSTANT_R) *
            ((1.0 / T0_KELVIN) - (1.0 / t_eff_k))
        )
        return round(multiplier, 3)

    def annual_degradation_cost(self, *args, **kwargs) -> dict:
        """
        Computes annualized battery asset depreciation under thermal stress.
        Zero-TypeError signature with universal *args and **kwargs parsing.
        """
        avg_temp_f = 100.0
        vehicle_key = "Rivian_EDV_500"
        solar_irradiance_wm2 = 0.0
        shade_pct = 0.0
        daily_drive_hours = 8.0

        if len(args) >= 1:
            avg_temp_f = args[0]
        if len(args) >= 2:
            vehicle_key = args[1]
        if len(args) >= 3:
            solar_irradiance_wm2 = args[2]
        if len(args) >= 4:
            shade_pct = args[3]
        if len(args) >= 5:
            daily_drive_hours = args[4]

        avg_temp_f = float(kwargs.get("avg_temp_f", kwargs.get("temp_f", avg_temp_f)))
        vehicle_key = str(kwargs.get("vehicle_key", kwargs.get("vehicle", vehicle_key)))
        solar = float(kwargs.get("solar_irradiance_wm2", kwargs.get("solar", kwargs.get("solar_wm2", solar_irradiance_wm2))))
        shade = float(kwargs.get("shade_pct", kwargs.get("shade", shade_pct)))

        specs = EV_SPECS.get(vehicle_key, list(EV_SPECS.values())[0])
        replacement_cost = specs.get("battery_replacement_cost_usd", 28000)
        lifespan_years = specs.get("nominal_cycle_life_years", 8)

        solar_add = (solar / 1000.0) * 5.5
        shade_sub = (shade / 100.0) * 8.5
        effective_temp_f = avg_temp_f + solar_add - shade_sub

        factor = self.degradation_factor(avg_temp_f, solar, shade)
        baseline_annual = replacement_cost / lifespan_years

        effective_lifespan = max(0.5, lifespan_years / factor)
        heat_annual = replacement_cost / effective_lifespan
        extra_annual = max(0.0, heat_annual - baseline_annual)

        return {
            "vehicle": specs.get("name", vehicle_key),
            "avg_temp_f": round(avg_temp_f, 1),
            "effective_temp_f": round(effective_temp_f, 1),
            "degradation_factor": factor,
            "baseline_factor": 1.000,
            "extra_multiplier": round(factor, 2),
            "battery_replacement_cost": replacement_cost,
            "nominal_lifespan_years": lifespan_years,
            "effective_lifespan_years": round(effective_lifespan, 1),
            "baseline_annual_cost_usd": round(baseline_annual, 2),
            "heat_annual_cost_usd": round(heat_annual, 2),
            "extra_annual_cost_usd": round(extra_annual, 2),
            "solar_irradiance_wm2": solar,
            "solar_temp_addition_f": round(solar_add, 1),
            "shade_temp_reduction_f": round(shade_sub, 1)
        }

    def compare_routes(self, routes: list, vehicle_key: str = "Rivian_EDV_500",
                       solar_irradiance_wm2: float = 0,
                       *args, **kwargs) -> dict:
        """
        Evaluates candidate corridors and computes comparative savings.
        """
        results = []
        for route in routes:
            temp = float(route.get("avg_temp_f", 100.0))
            shade = float(route.get("shade_pct", 0.0))
            route_solar = float(route.get("solar_irradiance", solar_irradiance_wm2))

            cost_data = self.annual_degradation_cost(
                temp, vehicle_key, route_solar, shade
            )
            results.append({
                "name": route.get("name", "Route"),
                "route_name": route.get("name", "Route"),
                "route_key": route.get("key", route.get("name", "Route")),
                "description": route.get("description", ""),
                "avg_temp_f": round(temp, 1),
                "effective_temp_f": cost_data["effective_temp_f"],
                "shade_pct": shade,
                "solar_irradiance": route_solar,
                "distance_miles": route.get("distance_miles", 0.0),
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
                (savings_per_van / worst["annual_cost_usd"]) * 100.0, 1
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
