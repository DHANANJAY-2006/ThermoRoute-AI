"""
Page 3 — Battery Savings Calculator
The financial case for ThermoRoute AI.
VC judge Vikram Venkat (Cota Capital) focus: make the ROI unmissable.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.battery_model import BatteryDegradationModel
from core.cost_calculator import fleet_roi_summary, benchmark_fleets, yearly_projection

st.set_page_config(page_title="Battery Savings — ThermoRoute AI",
                   page_icon="💰", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background:linear-gradient(160deg,#04091C 0%,#060E22 50%,#091A35 100%);
}
[data-testid="stSidebar"] { background-color:#0d1627; }
h1,h2,h3 { color:#ffffff !important; }
p,li { color:#a9b6c6 !important; }
</style>
""", unsafe_allow_html=True)

bm = BatteryDegradationModel()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## 💰 Battery Savings Calculator")
st.caption("Translate thermal route optimisation into real dollar savings")
st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    vehicle_key = st.selectbox(
        "Vehicle Type",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['icon']} {ev_specs[k]['name']}"
    )
with col2:
    hot_temp = st.slider("🔥 Hot Route Avg Temp (°F)", 90, 130, 112)
with col3:
    cool_temp = st.slider("🌿 Cool Route Avg Temp (°F)", 70, 110, 96)

col4, col5, col6 = st.columns(3)
with col4:
    fleet_size = st.number_input("Fleet Size", 1, 500000, 500, step=50)
with col5:
    solar = st.slider("Solar Irradiance (W/m²)", 200, 1200, 900,
                       help="From FortyGuard /v1/env_params")
with col6:
    product_price = st.number_input("ThermoRoute AI Price ($/van/month)",
                                     1.0, 500.0, 29.0, step=1.0)

st.divider()

# ── Calculations ──────────────────────────────────────────────────────────────
hot_data = bm.annual_degradation_cost(hot_temp, vehicle_key, solar)
cool_data = bm.annual_degradation_cost(cool_temp, vehicle_key, solar)
savings_per_van = hot_data["heat_annual_cost_usd"] - cool_data["heat_annual_cost_usd"]
savings_per_van = max(0, savings_per_van)
roi = fleet_roi_summary(savings_per_van, fleet_size, product_price)
projection = yearly_projection(savings_per_van, fleet_size)

# ── Hero Metrics ──────────────────────────────────────────────────────────────
st.markdown("### 💸 Your Savings Summary")
m1, m2, m3, m4 = st.columns(4)
m1.metric("💰 Savings Per Van", f"${savings_per_van:,.0f}/yr",
           f"{roi['savings_per_van_annual_usd']:,.0f} annually")
m2.metric("🚐 Total Fleet Savings", f"${roi['total_annual_savings_usd']:,.0f}/yr",
           f"{fleet_size} vans × ${savings_per_van:,.0f}")
m3.metric("⏱️ Payback Period", f"{roi['payback_months']:.1f} months",
           "ThermoRoute AI pays for itself")
m4.metric("📈 5-Year Net Benefit", f"${roi['five_year_net_usd']:,.0f}",
           f"ROI: {roi['roi_pct']:.0f}%")

st.divider()

# ── Degradation Comparison ────────────────────────────────────────────────────
st.markdown("### 🔋 Hot vs Cool Route — Battery Degradation Detail")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"#### 🔥 Hot Route ({hot_temp}°F)")
    st.metric("Degradation Factor", f"{hot_data['degradation_factor']:.2f}×")
    st.metric("Annual Cost Per Van", f"${hot_data['heat_annual_cost_usd']:,.0f}")
    st.metric("Extra vs Ideal", f"${hot_data['extra_annual_cost_usd']:,.0f}")
    st.metric("Effective Battery Life", f"{hot_data['effective_lifespan_years']:.1f} years")

with col_b:
    st.markdown(f"#### 🌿 Cool Route ({cool_temp}°F)")
    st.metric("Degradation Factor", f"{cool_data['degradation_factor']:.2f}×")
    st.metric("Annual Cost Per Van", f"${cool_data['heat_annual_cost_usd']:,.0f}")
    st.metric("Extra vs Ideal", f"${cool_data['extra_annual_cost_usd']:,.0f}")
    st.metric("Effective Battery Life", f"{cool_data['effective_lifespan_years']:.1f} years")

st.divider()

# ── Degradation curve ─────────────────────────────────────────────────────────
st.markdown("### 🔬 Arrhenius Degradation Curve")
import numpy as np
temps = list(range(60, 140, 2))
factors = [bm.degradation_factor(t, solar) for t in temps]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=temps, y=factors,
    mode="lines",
    line=dict(color="#1769b0", width=3),
    name="Degradation Factor"
))
fig.add_vline(x=hot_temp, line_color="#ef4444", line_dash="dash",
               annotation_text=f"Hot Route {hot_temp}°F ({bm.degradation_factor(hot_temp, solar):.2f}×)")
fig.add_vline(x=cool_temp, line_color="#22c55e", line_dash="dash",
               annotation_text=f"Cool Route {cool_temp}°F ({bm.degradation_factor(cool_temp, solar):.2f}×)")
fig.add_vline(x=77, line_color="#a9b6c6", line_dash="dot",
               annotation_text="77°F Baseline")
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#a9b6c6",
    xaxis_title="Temperature (°F)",
    yaxis_title="Degradation Factor (×)",
    height=380
)
st.plotly_chart(fig, use_container_width=True)

# ── 5-Year Projection ─────────────────────────────────────────────────────────
st.markdown("### 📈 5-Year Cumulative Fleet Savings")
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=[f"Year {r['year']}" for r in projection],
    y=[r["annual_savings_usd"] for r in projection],
    name="Annual Savings",
    marker_color="#1769b0"
))
fig2.add_trace(go.Scatter(
    x=[f"Year {r['year']}" for r in projection],
    y=[r["cumulative_savings_usd"] for r in projection],
    mode="lines+markers",
    name="Cumulative Savings",
    line=dict(color="#ffda00", width=3),
    yaxis="y2"
))
fig2.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#a9b6c6",
    yaxis=dict(title="Annual Savings ($)"),
    yaxis2=dict(title="Cumulative ($)", overlaying="y", side="right"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    height=380
)
st.plotly_chart(fig2, use_container_width=True)

# ── Industry Benchmarks ───────────────────────────────────────────────────────
st.divider()
st.markdown("### 🌍 Industry-Scale Impact — US EV Delivery Fleets")
st.caption("Based on publicly known fleet sizes. FortyGuard is a DHL technology partner.")

benchmarks = benchmark_fleets()
import pandas as pd
rows = []
for b in benchmarks:
    vk = list(ev_specs.keys())[0]  # use selected vehicle for comparison
    svpu = savings_per_van
    total = svpu * b["ev_vans"]
    rows.append({
        "Operator": b["operator"],
        "EV Fleet Size": f"{b['ev_vans']:,}",
        "Vehicle": b["vehicle"],
        "Annual Savings": f"${total:,.0f}",
        "Monthly Savings": f"${total/12:,.0f}"
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.info(
    f"💡 **DHL is a FortyGuard partner.** "
    f"At {savings_per_van:,.0f}$/van/year savings across DHL's 35,000 EV vans: "
    f"**${savings_per_van * 35000:,.0f}/year** in battery savings — powered by FortyGuard data."
)

st.caption("⚡ ThermoRoute AI · FortyGuard Hackathon '26 · Track 03 Industrial & Enterprise")
