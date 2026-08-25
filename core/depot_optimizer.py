"""
Smart Depot Charging & Thermal Pre-Conditioning Optimizer
==========================================================
Optimizes overnight commercial fleet charging windows against FortyGuard 12-hour
temperature forecasts and Time-of-Use (TOU) utility electricity pricing.
"""

import math
from datetime import datetime, timedelta


def optimize_depot_charging(forecast_temps: list,
                            fleet_size: int = 500,
                            battery_kwh: float = 135.0,
                            daily_kwh_needed: float = 85.0,
                            depot_power_kw_per_stall: float = 22.0) -> dict:
    """
    Computes optimal charging profile across the 12-hour depot staging window.
    """
    now = datetime.now()
    schedule = []
    
    # 12-hour forward intervals
    # Off-peak TOU tariff: $0.08/kWh (00:00 - 06:00), Peak: $0.24/kWh (16:00 - 21:00), Shoulder: $0.14/kWh
    unoptimized_total_cost = 0.0
    optimized_total_cost = 0.0
    
    # Required charging duration in hours
    charge_hours_needed = max(1.0, daily_kwh_needed / depot_power_kw_per_stall)
    
    # Rank hours by combined thermal stress (FortyGuard temp) + electricity tariff
    ranked_hours = []
    for i, temp in enumerate(forecast_temps[:12]):
        hour_time = now + timedelta(hours=i)
        hour_num = hour_time.hour
        
        # Determine TOU tariff
        if 0 <= hour_num <= 6:
            tariff = 0.08
            tariff_tier = "OFF-PEAK"
        elif 16 <= hour_num <= 21:
            tariff = 0.24
            tariff_tier = "PEAK"
        else:
            tariff = 0.14
            tariff_tier = "SHOULDER"

        # Thermal stress penalty factor
        thermal_penalty = (temp / 100.0) ** 2.0
        combined_score = tariff * thermal_penalty

        ranked_hours.append({
            "index": i,
            "hour_label": hour_time.strftime("%H:00"),
            "temp_f": temp,
            "tariff": tariff,
            "tariff_tier": tariff_tier,
            "score": combined_score
        })

    # Sort hours to find optimal charge window
    ranked_hours_sorted = sorted(ranked_hours, key=lambda x: x["score"])
    optimal_indices = set(x["index"] for x in ranked_hours_sorted[:int(math.ceil(charge_hours_needed))])

    for r in ranked_hours:
        idx = r["index"]
        is_charging = idx in optimal_indices
        
        # Thermal pre-conditioning (1 hour before departure in coolest window)
        is_preconditioning = (idx == ranked_hours_sorted[0]["index"])
        
        charge_draw_kw = depot_power_kw_per_stall if is_charging else 0.0
        hourly_energy_kwh = charge_draw_kw * 1.0
        hourly_cost_per_unit = hourly_energy_kwh * r["tariff"]
        
        schedule.append({
            "hour": r["hour_label"],
            "temp_f": r["temp_f"],
            "tariff_per_kwh": r["tariff"],
            "tariff_tier": r["tariff_tier"],
            "charge_power_kw": charge_draw_kw,
            "is_preconditioning": is_preconditioning,
            "status": "ACTIVE CHARGE" if is_charging else ("PRE-CONDITION" if is_preconditioning else "IDLE / STAGED")
        })

        if is_charging:
            optimized_total_cost += hourly_cost_per_unit

    # Baseline unoptimized charging (charges immediately upon arrival during hot evening peak)
    unoptimized_hours = ranked_hours[:int(math.ceil(charge_hours_needed))]
    for u in unoptimized_hours:
        unoptimized_total_cost += depot_power_kw_per_stall * u["tariff"]

    annual_depot_savings_per_van = max(0.0, (unoptimized_total_cost - optimized_total_cost) * 365.0)
    annual_depot_fleet_savings = annual_depot_savings_per_van * fleet_size

    return {
        "schedule": schedule,
        "daily_cost_per_unit_unoptimized": round(unoptimized_total_cost, 2),
        "daily_cost_per_unit_optimized": round(optimized_total_cost, 2),
        "annual_depot_savings_per_van_usd": round(annual_depot_savings_per_van, 2),
        "annual_depot_fleet_savings_usd": round(annual_depot_fleet_savings, 2),
        "coolest_charge_window": ranked_hours_sorted[0]["hour_label"],
        "hottest_avoided_window": sorted(ranked_hours, key=lambda x: x["temp_f"], reverse=True)[0]["hour_label"]
    }
