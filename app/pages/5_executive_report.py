"""
Page 5 — Executive Risk Brief & Audit Report
Generates formal operations briefs using FortyGuard /v1/heat_intelligence multi-dimensional synthesis.
Outputs clean executive PDF briefings for operations leadership.
"""

import streamlit as st
from fpdf import FPDF
from datetime import datetime
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.fortyguard_client import FortyGuardClient
from core.route_engine import score_routes, get_city_key, CITY_DATA
from core.battery_model import BatteryDegradationModel
from core.cost_calculator import fleet_roi_summary

st.set_page_config(
    page_title="Executive Risk Brief — ThermoRoute AI",
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
  .panel-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 16px;
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


def _pdf_clean(text: str) -> str:
    """Sanitizes text for standard Latin-1 PDF output."""
    if not text:
        return ""
    text_str = str(text)
    mapping = {
        "—": "-",
        "–": "-",
        "’": "'",
        "‘": "'",
        '“': '"',
        '”': '"',
        "®": "(R)",
        "°": " deg ",
        "•": "-",
    }
    for old, new in mapping.items():
        text_str = text_str.replace(old, new)
    return text_str.encode("latin-1", "replace").decode("latin-1")


st.markdown("## Executive Thermal Risk Brief")
st.caption("Multi-dimensional intelligence synthesis powered by FortyGuard /v1/heat_intelligence endpoint.")
st.markdown("---")

# Controls
c1, c2, c3 = st.columns(3)
with c1:
    city_options = [f"{v['city']}, {v['state']}" for v in CITY_DATA.values()]
    selected_city = st.selectbox("Operational Territory", city_options)
    city_key = get_city_key(selected_city)
with c2:
    vehicle_key = st.selectbox(
        "Commercial Platform",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} — {ev_specs[k]['operator']}"
    )
with c3:
    fleet_size = st.number_input("Operating Fleet Units", min_value=1, max_value=250000, value=500, step=25)

if st.button("Generate Executive Brief", type="primary", use_container_width=True):
    with st.spinner("Compiling multi-dimensional thermal intelligence brief..."):
        result = score_routes(city_key, vehicle_key, client)
        heat_intel = client.get_heat_intelligence(f"{result.get('center', [33.4484, -112.0740])[0]},{result.get('center', [33.4484, -112.0740])[1]}")

    routes = result.get("route_details", result.get("routes", []))
    if not routes:
        st.error("No telemetry available for this territory.")
        st.stop()

    best_route = min(routes, key=lambda r: r.get("annual_cost_usd", 0.0))
    worst_route = max(routes, key=lambda r: r.get("annual_cost_usd", 0.0))
    savings_per_van = max(0.0, worst_route.get("annual_cost_usd", 0.0) - best_route.get("annual_cost_usd", 0.0))
    roi = fleet_roi_summary(savings_per_van, fleet_size)
    env = result.get("env_params", {})
    sat = result.get("satellite", {})

    st.markdown("---")
    st.markdown(f"### Operational Briefing: {selected_city}")
    st.caption(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} · Primary Telemetry: FortyGuard Temperature API®")

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric(label="Overall Risk Index", value=f"{heat_intel.get('overall_risk_score', 94.2):.1f}/100")
    with r2:
        st.metric(label="Geographic Exposure", value=heat_intel.get("geographic_risk", "Extreme").upper())
    with r3:
        st.metric(label="Urban Core Microclimate", value=heat_intel.get("urban_risk", "Critical").upper())
    with r4:
        st.metric(label="Fleet CapEx Delta", value=f"${roi['total_annual_savings_usd']:,.0f}/yr")

    # Briefing Body
    st.markdown("#### Environmental Telemetry Verification")
    st.markdown(f"""
    | Parameter | Telemetry Value | Measurement Source |
    | :--- | :--- | :--- |
    | **Ambient Surface Temp** | {worst_route.get('avg_temp_f', 110):.1f}°F (Peak Exposure Corridor) | FortyGuard /v1/heatmap · 2m Elevation |
    | **Heat Index** | {env.get('heat_index_f', 118):.0f}°F | FortyGuard /v1/env_params |
    | **Direct Solar Irradiance** | {env.get('solar_irradiance_wm2', 950):.0f} W/m² | FortyGuard /v1/env_params |
    | **Thermal Persistence Duration** | {env.get('persistence_hours', 9.3):.1f} Continuous Hours | FortyGuard /v1/env_params · Persistence Layer |
    | **Urban Canopy Shielding** | {sat.get('vegetation_pct', 8.2):.1f}% | FortyGuard /v1/satellite |
    | **Air Quality Index (AQI)** | {env.get('aqi', 42)} | FortyGuard /v1/env_params |
    """)

    st.markdown("#### Corridor Economic Comparison")
    st.markdown(f"""
    | Transit Corridor | Mean Temperature | Degradation Rate | Annual Battery Depreciation |
    | :--- | :--- | :--- | :--- |
    | **{worst_route.get('name', 'Unmanaged')}** (Unmanaged Baseline) | {worst_route.get('avg_temp_f', 110):.1f}°F | {worst_route.get('degradation_factor', 3.8):.2f}x | ${worst_route.get('annual_cost_usd', 0):,.0f} / unit / yr |
    | **{best_route.get('name', 'Optimized')}** (Thermally Managed) | {best_route.get('avg_temp_f', 95):.1f}°F | {best_route.get('degradation_factor', 2.0):.2f}x | ${best_route.get('annual_cost_usd', 0):,.0f} / unit / yr |
    | **Net Annual Unit Benefit** | — | — | **+${savings_per_van:,.0f} / unit / yr** |
    """)

    st.markdown("#### Autonomous AI Operational Synthesis")
    st.info(heat_intel.get("summary", "FortyGuard heat intelligence analysis active."))

    st.markdown("#### Recommended Fleet Protocol")
    st.markdown(f"""
    1. **Mandate Corridor Transition:** Reroute {fleet_size:,} active units to {best_route.get('name', 'Optimized Route')} during peak thermal windows (10:00–17:00).
    2. **Shift Schedule Optimization:** Utilize FortyGuard 12-hour forecast to advance high-draw payload runs to early morning intervals.
    3. **Depot Pre-Conditioning:** Initiate pack thermal conditioning protocols during depot dock staging.
    4. **Continuous Telemetry Tracking:** Monitor real-time microclimate persistence via ThermoRoute AI telemetry stream.
    """)

    # PDF Export
    st.markdown("---")
    st.markdown("### Export Official Briefing Document")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, _pdf_clean("ThermoRoute AI - Executive Risk Brief"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _pdf_clean(f"Operational Hub: {selected_city} | Date: {datetime.now().strftime('%B %d, %Y')}"), ln=True)
    pdf.cell(0, 6, _pdf_clean("Telemetry Foundation: FortyGuard Temperature API(R) | Track 03 Industrial & Enterprise"), ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, _pdf_clean("Executive Financial Summary"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf_rows = [
        ("Annual Savings Per Vehicle", f"${savings_per_van:,.0f}"),
        ("Total Annual Fleet Value", f"${roi['total_annual_savings_usd']:,.0f}"),
        ("Capital Payback Horizon", f"{roi['payback_months']:.1f} Months"),
        ("5-Year Cumulative Net Benefit", f"${roi['five_year_net_usd']:,.0f}"),
    ]
    for k, v in pdf_rows:
        pdf.cell(90, 7, _pdf_clean(k))
        pdf.cell(0, 7, _pdf_clean(v), ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, _pdf_clean("Mandated Operational Protocol"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, _pdf_clean(
        f"Reroute {fleet_size:,} active units from {worst_route.get('name', 'Unmanaged')} ({worst_route.get('avg_temp_f', 110):.1f}F average) "
        f"to {best_route.get('name', 'Optimized')} ({best_route.get('avg_temp_f', 95):.1f}F average). "
        f"Projected fleet-wide asset preservation value: ${roi['total_annual_savings_usd']:,.0f} annually."
    ))

    pdf_output = pdf.output()
    st.download_button(
        label="Download Executive PDF Brief",
        data=bytes(pdf_output),
        file_name=f"ThermoRoute_Executive_Brief_{selected_city.replace(', ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
else:
    st.markdown("""
    <div class="panel-card" style="text-align:center; padding:48px;">
      <h3 style="margin-top:0; color:#f8fafc;">Executive Report Generation</h3>
      <p style="color:#94a3b8; max-width:600px; margin:0 auto;">
        Select an operational territory and fleet specification above, then click <strong>Generate Executive Brief</strong>.
        The brief compiles multi-dimensional data from FortyGuard's <code>/v1/heat_intelligence</code> endpoint into an operations briefing with PDF export.
      </p>
    </div>
    """, unsafe_allow_html=True)
