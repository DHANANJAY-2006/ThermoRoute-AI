"""
Page 5 — Smart Depot Charging & Thermal Pre-Conditioning
Optimizes fleet charging schedules against FortyGuard 12-hour temperature forecasts
and Time-of-Use (TOU) electricity pricing to eliminate thermal charging stress.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.fortyguard_client import FortyGuardClient
from core.depot_optimizer import optimize_depot_charging
from core.route_engine import get_city_key, CITY_DATA

st.set_page_config(
    page_title="Smart Depot Charging — ThermoRoute AI",
    layout="wide"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  header[data-testid="stHeader"] { background: rgba(4, 9, 28, 0.8) !important; backdrop-filter: blur(8px); }
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  [data-testid="stAppViewContainer"] {
      background: radial-gradient(circle at 50% 0%, #0c1729 0%, #050a14 70%, #03060c 100%);
      color: #e2e8f0;
  }
  [data-testid="stSidebar"] { background-color: #060b14; border-right: 1px solid #172439; }
  [data-testid="metric-container"] {
      background: rgba(15, 23, 42, 0.65);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 14px 18px;
  }
  .panel-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 16px;
  }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.caption("FortyGuard Global AI Hackathon '26")
    st.caption("Track 03: Industrial & Enterprise")

client = FortyGuardClient()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## Smart Depot Charging & Thermal Pre-Conditioning Optimizer")
st.caption("Thermal-economic arbitrage aligning depot charging with FortyGuard 12-hour forecast and off-peak utility tariffs.")
st.markdown("---")

# Controls
c1, c2, c3, c4 = st.columns(4)
with c1:
    city_options = [f"{v['city']}, {v['state']}" for v in CITY_DATA.values()]
    selected_city = st.selectbox("Depot Facility Location", city_options)
    city_key = get_city_key(selected_city)
with c2:
    vehicle_key = st.selectbox(
        "Fleet Chassis Model",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} ({ev_specs[k]['battery_capacity_kwh']} kWh)"
    )
with c3:
    fleet_size = st.number_input("Staged Fleet Scale (Units)", 1, 250000, 500, step=25)
with c4:
    charger_power = st.selectbox("Depot Charger Power (kW/Stall)", [11.0, 19.2, 22.0, 50.0], index=2)

# Query FortyGuard 12-hour forecast
city = CITY_DATA.get(city_key, list(CITY_DATA.values())[0])
forecast_temps = client.get_forecast(f"{city['center'][0]},{city['center'][1]}", hours_ahead=12)

# Run optimization
depot_opt = optimize_depot_charging(
    forecast_temps=forecast_temps,
    fleet_size=fleet_size,
    battery_kwh=ev_specs[vehicle_key]["battery_capacity_kwh"],
    daily_kwh_needed=ev_specs[vehicle_key]["battery_capacity_kwh"] * 0.65,
    depot_power_kw_per_stall=charger_power
)

# Top Metrics Strip
d1, d2, d3, d4 = st.columns(4)
with d1:
    st.metric(
        label="Coolest Charging Window",
        value=depot_opt["coolest_charge_window"],
        delta="Optimal Cell Chemistry Window",
        delta_color="normal"
    )
with d2:
    st.metric(
        label="Peak Heat Window Avoided",
        value=depot_opt["hottest_avoided_window"],
        delta="High Stress Avoided",
        delta_color="inverse"
    )
with d3:
    st.metric(
        label="Unit Annual Depot Savings",
        value=f"${depot_opt['annual_depot_savings_per_van_usd']:,.0f}/yr",
        delta="TOU Tariff + Cell Wear",
        delta_color="normal"
    )
with d4:
    st.metric(
        label=f"Fleet Annual Depot Benefit ({fleet_size} Units)",
        value=f"${depot_opt['annual_depot_fleet_savings_usd']:,.0f}/yr",
        delta="Utility & Asset ROI",
        delta_color="normal"
    )

st.markdown("---")

# Chart: Thermal Forecast vs Charging Power Schedule
st.markdown("### 12-Hour Depot Charging Schedule & Ambient Thermal Profile")
st.caption("Charging power (kW) dynamically scheduled during low-temperature and off-peak utility intervals:")

hours = [s["hour"] for s in depot_opt["schedule"]]
temps = [s["temp_f"] for s in depot_opt["schedule"]]
powers = [s["charge_power_kw"] for s in depot_opt["schedule"]]
tariffs = [s["tariff_per_kwh"] for s in depot_opt["schedule"]]

fig_depot = go.Figure()

# Ambient temperature curve
fig_depot.add_trace(go.Scatter(
    x=hours,
    y=temps,
    mode="lines+markers",
    name="FortyGuard Ambient Temp (°F)",
    line=dict(color="#f97316", width=3)
))

# Scheduled Charging Power Bars
fig_depot.add_trace(go.Bar(
    x=hours,
    y=powers,
    name="Active Charge Rate (kW)",
    marker_color="#38bdf8",
    opacity=0.7,
    yaxis="y2"
))

fig_depot.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8"),
    xaxis=dict(title="Depot Staging Hour (Local)", gridcolor="#1e293b"),
    yaxis=dict(title="Ambient Temperature (°F)", gridcolor="#1e293b"),
    yaxis2=dict(title="Charging Power (kW)", overlaying="y", side="right", showgrid=False, range=[0, max(powers)*2.2 if max(powers) > 0 else 50]),
    height=380,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_depot, use_container_width=True)

st.markdown("---")

# Hourly Depot Schedule Table
st.markdown("### Staged Dispatch & Thermal Conditioning Schedule")
st.dataframe(pd.DataFrame(depot_opt["schedule"]), use_container_width=True, hide_index=True)
