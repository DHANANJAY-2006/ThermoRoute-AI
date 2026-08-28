"""
EV Energy Model — Thermal Operational Cost Engine
===================================================
Computes temperature-dependent energy consumption penalties and range
reduction costs for commercial EV delivery fleets.

Two cost components beyond Arrhenius degradation:

  1. Energy Efficiency Penalty
     Heat forces heavier AC load and increases battery internal resistance,
     raising kWh/mile consumption above the manufacturer rated baseline.
     Coefficient: 0.25% additional kWh/mile per °F above 77°F baseline.
     AC peak load differential: up to 8.5 kWh/day at 111°F vs baseline.

  2. Operational Range Overhead
     Thermal degradation reduces effective single-charge range.
     Reduced range = more depot returns, mid-route top-ups, and driver
     scheduling overhead. Coefficient: 0.35% range reduction per °F above baseline.

References:
  - NREL Fleet DNA Commercial Vehicle Operational Data Study (2023)
  - DOE Alternative Fuels Center EV Range Impact Assessment
  - SAE J3072 Commercial EV Thermal Performance Standard
"""

import math
import json
import os


def _load_specs() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "ev_specs.json")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


EV_SPECS = _load_specs()

# Operational constants
BASELINE_TEMP_F           = 77.0    # Manufacturer rated performance baseline
OPERATING_DAYS_PER_YEAR   = 260     # 5 days/week × 52 weeks
ELECTRICITY_RATE_USD_KWH  = 0.14    # US commercial fleet average (EIA 2024)
DRIVER_RATE_USD_HR        = 22.0    # US delivery driver avg (BLS 2024)
DAILY_OPERATIONAL_MILES   = 85.0    # Commercial urban delivery van avg (NREL Fleet DNA)

# Energy penalty coefficients
ENERGY_PENALTY_PCT_PER_F          = 0.0025   # 0.25% per °F — battery resistance + motor loss
AC_EXTREME_HEAT_DAILY_KWH         = 8.5      # Extra AC draw at 111°F+ (4.5kW × 4.5h drive day)
AC_MODERATE_HEAT_DAILY_KWH        = 2.8      # Extra AC draw at 85–105°F range

# Range overhead coefficients
RANGE_REDUCTION_PCT_PER_F         = 0.35     # 0.35% per °F above baseline (DOE validated)
OVERHEAD_COST_PER_PCT_REDUCTION   = 30.0     # $30/yr per 1% range loss (labor + charging infra)


class EVEnergyModel:
    """
    Computes annual energy surcharge and range overhead cost per vehicle
    as a function of ambient roadway temperature and chassis specification.
    """

    def energy_penalty_annual(
        self,
        temp_f: float,
        vehicle_key: str,
        daily_miles: float = DAILY_OPERATIONAL_MILES,
        electricity_rate: float = ELECTRICITY_RATE_USD_KWH
    ) -> dict:
        """
        Annual energy cost above baseline caused by heat-driven kWh/mile increase.
        Includes both efficiency degradation (battery internal resistance) and
        increased AC thermal load.
        """
        specs = EV_SPECS.get(vehicle_key, list(EV_SPECS.values())[0])
        base_kwh_per_mile = specs.get("base_kwh_per_mile", 0.88)

        temp_delta = max(0.0, temp_f - BASELINE_TEMP_F)

        # Efficiency component: extra kWh/mile from battery resistance at heat
        efficiency_penalty_pct = temp_delta * ENERGY_PENALTY_PCT_PER_F
        extra_kwh_per_mile = base_kwh_per_mile * efficiency_penalty_pct
        annual_efficiency_kwh = extra_kwh_per_mile * daily_miles * OPERATING_DAYS_PER_YEAR

        # AC thermal load component: scales linearly with heat band
        if temp_f >= 105.0:
            daily_ac_extra_kwh = AC_EXTREME_HEAT_DAILY_KWH * (temp_delta / 34.0)
        elif temp_f >= 85.0:
            daily_ac_extra_kwh = AC_MODERATE_HEAT_DAILY_KWH * (temp_delta / 20.0)
        else:
            daily_ac_extra_kwh = 0.0
        annual_ac_kwh = daily_ac_extra_kwh * OPERATING_DAYS_PER_YEAR

        total_extra_kwh = annual_efficiency_kwh + annual_ac_kwh
        annual_energy_cost = total_extra_kwh * electricity_rate

        return {
            "base_kwh_per_mile": base_kwh_per_mile,
            "efficiency_penalty_pct": round(efficiency_penalty_pct * 100, 2),
            "extra_kwh_per_mile": round(extra_kwh_per_mile, 4),
            "annual_ac_extra_kwh": round(annual_ac_kwh, 1),
            "total_extra_annual_kwh": round(total_extra_kwh, 1),
            "annual_energy_penalty_usd": round(annual_energy_cost, 2),
        }

    def range_overhead_annual(self, temp_f: float, vehicle_key: str) -> dict:
        """
        Annual operational overhead cost from heat-induced EV range reduction.
        Covers mid-route charging time, depot return overhead, and scheduling inefficiency.
        """
        specs = EV_SPECS.get(vehicle_key, list(EV_SPECS.values())[0])
        rated_range = specs.get("rated_range_miles", 150)

        temp_delta = max(0.0, temp_f - BASELINE_TEMP_F)
        range_reduction_pct = temp_delta * RANGE_REDUCTION_PCT_PER_F
        effective_range = max(10.0, rated_range * (1.0 - range_reduction_pct / 100.0))

        annual_overhead = range_reduction_pct * OVERHEAD_COST_PER_PCT_REDUCTION

        return {
            "rated_range_miles": rated_range,
            "range_reduction_pct": round(range_reduction_pct, 1),
            "effective_range_miles": round(effective_range, 1),
            "annual_range_overhead_usd": round(annual_overhead, 2),
        }

    def total_operational_cost_annual(
        self,
        temp_f: float,
        vehicle_key: str,
        daily_miles: float = DAILY_OPERATIONAL_MILES,
        electricity_rate: float = ELECTRICITY_RATE_USD_KWH
    ) -> dict:
        """
        Full 2-component operational penalty: energy + range overhead.
        Combines into a single annual cost figure per vehicle.
        """
        energy = self.energy_penalty_annual(temp_f, vehicle_key, daily_miles, electricity_rate)
        range_oh = self.range_overhead_annual(temp_f, vehicle_key)

        total = energy["annual_energy_penalty_usd"] + range_oh["annual_range_overhead_usd"]

        return {
            **energy,
            **range_oh,
            "annual_operational_penalty_usd": round(total, 2),
        }
