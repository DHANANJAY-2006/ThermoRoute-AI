"""
Page 3 — Financial Modeling & CapEx ROI Analysis
Comprehensive financial modeling of thermal operational mitigation.
Quantifies battery asset depreciation, energy/AC surcharge, range overhead, payback horizons, and multi-year projections.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os, json, importlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import core.battery_model
import core.ev_energy_model
import core.cost_calculator
importlib.reload(core.battery_model)
importlib.reload(core.ev_energy_model)
importlib.reload(core.cost_calculator)

from core.battery_model import BatteryDegradationModel
from core.ev_energy_model import EVEnergyModel
from core.cost_calculator import fleet_roi_summary, benchmark_fleets, yearly_projection

st.set_page_config(
    page_title="Financial & ROI Analysis — ThermoRoute AI",
    page_icon="assets/logo.png",
    layout="wide"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains Mono:wght@400;500;700&display=swap');
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
    col_logo, col_txt = st.columns([1, 3])
    with col_logo:
        st.image("assets/logo.png", use_container_width=True)
    with col_txt:
        st.markdown("""
        <div style="padding-top:2px;">
          <div style="font-weight:800; font-size:1.1rem; letter-spacing:-0.02em; color:#ffffff; line-height:1.2;">
            ThermoRoute <span style="color:#38bdf8; font-weight:700;">AI</span>
          </div>
          <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">
            FortyGuard API®
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 0 0 10px 0; border-bottom: 1px solid #172439; margin-bottom: 14px;">
      <div style="display:inline-flex; align-items:center; gap:6px; font-family:'JetBrains Mono', monospace; font-size:0.65rem; color:#38bdf8; background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.25); padding:2px 6px; border-radius:4px;">
        <span>TRACK 03 // ENTERPRISE</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

bm = BatteryDegradationModel()
em = EVEnergyModel()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## Financial Modeling & CapEx ROI Analysis")
st.caption("Comprehensive 3-Component EV Cost Engine: Arrhenius Cell Degradation · Energy/AC Penalty · Range Overhead")
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
    fleet_size = int(st.number_input("Operational Fleet Size (Units)", min_value=1, max_value=250000, value=500, step=1))
with i5:
    solar = int(st.slider("Mean Solar Irradiance (W/m²)", min_value=200, max_value=1200, value=900, step=50))
with i6:
    saas_fee = float(st.number_input("Software Platform Fee ($/Unit/Month)", min_value=1.0, max_value=250.0, value=29.0, step=1.0))

# 3-Component Cost Calculations
hot_deg = bm.annual_degradation_cost(hot_temp, vehicle_key, solar, 5.0)
cool_deg = bm.annual_degradation_cost(cool_temp, vehicle_key, solar * 0.75, 30.0)

hot_op = em.total_operational_cost_annual(hot_temp, vehicle_key)
cool_op = em.total_operational_cost_annual(cool_temp, vehicle_key)

hot_total_per_van = hot_deg["heat_annual_cost_usd"] + hot_op["annual_operational_penalty_usd"]
cool_total_per_van = cool_deg["heat_annual_cost_usd"] + cool_op["annual_operational_penalty_usd"]

deg_savings = max(0.0, hot_deg["heat_annual_cost_usd"] - cool_deg["heat_annual_cost_usd"])
energy_savings = max(0.0, hot_op["annual_energy_penalty_usd"] - cool_op["annual_energy_penalty_usd"])
range_savings = max(0.0, hot_op["annual_range_overhead_usd"] - cool_op["annual_range_overhead_usd"])

total_savings_per_van = max(0.0, hot_total_per_van - cool_total_per_van)

roi = fleet_roi_summary(total_savings_per_van, fleet_size, saas_fee)
projection = yearly_projection(total_savings_per_van, fleet_size)

st.markdown("---")

# Executive Financial Summary
st.markdown("### Executive Financial Summary (3-Component Model)")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Unit Total Annual Savings", value=f"${total_savings_per_van:,.0f}/yr", delta="Asset + Energy + Range")
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
    st.markdown("#### 3-Component Cost Stack: High-Stress vs. Optimized")
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name="Battery Degradation",
        x=["High-Stress Corridor", "Optimized Corridor"],
        y=[hot_deg["heat_annual_cost_usd"], cool_deg["heat_annual_cost_usd"]],
        marker_color="#ef4444"
    ))
    fig_comp.add_trace(go.Bar(
        name="Energy & AC Surcharge",
        x=["High-Stress Corridor", "Optimized Corridor"],
        y=[hot_op["annual_energy_penalty_usd"], cool_op["annual_energy_penalty_usd"]],
        marker_color="#f97316"
    ))
    fig_comp.add_trace(go.Bar(
        name="Range Overhead & Charging",
        x=["High-Stress Corridor", "Optimized Corridor"],
        y=[hot_op["annual_range_overhead_usd"], cool_op["annual_range_overhead_usd"]],
        marker_color="#eab308"
    ))
    fig_comp.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        yaxis=dict(title="Annual Cost per Van ($)", gridcolor="#1e293b"),
        height=340,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

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
    total_ann = total_savings_per_van * b["ev_vans"]
    b_rows.append({
        "Fleet Enterprise": b["operator"],
        "Active / Committed EV Fleet": f"{b['ev_vans']:,} Units",
        "Primary Chassis": b["vehicle"],
        "Annual Cost Avoidance": f"${total_ann:,.0f}",
        "5-Year Value Created": f"${total_ann * 5:,.0f}"
    })

st.dataframe(pd.DataFrame(b_rows), use_container_width=True, hide_index=True)
