"""
Page 1 — Fleet Risk Monitor
Real-time thermal risk monitoring across major logistics hubs.
Powered by FortyGuard /v1/heatmap and /v1/env_params endpoints.
"""

import streamlit as st
import plotly.graph_objects as go
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.fortyguard_client import FortyGuardClient
from core.route_engine import multi_city_snapshot
from core.alert_manager import evaluate
from core.battery_model import BatteryDegradationModel

st.set_page_config(
    page_title="Fleet Risk Monitor — ThermoRoute AI",
    layout="wide"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
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
  .city-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 12px;
  }
  .status-pill {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 3px;
      font-weight: 600;
  }
</style>
""", unsafe_allow_html=True)

client = FortyGuardClient()
bm = BatteryDegradationModel()

# Load vehicle configurations
with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## Fleet Thermal Exposure Monitor")
st.caption(f"Data source: FortyGuard Temperature API® · System Mode: {client.mode} · Jurisdiction: United States")
st.markdown("---")

# Controls
ctrl1, ctrl2 = st.columns([2, 1])
with ctrl1:
    vehicle_key = st.selectbox(
        "Commercial Chassis Selection",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} — {ev_specs[k]['operator']} ({ev_specs[k]['battery_kwh']} kWh Pack)"
    )
with ctrl2:
    fleet_size = st.number_input("Active Fleet Size (Units)", min_value=1, max_value=250000, value=500, step=25)

# Fetch telemetry
with st.spinner("Acquiring regional thermal telemetry from FortyGuard API..."):
    cities = multi_city_snapshot(vehicle_key, client)

st.markdown("### Regional Thermal Exposure Index")
city_cols = st.columns(len(cities))

for col, city in zip(city_cols, cities):
    with col:
        factor = city["degradation_factor"]
        temp = city["temp_f"]
        cost_data = bm.annual_degradation_cost(temp, vehicle_key)
        annual_extra = cost_data["extra_annual_cost_usd"]
        fleet_extra = annual_extra * fleet_size
        
        status_color = city["color"]
        
        st.markdown(f"""
        <div class="city-card" style="border-top: 3px solid {status_color};">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-weight:700; font-size:1.05rem; color:#f8fafc;">{city['city']}, {city['state']}</span>
            <span class="status-pill" style="background:{status_color}20; color:{status_color}; border:1px solid {status_color}40;">
              {city['risk_level'].upper()}
            </span>
          </div>
          <div style="font-family:'JetBrains Mono', monospace; font-size:2rem; font-weight:700; color:#ffffff; margin: 6px 0;">
            {temp:.0f}°F
          </div>
          <p style="font-size:0.8rem; color:#94a3b8; margin-bottom:12px;">Heat Index: {city['heat_index_f']:.0f}°F · Persistence: {city['persistence_hours']:.1f}h</p>
          <div style="border-top:1px solid #1e293b; padding-top:10px;">
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#38bdf8; font-weight:600;">
              {factor:.2f}x Degradation Rate
            </div>
            <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">
              Unit Cost Delta: +${annual_extra:,.0f}/yr
            </div>
            <div style="font-size:0.8rem; color:#f43f5e; font-weight:600; margin-top:2px;">
              Fleet Impact: +${fleet_extra:,.0f}/yr
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Analytics charts
c_chart1, c_chart2 = st.columns(2)

with c_chart1:
    st.markdown("#### Ambient Roadway Temperature")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{c['city']}, {c['state']}" for c in cities],
        y=[c["temp_f"] for c in cities],
        marker_color=[c["color"] for c in cities],
        text=[f"{c['temp_f']:.0f}°F" for c in cities],
        textposition="outside"
    ))
    fig.add_hline(y=95, line_dash="dash", line_color="#eab308", annotation_text="Elevated Threshold (95°F)")
    fig.add_hline(y=108, line_dash="dash", line_color="#ef4444", annotation_text="Critical Threshold (108°F)")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        yaxis=dict(title="Temperature (°F)", gridcolor="#1e293b"),
        xaxis=dict(gridcolor="#1e293b"),
        height=320,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with c_chart2:
    st.markdown("#### Electrochemical Degradation Multiplier")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=[f"{c['city']}, {c['state']}" for c in cities],
        y=[c["degradation_factor"] for c in cities],
        marker_color=[c["color"] for c in cities],
        text=[f"{c['degradation_factor']:.2f}x" for c in cities],
        textposition="outside"
    ))
    fig2.add_hline(y=1.0, line_dash="dot", line_color="#22c55e", annotation_text="Nominal Baseline (1.00x)")
    fig2.add_hline(y=3.0, line_dash="dash", line_color="#ef4444", annotation_text="Accelerated Degradation (>3.0x)")
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        yaxis=dict(title="Degradation Multiplier", gridcolor="#1e293b"),
        xaxis=dict(gridcolor="#1e293b"),
        height=320,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

# Autonomous decision engine output
st.markdown("---")
st.markdown("### Autonomous Decision Support")
st.caption("Real-time automated evaluation of thermal exposure parameters:")

top_risk_city = cities[0]
persistence = top_risk_city.get("persistence_hours", 8.5)
alerts = evaluate(top_risk_city["temp_f"], top_risk_city["degradation_factor"], persistence,
                  route_name=f"{top_risk_city['city']} Central Logistics Network")

for a in alerts:
    border_color = a["color"]
    st.markdown(f"""
    <div style="background:rgba(15,23,42,0.6); border-left:4px solid {border_color}; border-radius:4px; padding:14px 18px; margin-bottom:10px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <span style="font-family:'JetBrains Mono', monospace; font-size:0.78rem; font-weight:700; color:{border_color};">{a['level']}</span>
        <span style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#64748b;">LOGGED AT {a['time']}</span>
      </div>
      <p style="margin:0 0 6px 0; color:#f1f5f9;">{a['message']}</p>
      <div style="font-size:0.82rem; color:#38bdf8;"><strong>Recommended Action:</strong> {a['action']}</div>
    </div>
    """, unsafe_allow_html=True)
