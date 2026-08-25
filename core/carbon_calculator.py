"""
Scope 3 ESG & Carbon Avoidance Engine
=====================================
Life-cycle greenhouse gas (GHG) accounting for commercial EV battery preservation.
Quantifies avoided embedded manufacturing emissions (Scope 3) and regulatory credits.
"""

# Life-Cycle Assessment (LCA) benchmarks from Argonne National Laboratory (GREET Model)
# Commercial NMC/LFP pack manufacturing carbon intensity: ~62 kg CO2e per kWh of capacity
EMBEDDED_KG_CO2_PER_KWH = 62.5
DIESEL_KG_CO2_PER_GALLON = 10.18
TREE_ANNUAL_CO2_ABSORPTION_KG = 21.77


def calculate_fleet_esg_impact(fleet_size: int = 500,
                               battery_kwh: float = 135.0,
                               lifespan_extension_years: float = 1.9,
                               nominal_lifespan_years: float = 8.0) -> dict:
    """
    Computes life-cycle embedded CO2 avoided by deferring premature battery replacement.
    """
    # Embedded carbon per full battery replacement pack
    pack_embedded_co2_kg = battery_kwh * EMBEDDED_KG_CO2_PER_KWH
    pack_embedded_co2_mt = pack_embedded_co2_kg / 1000.0

    # Fraction of full replacement avoided per vehicle annually
    replacement_avoided_fraction_annual = (lifespan_extension_years / nominal_lifespan_years) / 5.0

    # Annual and 5-year carbon avoidance
    unit_annual_co2_avoided_kg = pack_embedded_co2_kg * replacement_avoided_fraction_annual
    fleet_annual_co2_avoided_mt = (unit_annual_co2_avoided_kg * fleet_size) / 1000.0
    fleet_5yr_co2_avoided_mt = fleet_annual_co2_avoided_mt * 5.0

    # Environmental equivalence metrics
    tree_equivalent_annual = (fleet_annual_co2_avoided_mt * 1000.0) / TREE_ANNUAL_CO2_ABSORPTION_KG
    diesel_gallons_equivalent_annual = (fleet_annual_co2_avoided_mt * 1000.0) / DIESEL_KG_CO2_PER_GALLON

    # ESG Carbon Credit Valuation (assuming $45/metric ton Voluntary Carbon Market credit)
    carbon_credit_value_usd_annual = fleet_annual_co2_avoided_mt * 45.0
    carbon_credit_value_usd_5yr = fleet_5yr_co2_avoided_mt * 45.0

    return {
        "pack_embedded_co2_mt": round(pack_embedded_co2_mt, 1),
        "fleet_annual_co2_avoided_mt": round(fleet_annual_co2_avoided_mt, 1),
        "fleet_5yr_co2_avoided_mt": round(fleet_5yr_co2_avoided_mt, 1),
        "unit_annual_co2_avoided_kg": round(unit_annual_co2_avoided_kg, 1),
        "tree_equivalent_annual": int(tree_equivalent_annual),
        "diesel_gallons_equivalent_annual": int(diesel_gallons_equivalent_annual),
        "carbon_credit_value_usd_annual": round(carbon_credit_value_usd_annual, 2),
        "carbon_credit_value_usd_5yr": round(carbon_credit_value_usd_5yr, 2)
    }
