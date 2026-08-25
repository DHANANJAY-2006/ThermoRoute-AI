"""
Page 3 — Financial Modeling & CapEx ROI Analysis
Financial modeling of thermal degradation mitigation.
Quantifies capital expenditure avoidance, payback horizons, and multi-year projections.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.battery_model import BatteryDegradationModel
from core.cost_calculator import fleet_roi_summary, benchmark_fleets, yearly_projection

st.set_page_config(
    page_title="Financial & ROI Analysis — ThermoRoute AI",
    layout="wide"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  header[data-testid="stHeader"] { background: rgba(4, 9, 28, 0.8) !important; backdrop-filter: blur(8px); }
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  [data-testid="stSidebarNav"] span {
      text-transform: capitalize !important;
      font-weight: 500 !important;
      font-size: 0.95rem !important;
  }
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
      background: rgba(15, 23, 42, 0.65);
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

bm = BatteryDegradationModel()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## Financial Modeling & CapEx ROI Analysis")
st.caption("Quantitative capital expenditure avoidance modeling based on Arrhenius cell degradation kinetics.")
st.markdown("---")

# Simulation Parameters
st.markdown("### Operational Simulation Inputs")
i1, i2, i3 = st.columns(3)
with i1:
    vehicle_key = st.selectbox(
        "Chassis Specification",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} (${ev_specs[k]['battery_replacement_cost_usd']:,} Pack Replacement)"
    )
with i2:
    hot_temp = st.slider("High-Stress Baseline Temp (°F)", 90.0, 130.0, 111.4, step=0.5)
with i3:
    cool_temp = st.slider("Thermally Managed Corridor Temp (°F)", 70.0, 110.0, 95.9, step=0.5)

i4, i5, i6 = st.columns(3)
with i4:
    fleet_size = st.number_input("Operational Fleet Size (Units)", 1, 250000, 500, step=25)
with i5:
    solar = st.slider("Mean Solar Irradiance (W/m²)", 200, 1200, 900, step=50)
with i6:
    saas_fee = st.number_input("Software Platform Fee ($/Unit/Month)", 1.0, 250.0, 29.0, step=1.0)

# Calculations
hot_data = bm.annual_degradation_cost(hot_temp, vehicle_key, solar_irradiance_wm2=solar, shade_pct=5.0)
cool_data = bm.annual_degradation_cost(cool_temp, vehicle_key, solar_irradiance_wm2=solar*0.75, shade_pct=30.0)
savings_per_van = max(0.0, hot_data["heat_annual_cost_usd"] - cool_data["heat_annual_cost_usd"])
roi = fleet_roi_summary(savings_per_van, fleet_size, saas_fee)
projection = yearly_projection(savings_per_van, fleet_size)

st.markdown("---")

# Executive Financial Summary
st.markdown("### Executive Financial Summary")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Unit CapEx Savings", value=f"${savings_per_van:,.0f}/yr", delta="Annual Asset Preservation")
with m2:
    st.metric(label="Fleet Annual Gross Benefit", value=f"${roi['total_annual_savings_usd']:,.0f}/yr", delta=f"{fleet_size} Units Active")
with m3:
    st.metric(label="Capital Payback Horizon", value=f"{roi['payback_months']:.1f} Months", delta="Rapid Value Realization")
with m4:
    st.metric(label="5-Year Net Benefit", value=f"${roi['five_year_net_usd']:,.0f}", delta=f"ROI: {roi['roi_pct']:.0f}%")

st.markdown("---")

# Visual analytics
c_plot1, c_plot2 = st.columns(2)

with c_plot1:
    st.markdown("#### Arrhenius Kinetics Degradation Curve")
    temps_range = list(range(60, 136, 2))
    deg_factors = [bm.degradation_factor(t, solar) for t in temps_range]
    
    fig_arr = go.Figure()
    fig_arr.add_trace(go.Scatter(
        x=temps_range, y=deg_factors,
        mode="lines",
        line=dict(color="#38bdf8", width=3),
        name="Degradation Multiplier"
    ))
    fig_arr.add_vline(x=hot_temp, line_color="#ef4444", line_dash="dash", annotation_text=f"High-Stress ({hot_temp:.1f}°F)")
    fig_arr.add_vline(x=cool_temp, line_color="#22c55e", line_dash="dash", annotation_text=f"Optimized ({cool_temp:.1f}°F)")
    fig_arr.add_vline(x=77, line_color="#64748b", line_dash="dot", annotation_text="Nominal (77°F)")
    fig_arr.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        xaxis=dict(title="Roadway Ambient Temperature (°F)", gridcolor="#1e293b"),
        yaxis=dict(title="Degradation Factor (x)", gridcolor="#1e293b"),
        height=340,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_arr, use_container_width=True)

with c_plot2:
    st.markdown("#### 5-Year Cumulative Fleet Net Benefit")
    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(
        x=[f"Year {r['year']}" for r in projection],
        y=[r["annual_savings_usd"] for r in projection],
        name="Annual Savings",
        marker_color="#1d4ed8"
    ))
    fig_proj.add_trace(go.Scatter(
        x=[f"Year {r['year']}" for r in projection],
        y=[r["cumulative_savings_usd"] for r in projection],
        mode="lines+markers",
        name="Cumulative Net Benefit",
        line=dict(color="#38bdf8", width=3),
        yaxis="y2"
    ))
    fig_proj.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        yaxis=dict(title="Annual Benefit ($)", gridcolor="#1e293b"),
        yaxis2=dict(title="Cumulative Benefit ($)", overlaying="y", side="right", showgrid=False),
        height=340,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_proj, use_container_width=True)

# Enterprise Industry Benchmark
st.markdown("---")
st.markdown("### Enterprise Fleet Macro Market Validation")
st.caption("Projected industry impact across active commercial EV deployment pipelines in the US logistics corridor:")

benchmarks = benchmark_fleets()
b_rows = []
for b in benchmarks:
    total_ann = savings_per_van * b["ev_vans"]
    b_rows.append({
        "Fleet Enterprise": b["operator"],
        "Active / Committed EV Fleet": f"{b['ev_vans']:,} Units",
        "Primary Chassis": b["vehicle"],
        "Annual CapEx Avoidance": f"${total_ann:,.0f}",
        "5-Year Value Created": f"${total_ann * 5:,.0f}"
    })

st.dataframe(pd.DataFrame(b_rows), use_container_width=True, hide_index=True)
