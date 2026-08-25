"""
Page 1 — Fleet Dashboard
Real-time fleet heat risk across all supported US cities.
Uses FortyGuard heatmap + env_params endpoints.
"""

import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.fortyguard_client import FortyGuardClient
from core.route_engine import multi_city_snapshot, get_available_cities, get_city_key
from core.alert_manager import evaluate
from core.battery_model import BatteryDegradationModel
import json

st.set_page_config(page_title="Fleet Dashboard — ThermoRoute AI",
                   page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg,#04091C 0%,#060E22 50%,#091A35 100%);
}
[data-testid="stSidebar"] { background-color:#0d1627; }
h1,h2,h3 { color:#ffffff !important; }
p,li { color:#a9b6c6 !important; }
</style>
""", unsafe_allow_html=True)

client = FortyGuardClient()
bm = BatteryDegradationModel()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Fleet Thermal Risk Dashboard")
st.caption(f"Data source: FortyGuard Temperature API® · {client.mode} · US cities only")

# ── Vehicle selector ──────────────────────────────────────────────────────────
with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

vehicle_key = st.selectbox(
    "Select Vehicle Type",
    list(ev_specs.keys()),
    format_func=lambda k: f"{ev_specs[k]['icon']} {ev_specs[k]['name']} ({ev_specs[k]['operator']})"
)

fleet_size = st.slider("Fleet Size (number of vans)", 10, 10000, 500, step=10)
st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("🌡️ Fetching live temperature data from FortyGuard API..."):
    cities = multi_city_snapshot(vehicle_key, client)

# ── Risk Cards ────────────────────────────────────────────────────────────────
st.markdown("### 🌍 City-by-City Heat Risk")
cols = st.columns(len(cities))

for col, city in zip(cols, cities):
    with col:
        factor = city["degradation_factor"]
        temp = city["temp_f"]
        annual_extra = bm.annual_degradation_cost(temp, vehicle_key)["extra_annual_cost_usd"]
        fleet_extra = annual_extra * fleet_size

        st.markdown(f"""
<div style="background:rgba(23,105,176,0.1);border:1px solid {city['color']}44;
     border-radius:12px;padding:16px;text-align:center;">
  <div style="font-size:2rem;">{_risk_icon(city['risk_level'])}</div>
  <div style="color:#fff;font-weight:700;font-size:1.1rem;">{city['city']}, {city['state']}</div>
  <div style="color:{city['color']};font-size:2rem;font-weight:900;">{temp:.0f}°F</div>
  <div style="color:#a9b6c6;font-size:0.85rem;">{city['risk_level'].upper()} RISK</div>
  <hr style="border-color:#1e3a5f;margin:8px 0;">
  <div style="color:#ffda00;font-size:1.1rem;font-weight:700;">{factor:.2f}× degradation</div>
  <div style="color:#a9b6c6;font-size:0.8rem;">+${annual_extra:,.0f}/van/yr</div>
  <div style="color:#ef4444;font-size:0.8rem;">Fleet: +${fleet_extra:,.0f}/yr</div>
</div>
        """, unsafe_allow_html=True)


def _risk_icon(level: str) -> str:
    level = level.lower()
    if "critical" in level or "extreme" in level:
        return "🔴"
    elif "high" in level:
        return "🟠"
    elif "moderate" in level:
        return "🟡"
    return "🟢"


st.divider()

# ── Temp Bar Chart ────────────────────────────────────────────────────────────
st.markdown("### 🌡️ Temperature Comparison")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=[f"{c['city']}, {c['state']}" for c in cities],
    y=[c["temp_f"] for c in cities],
    marker_color=[c["color"] for c in cities],
    text=[f"{c['temp_f']:.0f}°F" for c in cities],
    textposition="outside"
))
fig.add_hline(y=95, line_dash="dot", line_color="#eab308",
               annotation_text="⚠️ High Risk Threshold (95°F)")
fig.add_hline(y=108, line_dash="dot", line_color="#ef4444",
               annotation_text="🔴 Critical Threshold (108°F)")
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#a9b6c6",
    yaxis_title="Temperature (°F)",
    showlegend=False,
    height=350
)
st.plotly_chart(fig, use_container_width=True)

# ── Degradation Factor Chart ──────────────────────────────────────────────────
st.markdown("### 🔋 Battery Degradation Factor by City")
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=[f"{c['city']}, {c['state']}" for c in cities],
    y=[c["degradation_factor"] for c in cities],
    marker_color=[c["color"] for c in cities],
    text=[f"{c['degradation_factor']:.2f}×" for c in cities],
    textposition="outside"
))
fig2.add_hline(y=1.0, line_dash="dot", line_color="#22c55e",
                annotation_text="✅ Baseline (77°F ideal)")
fig2.add_hline(y=3.0, line_dash="dot", line_color="#ef4444",
                annotation_text="🔴 High damage (>3×)")
fig2.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#a9b6c6",
    yaxis_title="Degradation Factor (×)",
    showlegend=False,
    height=350
)
st.plotly_chart(fig2, use_container_width=True)

# ── Highest risk city alerts ──────────────────────────────────────────────────
st.divider()
st.markdown("### 🚨 Live Alerts — Highest Risk City")
top = cities[0]  # already sorted hottest first
env = top.get("env_params") or {}
persistence = env.get("persistence_hours", 8.5)
alerts = evaluate(top["temp_f"], top["degradation_factor"], persistence,
                   route_name=f"{top['city']} fleet routes")

for alert in alerts:
    level = alert["level"]
    if "CRITICAL" in level or "WAVE" in level:
        css = "alert-critical"
    elif "HIGH" in level:
        css = "alert-high"
    else:
        css = "alert-ok"
    st.markdown(f"""
<div class="{css}">
  <strong>{alert['level']}</strong> · {alert['time']}<br>
  {alert['message']}<br>
  <em>Recommended action: {alert['action']}</em>
</div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("⚡ ThermoRoute AI · FortyGuard Hackathon '26 · Track 03 Industrial & Enterprise")
