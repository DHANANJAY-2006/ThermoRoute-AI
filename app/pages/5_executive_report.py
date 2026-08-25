"""
Page 5 — Executive Report
Auto-generated fleet thermal risk report using FortyGuard /v1/heat_intelligence.
Combines all data sources into a downloadable summary.
"""

import streamlit as st
from fpdf import FPDF
import io, sys, os, json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.fortyguard_client import FortyGuardClient
from core.route_engine import score_routes, get_city_key, CITY_DATA
from core.battery_model import BatteryDegradationModel
from core.cost_calculator import fleet_roi_summary

st.set_page_config(page_title="Executive Report — ThermoRoute AI",
                   page_icon="📄", layout="wide")

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

st.markdown("## 📄 Executive Fleet Thermal Risk Report")
st.caption(
    "Auto-generated using FortyGuard /v1/heat_intelligence endpoint + all data sources. "
    "Ready to send to your Operations Director."
)

col1, col2, col3 = st.columns(3)
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
with col3:
    fleet_size = st.number_input("Fleet Size", 1, 500000, 500, step=50)

if st.button("📊 Generate Executive Report", type="primary", use_container_width=True):
    with st.spinner("🤖 Generating report using FortyGuard Heat Intelligence API..."):
        result = score_routes(city_key, vehicle_key, client)
        heat_intel = client.get_heat_intelligence(
            f"{result['center'][0]},{result['center'][1]}"
        )

    routes = result["route_details"]
    best_route = min(routes, key=lambda r: r["avg_temp_f"])
    worst_route = max(routes, key=lambda r: r["avg_temp_f"])
    best_cost = bm.annual_degradation_cost(best_route["effective_temp_f"], vehicle_key)
    worst_cost = bm.annual_degradation_cost(worst_route["effective_temp_f"], vehicle_key)
    savings_per_van = worst_cost["heat_annual_cost_usd"] - best_cost["heat_annual_cost_usd"]
    roi = fleet_roi_summary(savings_per_van, fleet_size)
    env = result.get("env_params", {})
    sat = result.get("satellite", {})

    # ── On-screen report ──────────────────────────────────────────────────────
    st.divider()
    st.markdown(f"""
## 📋 Thermal Risk Report — {selected_city}
**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')} | **Powered by:** FortyGuard Temperature API®
    """)

    r1, r2, r3 = st.columns(3)
    r1.metric("Overall Risk Score", f"{heat_intel.get('overall_risk_score', 94.2):.0f}/100")
    r2.metric("Geographic Risk", heat_intel.get("geographic_risk", "Extreme").title())
    r3.metric("Urban Heat Risk", heat_intel.get("urban_risk", "Critical").title())

    st.markdown("### 🌡️ Thermal Conditions")
    st.markdown(f"""
| Parameter | Value | Source |
|---|---|---|
| Ambient Temperature | {worst_route['avg_temp_f']:.0f}°F (hot route) | FortyGuard /v1/heatmap · exceedance layer |
| Heat Index | {env.get('heat_index_f', 118):.0f}°F | FortyGuard /v1/env_params |
| Solar Irradiance | {env.get('solar_irradiance_wm2', 950):.0f} W/m² | FortyGuard /v1/env_params |
| Heat Persistence | {env.get('persistence_hours', 9.3):.1f} hrs above threshold | FortyGuard /v1/env_params · persistence layer |
| Vegetation Coverage | {sat.get('vegetation_pct', 8.2):.1f}% | FortyGuard /v1/satellite |
| AQI | {env.get('aqi', 42)} | FortyGuard /v1/env_params |
    """)

    st.markdown("### 🔋 Route Comparison")
    st.markdown(f"""
| Route | Avg Temp | Degradation | Annual Cost/Van |
|---|---|---|---|
| {worst_route['name']} (Current) | {worst_route['avg_temp_f']:.0f}°F | {worst_cost['degradation_factor']:.2f}× | ${worst_cost['heat_annual_cost_usd']:,.0f} |
| {best_route['name']} (Recommended) | {best_route['avg_temp_f']:.0f}°F | {best_cost['degradation_factor']:.2f}× | ${best_cost['heat_annual_cost_usd']:,.0f} |
| **Saving Per Van** | — | — | **${savings_per_van:,.0f}/yr** |
    """)

    st.markdown("### 💰 Financial Impact")
    st.markdown(f"""
| Metric | Value |
|---|---|
| Fleet Size | {fleet_size:,} vans |
| Savings Per Van | ${savings_per_van:,.0f}/year |
| Total Annual Fleet Savings | ${roi['total_annual_savings_usd']:,.0f} |
| ThermoRoute AI Cost | ${roi['product_cost_annual_usd']:,.0f}/year |
| Net Annual Benefit | ${roi['net_annual_benefit_usd']:,.0f} |
| Payback Period | {roi['payback_months']:.1f} months |
| 5-Year Net Benefit | ${roi['five_year_net_usd']:,.0f} |
    """)

    st.markdown("### 📝 AI Assessment")
    st.info(heat_intel.get("summary", "FortyGuard heat intelligence analysis unavailable in demo mode."))

    st.markdown("### ✅ Recommendations")
    st.markdown(f"""
1. **Switch to {best_route['name']}** for all deliveries during peak hours (10AM–6PM)
2. **Shift urgent deliveries to early AM** (before 9AM) using the 12-hour forecast
3. **Pre-cool vehicles** during the loading window to reduce initial battery temperature
4. **Monitor Fleet Dashboard daily** for city-wide risk changes
5. **Deploy ThermoRoute AI** across all {fleet_size:,} vans for ${roi['total_annual_savings_usd']:,.0f} annual savings
    """)

    # ── PDF Download ──────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📥 Download PDF Report")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "ThermoRoute AI — Executive Report", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"City: {selected_city}  |  Generated: {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.cell(0, 8, "Powered by FortyGuard Temperature API(R)  |  FortyGuard Hackathon '26 Track 03", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Financial Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    rows = [
        ("Savings Per Van (Annual)", f"${savings_per_van:,.0f}"),
        ("Total Fleet Savings", f"${roi['total_annual_savings_usd']:,.0f}/yr"),
        ("Payback Period", f"{roi['payback_months']:.1f} months"),
        ("5-Year Net Benefit", f"${roi['five_year_net_usd']:,.0f}"),
    ]
    for k, v in rows:
        pdf.cell(90, 8, k)
        pdf.cell(0, 8, v, ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Recommended Action", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        f"Switch all {fleet_size:,} vans to {best_route['name']} ({best_route['avg_temp_f']:.0f}F avg) "
        f"from current {worst_route['name']} ({worst_route['avg_temp_f']:.0f}F avg). "
        f"Estimated annual battery savings: ${roi['total_annual_savings_usd']:,.0f}."
    )

    pdf_bytes = pdf.output()
    st.download_button(
        label="⬇️ Download PDF Report",
        data=bytes(pdf_bytes),
        file_name=f"ThermoRoute_Report_{selected_city.replace(', ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

else:
    st.markdown("""
<div style="text-align:center;padding:60px;background:rgba(23,105,176,0.05);
     border:1px dashed #1e3a5f;border-radius:12px;">
  <div style="font-size:3rem;">📄</div>
  <div style="color:#a9b6c6;margin-top:12px;">
    Select a city and vehicle type above, then click <strong>Generate Executive Report</strong>.
    <br>The report uses FortyGuard's <code>/v1/heat_intelligence</code> endpoint to create
    a multi-dimensional thermal risk assessment, downloadable as PDF.
  </div>
</div>
    """, unsafe_allow_html=True)

st.caption("⚡ ThermoRoute AI · FortyGuard Hackathon '26 · Track 03 Industrial & Enterprise")
