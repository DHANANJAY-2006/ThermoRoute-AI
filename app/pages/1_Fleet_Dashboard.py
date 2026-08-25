"""
Page 1 — Regional Fleet Risk Monitor
Provides high-level regional thermal exposure indices across primary US logistics hubs.
Powered by FortyGuard Temperature API /v1/heatmap and /v1/env_params.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os, json, importlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import core.fortyguard_client
import core.battery_model
import core.route_engine
import core.alert_manager
importlib.reload(core.fortyguard_client)
importlib.reload(core.battery_model)
importlib.reload(core.route_engine)
importlib.reload(core.alert_manager)

from core.fortyguard_client import FortyGuardClient
from core.battery_model import BatteryDegradationModel
from core.route_engine import multi_city_snapshot, CITY_DATA
from core.alert_manager import evaluate

st.set_page_config(
    page_title="Fleet Risk Monitor — ThermoRoute AI",
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
  .alert-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
  }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-box">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <span style="font-weight:800; font-size:1.05rem; letter-spacing:0.03em; color:#ffffff;">THERMOROUTE<span style="color:#38bdf8;">.AI</span></span>
        <span style="font-family:'JetBrains Mono', monospace; font-size:0.65rem; font-weight:700; padding:2px 6px; border-radius:3px; background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.35); color:#38bdf8;">v1.0 PRO</span>
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:10px;">Hyperlocal Fleet Thermal Intelligence</div>
      <div style="display:flex; align-items:center; gap:6px; font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:#4ade80; background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.2); padding:4px 8px; border-radius:4px; margin-bottom:8px;">
        <span style="width:6px; height:6px; border-radius:50%; background:#4ade80; box-shadow:0 0 6px #4ade80; display:inline-block;"></span>
        <span>FORTYGUARD API // ACTIVE</span>
      </div>
      <div style="font-family:'JetBrains Mono', monospace; font-size:0.66rem; color:#64748b; border-top:1px solid #1e293b; padding-top:6px;">
        TRACK 03: INDUSTRIAL & ENTERPRISE
      </div>
    </div>
    """, unsafe_allow_html=True)

client = FortyGuardClient()
bm = BatteryDegradationModel()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## Regional Fleet Thermal Risk Monitor")
st.caption("Cross-regional microclimate telemetry synthesized from FortyGuard Temperature API® · 2m Elevation")
st.markdown("---")

# Controls
c1, c2 = st.columns(2)
with c1:
    vehicle_key = st.selectbox(
        "Commercial Fleet Model",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} — {ev_specs[k]['operator']}"
    )
with c2:
    fleet_size = int(st.number_input("Operational Fleet Size per Territory", min_value=1, max_value=50000, value=500, step=1))

# Fetch snapshot
with st.spinner("Querying FortyGuard Temperature API telemetry across US logistics corridors..."):
    snapshots = multi_city_snapshot(client)

# Top KPI strip
t1, t2, t3, t4 = st.columns(4)
highest_risk = max(snapshots, key=lambda s: s["temp_f"])
lowest_risk = min(snapshots, key=lambda s: s["temp_f"])

with t1:
    st.metric(
        label="Peak Thermal Exposure",
        value=f"{highest_risk['temp_f']}°F",
        delta=f"{highest_risk['city']} ({highest_risk['risk_level']})",
        delta_color="inverse"
    )
with t2:
    st.metric(
        label="Maximum Chemical Aging Rate",
        value=f"{bm.degradation_factor(highest_risk['temp_f']):.2f}x",
        delta="Arrhenius Acceleration",
        delta_color="inverse"
    )
with t3:
    st.metric(
        label="Moderate Corridor Exposure",
        value=f"{lowest_risk['temp_f']}°F",
        delta=f"{lowest_risk['city']} (Base Risk)",
        delta_color="normal"
    )
with t4:
    total_fleet_impact = sum(
        bm.annual_degradation_cost(s["temp_f"], vehicle_key)["extra_annual_cost_usd"] * fleet_size
        for s in snapshots
    )
    st.metric(
        label=f"Multi-Hub Risk Exposure ({fleet_size*4:,} Units)",
        value=f"${total_fleet_impact:,.0f}/yr",
        delta="Cumulative CapEx Risk",
        delta_color="inverse"
    )

st.markdown("---")

# Multi-City Comparison Chart
st.markdown("### Cross-Territory Roadway Ambient Temperature vs Nominal Baseline (77°F)")
fig_cities = go.Figure()
cities_list = [s["city"] for s in snapshots]
temps_list = [s["temp_f"] for s in snapshots]
colors_list = [bm.risk_color(t) for t in temps_list]

fig_cities.add_trace(go.Bar(
    x=cities_list,
    y=temps_list,
    marker_color=colors_list,
    text=[f"{t}°F" for t in temps_list],
    textposition="outside"
))
fig_cities.add_hline(y=77, line_dash="dot", line_color="#22c55e", annotation_text="Nominal Baseline (77°F)")
fig_cities.add_hline(y=95, line_dash="dash", line_color="#eab308", annotation_text="Accelerated Degradation Threshold (95°F)")
fig_cities.add_hline(y=108, line_dash="dash", line_color="#ef4444", annotation_text="Critical Stress Threshold (108°F)")
fig_cities.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8"),
    yaxis=dict(title="Roadway Ambient Air Temperature (°F)", gridcolor="#1e293b", range=[50, 130]),
    xaxis=dict(gridcolor="#1e293b"),
    height=360,
    margin=dict(l=20, r=20, t=20, b=20)
)
st.plotly_chart(fig_cities, use_container_width=True)

# Territory breakdown table
st.markdown("### Operational Risk Table by Logistics Hub")
table_data = []
for s in snapshots:
    t = s["temp_f"]
    factor = bm.degradation_factor(t)
    cost_info = bm.annual_degradation_cost(t, vehicle_key)
    fleet_extra = cost_info["extra_annual_cost_usd"] * fleet_size
    table_data.append({
        "Operating Hub": f"{s['city']}, {s['state']}",
        "Roadway Temp (2m AGL)": f"{t:.1f}°F",
        "Heat Index": f"{s['heat_index_f']:.0f}°F",
        "Degradation Rate": f"{factor:.2f}x",
        "Expected Lifespan": f"{cost_info['effective_lifespan_years']} Years",
        "Annual Cost / Unit": f"${cost_info['heat_annual_cost_usd']:,.0f}",
        "Annual Territory Risk": f"${fleet_extra:,.0f}",
        "Status": s["risk_level"].upper()
    })

st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

# Alerts section
st.markdown("---")
st.markdown("### Autonomous Decision Support Alerts")
st.caption("Real-time alert dispatch based on FortyGuard temperature persistence layers:")

for s in snapshots:
    deg = bm.degradation_factor(s["temp_f"])
    alerts = evaluate(s["temp_f"], deg, s["persistence_hours"], s["city"])
    for alert in alerts:
        if alert["level"] != "NOMINAL STATUS":
            st.markdown(f"""
            <div class="alert-card" style="border-left: 4px solid {alert['color']};">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:{alert['color']}; font-size:0.9rem;">{alert['level']} // {s['city'].upper()}</span>
                <span style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#94a3b8;">{alert['time']}</span>
              </div>
              <p style="margin:6px 0; font-size:0.9rem; color:#e2e8f0;">{alert['message']}</p>
              <div style="font-size:0.8rem; color:#38bdf8; font-weight:600;">Recommended Action: {alert['action']}</div>
            </div>
            """, unsafe_allow_html=True)
