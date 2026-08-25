"""
Page 4 — ML Battery Health (SoH %) & Remaining Useful Life (RUL)
Physics-Informed degradation simulator modeling capacity retention over 100,000 miles.
Demonstrates life extension from 2.2 years (unmanaged) to 4.5+ years (ThermoRoute AI).
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.ml_battery_health import simulate_degradation_curve

st.set_page_config(
    page_title="Battery Health ML (SoH & RUL) — ThermoRoute AI",
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

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## Physics-Informed ML Battery Health (SoH %) & Remaining Useful Life")
st.caption("Electro-thermal capacity loss simulation over 120,000 operational transit miles.")
st.markdown("---")

# Controls
c1, c2, c3, c4 = st.columns(4)
with c1:
    vehicle_key = st.selectbox(
        "Commercial Platform",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} (${ev_specs[k]['battery_replacement_cost_usd']:,} Pack)"
    )
with c2:
    ambient_temp = st.slider("Mean Operating Ambient Temp (°F)", 85.0, 125.0, 111.4, step=0.5)
with c3:
    dod_input = st.slider("Daily Depth of Discharge (DoD %)", 50, 100, 80, step=5)
with c4:
    fast_charge_ratio = st.slider("DC Fast Charging Ratio (%)", 0, 100, 40, step=5)

# Simulate degradation
sim_res = simulate_degradation_curve(
    max_miles=120000,
    ambient_temp_f=ambient_temp,
    dod_pct=dod_input,
    fast_charge_pct=fast_charge_ratio
)

# Top Summary Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(
        label="Unmanaged Lifespan to 70% EOL",
        value=f"{sim_res['miles_to_70_unmanaged']:,} Miles",
        delta=f"{sim_res['years_to_eol_unmanaged']} Years Rated",
        delta_color="inverse"
    )
with m2:
    st.metric(
        label="ThermoRoute AI Managed Lifespan",
        value=f"{sim_res['miles_to_70_managed']:,} Miles",
        delta=f"{sim_res['years_to_eol_managed']} Years Rated",
        delta_color="normal"
    )
with m3:
    st.metric(
        label="Asset Life Extension Delta",
        value=f"+{sim_res['extended_life_years']} Years",
        delta=f"+{sim_res['extended_life_miles']:,} Miles",
        delta_color="normal"
    )
with m4:
    rep_cost = ev_specs[vehicle_key]["battery_replacement_cost_usd"]
    # Saved depreciation
    ann_savings = (rep_cost / sim_res['years_to_eol_unmanaged']) - (rep_cost / sim_res['years_to_eol_managed'])
    st.metric(
        label="Annual Unit CapEx Avoidance",
        value=f"${ann_savings:,.0f}/yr",
        delta=f"${ann_savings * 500:,.0f}/yr (500 Vans)",
        delta_color="normal"
    )

st.markdown("---")

# SoH Degradation Trajectory Plot
st.markdown("### 120,000-Mile Battery Capacity Retention Trajectory (SoH %)")
st.caption("Comparison of chemical capacity fade between unmanaged urban corridors and ThermoRoute AI thermal routing:")

fig_soh = go.Figure()

fig_soh.add_trace(go.Scatter(
    x=sim_res["mileage_points"],
    y=sim_res["unmanaged_soh"],
    mode="lines",
    name="Unmanaged Routing (Urban Core Heat)",
    line=dict(color="#ef4444", width=3)
))

fig_soh.add_trace(go.Scatter(
    x=sim_res["mileage_points"],
    y=sim_res["managed_soh"],
    mode="lines",
    name="ThermoRoute AI (Thermally Managed Corridors)",
    line=dict(color="#22c55e", width=3)
))

# 80% and 70% threshold lines
fig_soh.add_hline(y=80.0, line_dash="dash", line_color="#eab308", annotation_text="OEM Warranty Threshold (80% SoH)")
fig_soh.add_hline(y=70.0, line_dash="dash", line_color="#ef4444", annotation_text="End of Commercial Life (70% SoH)")

fig_soh.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8"),
    xaxis=dict(title="Odometer Mileage (Miles)", gridcolor="#1e293b"),
    yaxis=dict(title="Battery State-of-Health (%)", gridcolor="#1e293b", range=[50, 102]),
    height=420,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_soh, use_container_width=True)

st.markdown("---")

# Milestone Breakdown Table
st.markdown("### Commercial Pack Aging Milestones")
milestone_data = [
    {
        "Operational Threshold": "80% SoH (OEM Warranty Limit)",
        "Unmanaged Routing": f"{sim_res['miles_to_80_unmanaged']:,} Miles (~{round(sim_res['miles_to_80_unmanaged']/22000, 1)} Years)",
        "ThermoRoute AI Managed": f"{sim_res['miles_to_80_managed']:,} Miles (~{round(sim_res['miles_to_80_managed']/22000, 1)} Years)",
        "Preservation Advantage": f"+{sim_res['miles_to_80_managed'] - sim_res['miles_to_80_unmanaged']:,} Miles (+{round((sim_res['miles_to_80_managed'] - sim_res['miles_to_80_unmanaged'])/22000, 1)} Years)"
    },
    {
        "Operational Threshold": "70% SoH (End-of-Life Pack Scrappage)",
        "Unmanaged Routing": f"{sim_res['miles_to_70_unmanaged']:,} Miles (~{sim_res['years_to_eol_unmanaged']} Years)",
        "ThermoRoute AI Managed": f"{sim_res['miles_to_70_managed']:,} Miles (~{sim_res['years_to_eol_managed']} Years)",
        "Preservation Advantage": f"+{sim_res['extended_life_miles']:,} Miles (+{sim_res['extended_life_years']} Years)"
    }
]

st.dataframe(pd.DataFrame(milestone_data), use_container_width=True, hide_index=True)
