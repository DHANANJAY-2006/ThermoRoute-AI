"""
Page 7 — 12-Hour Shift Planner
Utilizes FortyGuard's 12-hour thermal forecast to optimize dispatch timing.
Adheres strictly to FortyGuard API's 12-hour maximum forecast horizon.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.fortyguard_client import FortyGuardClient
from core.route_engine import get_city_key, CITY_DATA
from core.battery_model import BatteryDegradationModel

st.set_page_config(
    page_title="12-Hour Shift Planner — ThermoRoute AI",
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
  .window-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 18px;
      text-align: center;
  }
  .status-pill {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 3px;
      font-weight: 700;
  }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.caption("FortyGuard Global AI Hackathon '26")
    st.caption("Track 03: Industrial & Enterprise")

client = FortyGuardClient()
bm = BatteryDegradationModel()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## 12-Hour Predictive Dispatch Planner")
st.caption("Temporal dispatch optimization enforcing FortyGuard API 12-hour forward forecast parameter limits.")
st.markdown("---")

# Controls
c1, c2, c3 = st.columns(3)
with c1:
    city_options = [f"{v['city']}, {v['state']}" for v in CITY_DATA.values()]
    selected_city = st.selectbox("Dispatch Region", city_options)
    city_key = get_city_key(selected_city)
with c2:
    vehicle_key = st.selectbox(
        "Fleet Configuration",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} — {ev_specs[k]['operator']}"
    )
with c3:
    fleet_size = st.number_input("Operating Fleet Units", min_value=1, max_value=250000, value=500, step=25)

# Fetch forecast
with st.spinner("Querying FortyGuard 12-hour thermal forecast telemetry..."):
    city = CITY_DATA.get(city_key, list(CITY_DATA.values())[0])
    location = f"{city['center'][0]},{city['center'][1]}"
    forecast_temps = client.get_forecast(location, hours_ahead=12)

now = datetime.now()
hours = [now + timedelta(hours=i) for i in range(12)]
hour_labels = [h.strftime("%H:00") for h in hours]
factors = [bm.degradation_factor(t) for t in forecast_temps]
colors = [bm.risk_color(t) for t in forecast_temps]

sorted_indices = sorted(range(12), key=lambda i: forecast_temps[i])
optimal_windows = sorted_indices[:3]
high_risk_windows = sorted_indices[-3:]

st.markdown("### 12-Hour Forward Thermal Trajectory")
fig_fc = go.Figure()

for idx in optimal_windows:
    fig_fc.add_vrect(x0=idx - 0.4, x1=idx + 0.4, fillcolor="rgba(34,197,94,0.1)", line_width=0)
for idx in high_risk_windows:
    fig_fc.add_vrect(x0=idx - 0.4, x1=idx + 0.4, fillcolor="rgba(239,68,68,0.1)", line_width=0)

fig_fc.add_trace(go.Bar(
    x=hour_labels,
    y=forecast_temps,
    marker_color=colors,
    text=[f"{t:.0f}°F" for t in forecast_temps],
    textposition="outside",
    name="Ambient Temperature (°F)"
))
fig_fc.add_trace(go.Scatter(
    x=hour_labels,
    y=factors,
    mode="lines+markers",
    line=dict(color="#38bdf8", width=2, dash="dot"),
    marker=dict(size=7, color="#38bdf8"),
    name="Degradation Multiplier",
    yaxis="y2"
))
fig_fc.add_hline(y=95, line_dash="dash", line_color="#eab308", annotation_text="Elevated (95°F)")
fig_fc.add_hline(y=108, line_dash="dash", line_color="#ef4444", annotation_text="Critical (108°F)")
fig_fc.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8"),
    xaxis=dict(title="Dispatch Hour (Local)", gridcolor="#1e293b"),
    yaxis=dict(title="Temperature (°F)", gridcolor="#1e293b"),
    yaxis2=dict(title="Degradation Multiplier (x)", overlaying="y", side="right", showgrid=False),
    height=360,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_fc, use_container_width=True)

st.markdown("---")

# Recommended vs High Risk Strips
st.markdown("### Optimal Dispatch Windows (Lowest Thermal Stress)")
w_cols = st.columns(3)
for col, idx in zip(w_cols, optimal_windows):
    with col:
        t = forecast_temps[idx]
        f = factors[idx]
        st.markdown(f"""
        <div class="window-card" style="border-top: 3px solid #22c55e;">
          <span class="status-pill" style="background:#22c55e20; color:#4ade80; border:1px solid #22c55e40;">PREFERRED DISPATCH</span>
          <div style="font-family:'JetBrains Mono', monospace; font-size:1.6rem; font-weight:700; color:#ffffff; margin:8px 0 4px 0;">
            {hour_labels[idx]}
          </div>
          <div style="color:#94a3b8; font-size:0.9rem;">Forecast: {t:.0f}°F</div>
          <div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#38bdf8; font-weight:600; margin-top:6px;">
            {f:.2f}x Nominal Aging
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("### High-Exposure Intervals (Shift Deferral Advised)")
r_cols = st.columns(3)
for col, idx in zip(r_cols, high_risk_windows):
    with col:
        t = forecast_temps[idx]
        f = factors[idx]
        st.markdown(f"""
        <div class="window-card" style="border-top: 3px solid #ef4444;">
          <span class="status-pill" style="background:#ef444420; color:#f87171; border:1px solid #ef444440;">HIGH STRESS EXPOSURE</span>
          <div style="font-family:'JetBrains Mono', monospace; font-size:1.6rem; font-weight:700; color:#ffffff; margin:8px 0 4px 0;">
            {hour_labels[idx]}
          </div>
          <div style="color:#94a3b8; font-size:0.9rem;">Forecast: {t:.0f}°F</div>
          <div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#f87171; font-weight:600; margin-top:6px;">
            {f:.2f}x Nominal Aging
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Hourly schedule matrix
st.markdown("### 12-Hour Operational Dispatch Matrix")
table_rows = []
for i, (label, t, f) in enumerate(zip(hour_labels, forecast_temps, factors)):
    status = "OPTIMAL DISPATCH" if i in optimal_windows else ("HIGH STRESS / AVOID" if i in high_risk_windows else "STANDARD DISPATCH")
    ann_cost = bm.annual_degradation_cost(t, vehicle_key)["heat_annual_cost_usd"]
    hourly_fleet = (ann_cost / 365 / 24) * fleet_size
    table_rows.append({
        "Hour": label,
        "Forecast Temperature": f"{t:.0f}°F",
        "Degradation Factor": f"{f:.2f}x",
        "Fleet Cost Run-Rate": f"${hourly_fleet:,.2f}/hr",
        "Dispatch Strategy": status
    })
st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
