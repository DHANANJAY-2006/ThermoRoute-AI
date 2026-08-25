"""
Cost Calculator — Fleet Financial Modeling
==========================================
Computes annual battery replacement cost deltas, net financial ROI,
and multi-year cumulative fleet return based on Arrhenius cell kinetics.
"""

import json
import os


def _load_prices() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "electricity_prices.json")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


ELECTRICITY = _load_prices()


def fleet_roi_summary(savings_per_van: float, fleet_size: int,
                       product_cost_per_van_monthly: float = 29.0) -> dict:
    """
    Computes total fleet ROI, net annual value, and capital payback period.
    """
    annual_savings = savings_per_van * fleet_size
    annual_product_cost = product_cost_per_van_monthly * 12 * fleet_size
    net_annual_benefit = annual_savings - annual_product_cost
    payback_months = (annual_product_cost / (annual_savings / 12)
                      if annual_savings > 0 else 999.0)

    return {
        "fleet_size": fleet_size,
        "savings_per_van_annual_usd": round(savings_per_van, 2),
        "total_annual_savings_usd": round(annual_savings, 2),
        "product_cost_annual_usd": round(annual_product_cost, 2),
        "net_annual_benefit_usd": round(net_annual_benefit, 2),
        "payback_months": round(payback_months, 1),
        "roi_pct": round((net_annual_benefit / annual_product_cost) * 100, 1)
                   if annual_product_cost > 0 else 0.0,
        "five_year_net_usd": round(net_annual_benefit * 5, 2),
    }


def benchmark_fleets() -> list:
    """
    US commercial electric fleet deployment benchmarks.
    """
    return [
        {"operator": "Amazon Logistics", "ev_vans": 100000, "vehicle": "Rivian EDV 500"},
        {"operator": "DHL Express",      "ev_vans": 35000,  "vehicle": "Mercedes eSprinter"},
        {"operator": "UPS Fleet",        "ev_vans": 10000,  "vehicle": "Mercedes eSprinter"},
        {"operator": "FedEx Express",    "ev_vans": 5000,   "vehicle": "BrightDrop EV600"},
    ]


def yearly_projection(savings_per_van: float, fleet_size: int, years: int = 5) -> list:
    """
    Computes year-over-year cumulative financial benefit.
    """
    rows = []
    cumulative = 0.0
    for yr in range(1, years + 1):
        annual = savings_per_van * fleet_size
        cumulative += annual
        rows.append({
            "year": yr,
            "annual_savings_usd": round(annual, 2),
            "cumulative_savings_usd": round(cumulative, 2)
        })
    return rows
