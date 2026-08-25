"""
Page 4 — 12-Hour Forecast & Workload Planner
Uses FortyGuard's 12-hour forecast to plan optimal delivery windows.
Max forecast = 12 hours (API enforced).
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.fortyguard_client import FortyGuardClient
from core.route_engine import get_city_key, CITY_DATA
from core.battery_model import BatteryDegradationModel

st.set_page_config(page_title="Forecast Planner — ThermoRoute AI",
                   page_icon="📅", layout="wide")

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

client = FortyGuardClient()
bm = BatteryDegradationModel()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## 📅 12-Hour Forecast & Delivery Planner")
st.info(
    "**FortyGuard API Forecast Limit: 12 hours ahead (max).**  \n"
    "ThermoRoute AI uses this window to identify the coolest delivery periods, "
    "minimising battery degradation and cooling costs for the shift ahead."
)

col1, col2 = st.columns(2)
with col1:
    city_options = [f"{v['city']}, {v['state']}" for v in CITY_DATA.values()]
    selected_city = st.selectbox("📍 City", city_options)
    city_key = get_city_key(selected_city)
with col2:
    vehicle_key = st.selectbox(
        "🚐 Vehicle",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['icon']} {ev_specs[k]['name']}"
    )

fleet_size = st.slider("Fleet Size", 10, 10000, 500, step=10)
st.divider()

# ── Get Forecast ──────────────────────────────────────────────────────────────
with st.spinner("📡 Fetching FortyGuard 12-hour forecast..."):
    city = CITY_DATA[city_key]
    location = f"{city['center'][0]},{city['center'][1]}"
    forecast_temps = client.get_forecast(location, hours_ahead=12)

now = datetime.now()
hours = [now + timedelta(hours=i) for i in range(12)]
hour_labels = [h.strftime("%I %p") for h in hours]

# ── Classify each hour ────────────────────────────────────────────────────────
factors = [bm.degradation_factor(t) for t in forecast_temps]
colors = [bm.risk_color(t) for t in forecast_temps]

# Best delivery windows (lowest degradation)
sorted_hours = sorted(range(12), key=lambda i: forecast_temps[i])
best_3 = sorted_hours[:3]
worst_3 = sorted_hours[-3:]

# ── Forecast Chart ────────────────────────────────────────────────────────────
fig = go.Figure()

# Background shading for good/bad windows
for i in best_3:
    fig.add_vrect(x0=i - 0.4, x1=i + 0.4,
                   fillcolor="rgba(34,197,94,0.1)", line_width=0)
for i in worst_3:
    fig.add_vrect(x0=i - 0.4, x1=i + 0.4,
                   fillcolor="rgba(239,68,68,0.1)", line_width=0)

fig.add_trace(go.Bar(
    x=hour_labels,
    y=forecast_temps,
    marker_color=colors,
    text=[f"{t:.0f}°F" for t in forecast_temps],
    textposition="outside",
    name="Forecast Temp"
))
fig.add_trace(go.Scatter(
    x=hour_labels,
    y=factors,
    mode="lines+markers",
    line=dict(color="#ffda00", width=2, dash="dot"),
    marker=dict(size=8, color="#ffda00"),
    name="Degradation Factor (×)",
    yaxis="y2"
))
fig.add_hline(y=95, line_dash="dot", line_color="#eab308",
               annotation_text="⚠️ 95°F threshold")
fig.add_hline(y=108, line_dash="dot", line_color="#ef4444",
               annotation_text="🔴 108°F critical")
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#a9b6c6",
    xaxis_title="Time",
    yaxis=dict(title="Temperature (°F)"),
    yaxis2=dict(title="Degradation Factor (×)", overlaying="y",
                 side="right", showgrid=False),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    height=420,
    title=dict(text=f"12-Hour Temperature Forecast — {selected_city}",
                font=dict(color="#fff"))
)
st.plotly_chart(fig, use_container_width=True)

# ── Best Windows ──────────────────────────────────────────────────────────────
st.markdown("### ✅ Optimal Delivery Windows (FortyGuard Forecast)")
st.caption("🟢 Green = coolest hours = lowest battery degradation")

win_cols = st.columns(3)
for col, idx in zip(win_cols, best_3):
    with col:
        temp = forecast_temps[idx]
        factor = factors[idx]
        savings_vs_worst = (
            factors[worst_3[-1]] - factor
        ) * ev_specs[vehicle_key]["battery_replacement_cost_usd"] / ev_specs[vehicle_key]["nominal_cycle_life_years"]

        st.markdown(f"""
<div style="background:rgba(34,197,94,0.1);border:1px solid #22c55e44;
     border-radius:10px;padding:14px;text-align:center;">
  <div style="color:#22c55e;font-weight:700;font-size:1.1rem;">{hour_labels[idx]}</div>
  <div style="color:#fff;font-size:1.8rem;font-weight:900;">{temp:.0f}°F</div>
  <div style="color:#a9b6c6;font-size:0.85rem;">{factor:.2f}× degradation</div>
  <div style="color:#22c55e;font-size:0.85rem;margin-top:6px;">
    ✅ Saves ${savings_vs_worst * fleet_size:,.0f} fleet-wide vs peak
  </div>
</div>
        """, unsafe_allow_html=True)

# ── Worst Windows ─────────────────────────────────────────────────────────────
st.markdown("### ⚠️ Avoid These Windows")
bad_cols = st.columns(3)
for col, idx in zip(bad_cols, worst_3):
    with col:
        temp = forecast_temps[idx]
        factor = factors[idx]
        st.markdown(f"""
<div style="background:rgba(239,68,68,0.1);border:1px solid #ef444444;
     border-radius:10px;padding:14px;text-align:center;">
  <div style="color:#ef4444;font-weight:700;font-size:1.1rem;">{hour_labels[idx]}</div>
  <div style="color:#fff;font-size:1.8rem;font-weight:900;">{temp:.0f}°F</div>
  <div style="color:#a9b6c6;font-size:0.85rem;">{factor:.2f}× degradation</div>
  <div style="color:#ef4444;font-size:0.85rem;margin-top:6px;">⛔ Avoid heavy deliveries</div>
</div>
        """, unsafe_allow_html=True)

st.divider()

# ── Fleet Summary Table ───────────────────────────────────────────────────────
st.markdown("### 📋 Hour-by-Hour Fleet Degradation Cost")
import pandas as pd
rows = []
for i, (label, temp, factor) in enumerate(zip(hour_labels, forecast_temps, factors)):
    annual_cost = bm.annual_degradation_cost(temp, vehicle_key)["heat_annual_cost_usd"]
    hourly_fleet_cost = (annual_cost / 365 / 24) * fleet_size
    tag = "✅ BEST" if i in best_3 else ("⛔ AVOID" if i in worst_3 else "")
    rows.append({
        "Hour": label,
        "Temp (°F)": f"{temp:.0f}",
        "Degradation": f"{factor:.2f}×",
        "Hourly Fleet Cost": f"${hourly_fleet_cost:,.2f}",
        "Status": tag
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
st.caption(
    "⚠️ FortyGuard API forecast limited to 12 hours ahead. "
    "This complies with the official API specification."
)
st.caption("⚡ ThermoRoute AI · FortyGuard Hackathon '26 · Track 03 Industrial & Enterprise")
