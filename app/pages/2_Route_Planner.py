"""
Page 2 — Thermal Route Engine
Core spatial routing module correlating roadway segments with FortyGuard temperature data.
Powered by FortyGuard /v1/heatmap, /v1/satellite, /v1/env_params, and /v1/streetview.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd
import sys, os, json, importlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import core.battery_model
import core.ev_energy_model
import core.route_engine
importlib.reload(core.battery_model)
importlib.reload(core.ev_energy_model)
importlib.reload(core.route_engine)

from core.fortyguard_client import FortyGuardClient
from core.route_engine import score_routes, get_city_key, CITY_DATA
from core.battery_model import BatteryDegradationModel
from core.ev_energy_model import EVEnergyModel

st.set_page_config(
    page_title="Thermal Route Engine — ThermoRoute AI",
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
  .route-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 18px;
      margin-bottom: 12px;
  }
  .badge-rec {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      padding: 2px 8px;
      border-radius: 3px;
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid rgba(34, 197, 94, 0.4);
      color: #4ade80;
      font-weight: 700;
  }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="padding: 4px 0 14px 0; border-bottom: 1px solid #172439; margin-bottom: 14px;">
      <div style="font-weight:800; font-size:1.15rem; letter-spacing:-0.02em; color:#ffffff; margin-bottom:2px;">
        ThermoRoute <span style="color:#38bdf8; font-weight:700;">AI</span>
      </div>
      <div style="font-size:0.75rem; color:#64748b; margin-bottom:8px;">
        FortyGuard Temperature API®
      </div>
      <div style="display:inline-flex; align-items:center; gap:6px; font-family:'JetBrains Mono', monospace; font-size:0.65rem; color:#38bdf8; background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.25); padding:2px 6px; border-radius:4px;">
        <span>TRACK 03 // ENTERPRISE</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

client = FortyGuardClient()
bm = BatteryDegradationModel()
em = EVEnergyModel()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## Thermal Route Engine")
st.caption("Spatial microclimate evaluation via FortyGuard Temperature API® · 2.0m Elevation Telemetry")
st.markdown("---")

# Controls
c1, c2, c3 = st.columns(3)
with c1:
    city_options = [f"{v['city']}, {v['state']}" for v in CITY_DATA.values()]
    selected_city = st.selectbox("Target Operating Hub (US Only)", city_options)
    city_key = get_city_key(selected_city)
with c2:
    vehicle_key = st.selectbox(
        "Commercial Fleet Model",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} — {ev_specs[k]['operator']}"
    )
with c3:
    fleet_size = int(st.number_input("Fleet Operational Scale (Units)", min_value=1, max_value=250000, value=500, step=1))

# Calculate scores safely
with st.spinner("Executing spatial corridor thermal analysis..."):
    result = score_routes(city_key, vehicle_key, client)

routes = result.get("route_details", result.get("routes", []))
city_center = result.get("center", [33.4484, -112.0740])
solar = result.get("solar_irradiance_wm2", 800)
satellite = result.get("satellite", {})
env_data = result.get("env_params", {})

if not routes:
    st.error("Telemetry is currently unavailable for this corridor.")
    st.stop()

# Safe min/max calculation using .get()
best_route = min(routes, key=lambda r: r.get("annual_cost_usd", 0.0))
worst_route = max(routes, key=lambda r: r.get("annual_cost_usd", 0.0))

best_cost_val = best_route.get("annual_cost_usd", 0.0)
worst_cost_val = worst_route.get("annual_cost_usd", 0.0)
savings_per_van = max(0.0, worst_cost_val - best_cost_val)
fleet_savings = savings_per_van * fleet_size

# Top Summary Strip
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric(
        label="High-Stress Corridor (Worst)",
        value=f"{worst_route.get('avg_temp_f', 110.0):.1f}°F",
        delta=f"${worst_cost_val:,.0f}/unit/yr total",
        delta_color="inverse"
    )
with s2:
    st.metric(
        label="Thermally Optimal Route (Best)",
        value=f"{best_route.get('avg_temp_f', 95.0):.1f}°F",
        delta=f"${best_cost_val:,.0f}/unit/yr total",
        delta_color="normal"
    )
with s3:
    st.metric(
        label="Unit Operational Preservation",
        value=f"${savings_per_van:,.0f}/yr",
        delta=f"-{round(savings_per_van / worst_cost_val * 100, 1) if worst_cost_val > 0 else 0}% expense",
        delta_color="normal"
    )
with s4:
    st.metric(
        label=f"Annual Fleet Value ({fleet_size} Units)",
        value=f"${fleet_savings:,.0f}/yr",
        delta="Comprehensive ROI",
        delta_color="normal"
    )

st.markdown("---")

# Spatial Map
st.markdown("### Spatial Corridor Telemetry & Microclimate Map")
st.caption("Real turn-by-turn road geometry colored by thermal exposure. FortyGuard Temperature API 2-meter resolution.")

m = folium.Map(location=city_center, zoom_start=12, tiles="CartoDB dark_matter")

for route in routes:
    # Use real turn-by-turn road geometry if available, else waypoints
    road_geom = route.get("road_geometry", [])
    if not road_geom:
        waypoints = route.get("waypoints", [])
        road_geom = [[wp["lat"], wp["lon"]] for wp in waypoints]
    
    if not road_geom:
        continue

    color = route.get("color", "#38bdf8")
    is_rec = (route.get("name") == best_route.get("name"))
    weight = 5 if is_rec else 3
    dash = None if is_rec else "6 4"

    folium.PolyLine(
        road_geom,
        color=color,
        weight=weight,
        opacity=0.9,
        dash_array=dash,
        tooltip=f"{route.get('name', 'Route')} | Avg: {route.get('avg_temp_f', 100):.1f}°F | Total: ${route.get('annual_cost_usd', 0):,.0f}/yr"
    ).add_to(m)

    # Roadway waypoint markers
    for i, (wp, temp) in enumerate(zip(route.get("waypoints", []), route.get("segment_temps", []))):
        if i % 2 == 0:
            folium.CircleMarker(
                [wp["lat"], wp["lon"]],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                tooltip=f"{wp.get('name', 'Point')}: {temp:.1f}°F"
            ).add_to(m)

# Origin / Destination
if routes and routes[0].get("waypoints"):
    start_pt = routes[0]["waypoints"][0]
    end_pt = routes[0]["waypoints"][-1]
    folium.Marker([start_pt["lat"], start_pt["lon"]], popup="Logistics Hub / Depot",
                  icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
    folium.Marker([end_pt["lat"], end_pt["lon"]], popup="Target Delivery Zone",
                  icon=folium.Icon(color="red", icon="ok-sign")).add_to(m)

st_folium(m, width="100%", height=460)

# Corridor Breakdown Cards
st.markdown("### Candidate Corridor Assessment (3-Component Cost Model)")
r_cols = st.columns(len(routes))

for col, route in zip(r_cols, routes):
    is_rec = (route.get("name") == best_route.get("name"))
    status_color = route.get("color", "#38bdf8")
    
    with col:
        st.markdown(f"""
        <div class="route-card" style="border-top: 3px solid {status_color};">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-weight:700; font-size:0.95rem; color:#f8fafc;">{route.get('name', 'Route').split('—')[0].strip()}</span>
            {'<span class="badge-rec">RECOMMENDED</span>' if is_rec else ''}
          </div>
          <div style="font-family:'JetBrains Mono', monospace; font-size:1.8rem; font-weight:700; color:{status_color}; margin: 4px 0;">
            {route.get('avg_temp_f', 100):.1f}°F
          </div>
          <p style="font-size:0.8rem; color:#94a3b8; margin-bottom:8px;">
            Distance: {route.get('distance_miles', 0)} mi · Transit: {route.get('duration_minutes', 0)} min<br>
            Effective Range: {route.get('effective_range_miles', 0)} mi ({route.get('range_reduction_pct', 0)}% heat loss)
          </p>
          <div style="border-top:1px solid #1e293b; padding-top:8px;">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#94a3b8; margin-bottom:3px;">
              <span>⚡ Battery Degradation:</span>
              <span style="font-family:'JetBrains Mono', monospace; color:#f8fafc; font-weight:600;">${route.get('degradation_cost_usd', 0):,.0f}</span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#94a3b8; margin-bottom:3px;">
              <span>🔋 Energy & AC Surcharge:</span>
              <span style="font-family:'JetBrains Mono', monospace; color:#f8fafc; font-weight:600;">${route.get('energy_penalty_usd', 0):,.0f}</span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#94a3b8; margin-bottom:6px;">
              <span>⏱️ Range & Charging Overhead:</span>
              <span style="font-family:'JetBrains Mono', monospace; color:#f8fafc; font-weight:600;">${route.get('range_overhead_usd', 0):,.0f}</span>
            </div>
            <div style="border-top:1px dashed #334155; padding-top:6px; display:flex; justify-content:space-between; font-family:'JetBrains Mono', monospace; font-size:0.95rem; color:#38bdf8; font-weight:700;">
              <span>Total Annual / Unit:</span>
              <span>${route.get('annual_cost_usd', 0):,.0f}</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Segment Telemetry Plot
st.markdown("#### Point-by-Point Roadway Temperature Profile")
fig_seg = go.Figure()
for route in routes:
    segs = route.get("segment_temps", [route.get("avg_temp_f", 100)] * 5)
    fig_seg.add_trace(go.Scatter(
        x=list(range(1, len(segs) + 1)),
        y=segs,
        mode="lines+markers",
        name=route.get("name", "Route").split("—")[0].strip(),
        line=dict(color=route.get("color", "#38bdf8"), width=2),
        marker=dict(size=6)
    ))
fig_seg.add_hline(y=95, line_dash="dash", line_color="#eab308", annotation_text="Elevated Exposure (95°F)")
fig_seg.add_hline(y=108, line_dash="dash", line_color="#ef4444", annotation_text="Critical Stress (108°F)")
fig_seg.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8"),
    xaxis=dict(title="Roadway Waypoint Index", gridcolor="#1e293b"),
    yaxis=dict(title="Temperature (°F)", gridcolor="#1e293b"),
    height=320,
    margin=dict(l=20, r=20, t=20, b=20)
)
st.plotly_chart(fig_seg, use_container_width=True)

# FortyGuard Environmental Telemetry Strip
st.markdown("### Regional Environmental Telemetry (/v1/env_params & /v1/satellite)")
e1, e2, e3, e4, e5 = st.columns(5)
with e1:
    st.metric(label="Heat Index", value=f"{env_data.get('heat_index_f', 118):.0f}°F")
with e2:
    st.metric(label="Solar Irradiance", value=f"{env_data.get('solar_irradiance_wm2', 950):.0f} W/m²")
with e3:
    st.metric(label="Thermal Persistence", value=f"{env_data.get('persistence_hours', 9.3):.1f}h")
with e4:
    st.metric(label="Canopy Coverage", value=f"{satellite.get('vegetation_pct', 8.2):.1f}%")
with e5:
    st.metric(label="Surface Pavement", value=f"{satellite.get('pavement_pct', 38.7):.1f}%")
