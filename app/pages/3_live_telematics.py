"""
Page 3 — Live Fleet Telematics & In-Flight Autonomous Rerouting
Simulates real-time active fleet operations in Phoenix logistics corridor.
Detects in-flight thermal exposure spikes and issues automated corridor diversions.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.telematics_simulator import get_live_telematics_stream, trigger_dynamic_reroute

st.set_page_config(
    page_title="Live Telematics & Rerouting — ThermoRoute AI",
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
  .van-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
  }
  .status-tag {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      padding: 2px 6px;
      border-radius: 3px;
      font-weight: 700;
  }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.caption("FortyGuard Global AI Hackathon '26")
    st.caption("Track 03: Industrial & Enterprise")

st.markdown("## Live Fleet Telematics & In-Flight Autonomous Rerouting")
st.caption("Real-time telemetry stream simulating active commercial delivery vans across FortyGuard Phoenix thermal grid.")
st.markdown("---")

# Fetch active stream
vehicles = get_live_telematics_stream()

critical_count = sum(1 for v in vehicles if "CRITICAL" in v["status"])
optimal_count = sum(1 for v in vehicles if "OPTIMAL" in v["status"] or "REROUTED" in v["status"])
warning_count = sum(1 for v in vehicles if "ELEVATED" in v["status"])

# Top Status Strip
t1, t2, t3, t4 = st.columns(4)
with t1:
    st.metric(label="Active Fleet On-Road", value=f"{len(vehicles)} Units", delta="Live Telematics Stream")
with t2:
    st.metric(label="Critical Thermal Stress", value=f"{critical_count} Units", delta="Immediate Action Required", delta_color="inverse")
with t3:
    st.metric(label="Elevated Risk", value=f"{warning_count} Units", delta="Corridor Advisory", delta_color="inverse")
with t4:
    st.metric(label="Thermally Optimized", value=f"{optimal_count} Units", delta="Nominal Cell Aging", delta_color="normal")

st.markdown("---")

col_map, col_controls = st.columns([7, 5])

with col_map:
    st.markdown("### Active Transit Corridors & Real-Time Vehicle Pings")
    st.caption("Vehicles colored by thermal exposure: Red = Critical (>108°F), Orange = Elevated, Green = Optimized corridor.")

    m_live = folium.Map(location=[33.4650, -112.0800], zoom_start=12, tiles="CartoDB dark_matter")

    for v in vehicles:
        status_color = "red" if "CRITICAL" in v["status"] else ("orange" if "ELEVATED" in v["status"] else "green")
        
        popup_html = f"""
        <b>{v['id']} ({v['model']})</b><br>
        Operator: {v['operator']}<br>
        Driver: {v['driver']}<br>
        Road Temp: {v['ambient_road_temp_f']}°F<br>
        Pack Temp: {v['pack_internal_temp_f']}°F<br>
        Battery SoC: {v['soc_pct']}%<br>
        Speed: {v['speed_mph']} mph<br>
        <b>Status: {v['status']}</b>
        """
        
        folium.Marker(
            [v["lat"], v["lon"]],
            popup=popup_html,
            tooltip=f"{v['id']} | Road: {v['ambient_road_temp_f']}°F | Status: {v['status']}",
            icon=folium.Icon(color=status_color, icon="info-sign")
        ).add_to(m_live)

    st_folium(m_live, width="100%", height=480)

with col_controls:
    st.markdown("### Autonomous In-Flight Diversion Console")
    st.caption("Trigger immediate route diversion for vehicles under extreme thermal exposure:")

    selected_van_id = st.selectbox(
        "Select Active Unit",
        [v["id"] for v in vehicles],
        format_func=lambda x: f"{x} — {[v for v in vehicles if v['id'] == x][0]['model']} ({[v for v in vehicles if v['id'] == x][0]['status']})"
    )

    selected_van = [v for v in vehicles if v["id"] == selected_van_id][0]

    st.markdown(f"""
    <div class="van-card" style="border-left: 4px solid {'#ef4444' if 'CRITICAL' in selected_van['status'] else ('#f97316' if 'ELEVATED' in selected_van['status'] else '#22c55e')};">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-weight:700; font-size:1.05rem; color:#f8fafc;">{selected_van['id']} — {selected_van['model']}</span>
        <span class="status-tag" style="background:rgba(255,255,255,0.05); color:#f8fafc;">{selected_van['status']}</span>
      </div>
      <p style="font-size:0.85rem; color:#94a3b8; margin:6px 0 10px 0;">
        Operator: {selected_van['operator']} · Driver: {selected_van['driver']}<br>
        Active Roadway: {selected_van['active_corridor']}
      </p>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; border-top:1px solid #1e293b; padding-top:8px;">
        <div>
          <span style="font-size:0.75rem; color:#64748b; text-transform:uppercase;">Road Surface Temp</span>
          <div style="font-family:'JetBrains Mono', monospace; font-size:1.2rem; font-weight:700; color:#ffffff;">{selected_van['ambient_road_temp_f']:.1f}°F</div>
        </div>
        <div>
          <span style="font-size:0.75rem; color:#64748b; text-transform:uppercase;">Pack Cell Temp</span>
          <div style="font-family:'JetBrains Mono', monospace; font-size:1.2rem; font-weight:700; color:{'#ef4444' if selected_van['pack_internal_temp_f'] > 105 else '#38bdf8'};">{selected_van['pack_internal_temp_f']:.1f}°F</div>
        </div>
      </div>
      <div style="font-size:0.8rem; color:#38bdf8; margin-top:8px;">
        <strong>Recommended Intervention:</strong><br>{selected_van['recommended_reroute']}
      </div>
    </div>
    """, unsafe_allow_html=True)

    if selected_van["reroute_available"]:
        if st.button(f"⚡ Execute Autonomous Reroute on {selected_van['id']}", type="primary", use_container_width=True):
            with st.spinner(f"Transmitting waypoint diversion command to {selected_van['id']}..."):
                res = trigger_dynamic_reroute(selected_van_id)
            if res.get("success"):
                st.success(f"DIVERSION EXECUTED: {selected_van['id']} rerouted to Highway Bypass corridor! Projected thermal reduction: -{res['projected_temp_reduction_f']}°F.")
                st.rerun()
    else:
        st.info(f"{selected_van['id']} is currently operating on an optimized thermal corridor.")

# Telematics Feed Table
st.markdown("---")
st.markdown("### Fleet Telematics Stream Monitor")
telematics_rows = []
for v in vehicles:
    telematics_rows.append({
        "Unit ID": v["id"],
        "Platform": v["model"],
        "Operator": v["operator"],
        "Active Corridor": v["active_corridor"],
        "Road Surface Temp": f"{v['ambient_road_temp_f']:.1f}°F",
        "Pack Cell Temp": f"{v['pack_internal_temp_f']:.1f}°F",
        "SoC %": f"{v['soc_pct']}%",
        "Speed": f"{v['speed_mph']} mph",
        "Operating Status": v["status"]
    })

st.dataframe(pd.DataFrame(telematics_rows), use_container_width=True, hide_index=True)
