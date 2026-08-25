"""
Page 2 — Route Planner
THE CORE FEATURE of ThermoRoute AI.
Shows thermal route comparison on interactive map + cost breakdown.
Uses FortyGuard heatmap + satellite + env_params endpoints.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.fortyguard_client import FortyGuardClient
from core.route_engine import score_routes, get_city_key, CITY_DATA
from core.battery_model import BatteryDegradationModel
from core.cost_calculator import fleet_roi_summary

st.set_page_config(page_title="Route Planner — ThermoRoute AI",
                   page_icon="🗺️", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background:linear-gradient(160deg,#04091C 0%,#060E22 50%,#091A35 100%);
}
[data-testid="stSidebar"] { background-color:#0d1627; }
h1,h2,h3 { color:#ffffff !important; }
p,li,label { color:#a9b6c6 !important; }
</style>
""", unsafe_allow_html=True)

client = FortyGuardClient()
bm = BatteryDegradationModel()

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🗺️ Thermal Route Planner")
st.caption(f"FortyGuard Temperature API® · {client.mode} · US cities only")

# ── Controls ──────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    city_options = [f"{v['city']}, {v['state']}" for v in CITY_DATA.values()]
    selected_city = st.selectbox("📍 Select City (US Only)", city_options)
    city_key = get_city_key(selected_city)

with col2:
    vehicle_key = st.selectbox(
        "🚐 Vehicle Type",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['icon']} {ev_specs[k]['name']}"
    )

with col3:
    fleet_size = st.number_input("🚐 Fleet Size", min_value=1, max_value=500000,
                                  value=500, step=50)

st.divider()

# ── Score routes ──────────────────────────────────────────────────────────────
with st.spinner("🌡️ Analysing routes with FortyGuard temperature data..."):
    result = score_routes(city_key, vehicle_key, client)

routes = result["route_details"]
city_center = result["center"]
solar = result.get("solar_irradiance_wm2", 800)
satellite = result.get("satellite", {})

# ── Savings Hero ──────────────────────────────────────────────────────────────
best_route = min(routes, key=lambda r: r["avg_temp_f"])
worst_route = max(routes, key=lambda r: r["avg_temp_f"])
best_cost = bm.annual_degradation_cost(best_route["effective_temp_f"],
                                        vehicle_key, solar)
worst_cost = bm.annual_degradation_cost(worst_route["effective_temp_f"],
                                         vehicle_key, solar)
savings_per_van = worst_cost["heat_annual_cost_usd"] - best_cost["heat_annual_cost_usd"]
fleet_savings = savings_per_van * fleet_size

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("🔥 Hottest Route", f"{worst_route['avg_temp_f']:.0f}°F",
              f"${worst_cost['heat_annual_cost_usd']:,.0f}/van/yr")
col_b.metric("🌿 Coolest Route", f"{best_route['avg_temp_f']:.0f}°F",
              f"${best_cost['heat_annual_cost_usd']:,.0f}/van/yr")
col_c.metric("💰 Savings Per Van", f"${savings_per_van:,.0f}/yr",
              f"{round(savings_per_van / worst_cost['heat_annual_cost_usd'] * 100, 0):.0f}% less damage")
col_d.metric(f"💸 Fleet ({fleet_size:,} vans)",
              f"${fleet_savings:,.0f}/yr", "annual battery savings")

st.divider()

# ── Map ───────────────────────────────────────────────────────────────────────
st.markdown("### 🗺️ Route Thermal Map — Street-Level FortyGuard Temperature Data")

m = folium.Map(location=city_center, zoom_start=12,
               tiles="CartoDB dark_matter")

# Plot each route
for route in routes:
    latlons = [[wp["lat"], wp["lon"]] for wp in route["waypoints"]]
    color = route["color"]
    weight = 5 if route == best_route else 3
    dash = None if route == best_route else "10 5"

    folium.PolyLine(
        latlons,
        color=color,
        weight=weight,
        opacity=0.85,
        dash_array=dash,
        tooltip=f"{route['name']} | Avg {route['avg_temp_f']:.0f}°F | {route['risk_level']}"
    ).add_to(m)

    # Temp markers along route
    for i, (wp, temp) in enumerate(
            zip(route["waypoints"], route.get("segment_temps", []))):
        if i % 3 == 0:  # every 3rd waypoint
            folium.CircleMarker(
                [wp["lat"], wp["lon"]],
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                tooltip=f"{wp['name']}: {temp:.0f}°F"
            ).add_to(m)

# Start/End markers
start = routes[0]["waypoints"][0]
end = routes[0]["waypoints"][-1]
folium.Marker([start["lat"], start["lon"]],
              popup="📦 Distribution Center",
              icon=folium.Icon(color="blue", icon="home")).add_to(m)
folium.Marker([end["lat"], end["lon"]],
              popup="📍 Delivery Zone",
              icon=folium.Icon(color="red", icon="flag")).add_to(m)

st_folium(m, width="100%", height=480)

# ── Route Legend ──────────────────────────────────────────────────────────────
leg_cols = st.columns(len(routes))
for col, route in zip(leg_cols, routes):
    r_cost = bm.annual_degradation_cost(route["effective_temp_f"], vehicle_key, solar)
    with col:
        is_best = (route == best_route)
        st.markdown(f"""
<div style="background:rgba(23,105,176,0.1);border:2px solid {route['color']};
     border-radius:10px;padding:12px;text-align:center;
     {'box-shadow:0 0 12px ' + route['color'] + '88;' if is_best else ''}">
  {'<div style="color:#22c55e;font-weight:700;font-size:0.75rem;">✅ RECOMMENDED</div>' if is_best else ''}
  <div style="color:#fff;font-weight:700;">{route['name']}</div>
  <div style="color:{route['color']};font-size:1.6rem;font-weight:900;">{route['avg_temp_f']:.0f}°F</div>
  <div style="color:#a9b6c6;font-size:0.8rem;">{route['distance_miles']} mi · {route['duration_minutes']} min</div>
  <div style="color:#a9b6c6;font-size:0.8rem;">🌿 {route['shade_pct']}% shade</div>
  <hr style="border-color:#1e3a5f;margin:8px 0;">
  <div style="color:#ffda00;font-weight:700;">{r_cost['degradation_factor']:.2f}× degradation</div>
  <div style="color:#a9b6c6;font-size:0.85rem;">${r_cost['heat_annual_cost_usd']:,.0f}/van/yr</div>
</div>
        """, unsafe_allow_html=True)

st.divider()

# ── Route Comparison Table ────────────────────────────────────────────────────
st.markdown("### 📊 Route Comparison — Annual Cost Per Van")

import pandas as pd
rows = []
for route in routes:
    rc = bm.annual_degradation_cost(route["effective_temp_f"], vehicle_key, solar)
    rows.append({
        "Route": route["name"],
        "Avg Temp (°F)": f"{route['avg_temp_f']:.0f}",
        "Shade %": f"{route['shade_pct']}%",
        "Degradation": f"{rc['degradation_factor']:.2f}×",
        "Annual Cost/Van": f"${rc['heat_annual_cost_usd']:,.0f}",
        "Extra vs Ideal": f"${rc['extra_annual_cost_usd']:,.0f}",
        "Risk Level": route["risk_level"]
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

# ── Segment Temperature Chart ─────────────────────────────────────────────────
st.markdown("### 🌡️ Temperature Per Road Segment")
fig = go.Figure()
for route in routes:
    segs = route.get("segment_temps", [route["avg_temp_f"]] * 5)
    fig.add_trace(go.Scatter(
        x=list(range(1, len(segs) + 1)),
        y=segs,
        mode="lines+markers",
        name=route["name"].split("—")[0].strip(),
        line=dict(color=route["color"], width=2),
        marker=dict(size=7)
    ))
fig.add_hline(y=95, line_dash="dot", line_color="#eab308",
               annotation_text="⚠️ High Risk (95°F)")
fig.add_hline(y=108, line_dash="dot", line_color="#ef4444",
               annotation_text="🔴 Critical (108°F)")
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#a9b6c6",
    xaxis_title="Route Segment #",
    yaxis_title="Temperature (°F)",
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    height=350
)
st.plotly_chart(fig, use_container_width=True)

# ── Environmental Data ────────────────────────────────────────────────────────
st.divider()
st.markdown("### 🌬️ FortyGuard Environmental Parameters")
env = result.get("env_params", {})
e1, e2, e3, e4 = st.columns(4)
e1.metric("🌡️ Heat Index", f"{env.get('heat_index_f', 118):.0f}°F")
e2.metric("☀️ Solar Irradiance", f"{env.get('solar_irradiance_wm2', 950):.0f} W/m²")
e3.metric("💧 Humidity", f"{env.get('humidity_pct', 14):.0f}%")
e4.metric("⏱️ Heat Persistence", f"{env.get('persistence_hours', 9.3):.1f} hrs")

sat = result.get("satellite", {})
s1, s2, s3 = st.columns(3)
s1.metric("🌿 Vegetation Cover", f"{sat.get('vegetation_pct', 8.2):.1f}%",
           "shade potential")
s2.metric("🏢 Building Cover", f"{sat.get('building_pct', 43.1):.1f}%",
           "radiated heat source")
s3.metric("🛣️ Pavement Cover", f"{sat.get('pavement_pct', 38.7):.1f}%",
           "heat absorption")

st.caption("⚡ ThermoRoute AI · FortyGuard Hackathon '26 · Track 03 Industrial & Enterprise")
