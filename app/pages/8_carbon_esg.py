"""
Page 8 — Scope 3 ESG & Carbon Avoidance Ledger
Quantifies life-cycle embedded CO2 emissions avoided by extending battery pack life.
Generates corporate sustainability reporting metrics (Scope 3 GHG protocol).
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.carbon_calculator import calculate_fleet_esg_impact

st.set_page_config(
    page_title="Scope 3 ESG & Carbon Ledger — ThermoRoute AI",
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
      padding: 20px;
      margin-bottom: 16px;
  }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.caption("FortyGuard Global AI Hackathon '26")
    st.caption("Track 03: Industrial & Enterprise")

with open(os.path.join(os.path.dirname(__file__), "../../data/ev_specs.json"), encoding="utf-8") as f:
    ev_specs = json.load(f)

st.markdown("## Scope 3 ESG & Battery Carbon Avoidance Ledger")
st.caption("Life-Cycle Assessment (LCA) quantifying embedded manufacturing greenhouse gas emissions avoided.")
st.markdown("---")

# Controls
c1, c2, c3 = st.columns(3)
with c1:
    vehicle_key = st.selectbox(
        "Commercial EV Platform",
        list(ev_specs.keys()),
        format_func=lambda k: f"{ev_specs[k]['name']} ({ev_specs[k]['battery_capacity_kwh']} kWh Pack)"
    )
with c2:
    fleet_size = st.number_input("Operating Fleet Scale (Units)", 1, 250000, 500, step=25)
with c3:
    lifespan_ext = st.slider("Preserved Battery Life (Years)", 0.5, 4.0, 1.9, step=0.1)

# Calculations
esg = calculate_fleet_esg_impact(
    fleet_size=fleet_size,
    battery_kwh=ev_specs[vehicle_key]["battery_capacity_kwh"],
    lifespan_extension_years=lifespan_ext,
    nominal_lifespan_years=ev_specs[vehicle_key]["nominal_cycle_life_years"]
)

# Top Metrics Strip
e1, e2, e3, e4 = st.columns(4)
with e1:
    st.metric(
        label="Embedded Pack Carbon",
        value=f"{esg['pack_embedded_co2_mt']} MT CO₂e",
        delta="Per Replacement Pack",
        delta_color="inverse"
    )
with e2:
    st.metric(
        label="Fleet Annual CO₂e Avoided",
        value=f"{esg['fleet_annual_co2_avoided_mt']:,.1f} MT",
        delta=f"{fleet_size} Units Active",
        delta_color="normal"
    )
with e3:
    st.metric(
        label="5-Year Cumulative Carbon Avoided",
        value=f"{esg['fleet_5yr_co2_avoided_mt']:,.1f} MT CO₂e",
        delta="Scope 3 LCA Reduction",
        delta_color="normal"
    )
with e4:
    st.metric(
        label="Carbon Offset Market Value",
        value=f"${esg['carbon_credit_value_usd_5yr']:,.0f}",
        delta="5-Year Credit Valuation",
        delta_color="normal"
    )

st.markdown("---")

# Visual equivalences
c_eq1, c_eq2 = st.columns(2)

with c_eq1:
    st.markdown("""
    <div class="panel-card">
      <h3 style="margin-top:0; color:#f8fafc;">Environmental Equivalence Metrics</h3>
      <p style="color:#94a3b8; font-size:0.9rem;">
        Preventing premature commercial lithium-ion pack disposal generates verified Scope 3 GHG avoidance equivalents:
      </p>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:16px;">
        <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:6px; border:1px solid #1e293b;">
          <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase;">Mature Trees Equivalent</div>
          <div style="font-family:'JetBrains Mono', monospace; font-size:1.4rem; font-weight:700; color:#22c55e;">
            {:,} Trees
          </div>
          <div style="font-size:0.75rem; color:#94a3b8;">Annual Carbon Sequestration</div>
        </div>
        <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:6px; border:1px solid #1e293b;">
          <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase;">Diesel Fuel Offset</div>
          <div style="font-family:'JetBrains Mono', monospace; font-size:1.4rem; font-weight:700; color:#38bdf8;">
            {:,} Gal
          </div>
          <div style="font-size:0.75rem; color:#94a3b8;">Gallons Diesel Equivalent</div>
        </div>
      </div>
    </div>
    """.format(esg['tree_equivalent_annual'], esg['diesel_gallons_equivalent_annual']), unsafe_allow_html=True)

with c_eq2:
    st.markdown("#### Cumulative 5-Year Scope 3 Emissions Avoidance")
    fig_esg = go.Figure()
    years = [f"Year {i}" for i in range(1, 6)]
    cum_mt = [esg["fleet_annual_co2_avoided_mt"] * i for i in range(1, 6)]
    
    fig_esg.add_trace(go.Bar(
        x=years,
        y=cum_mt,
        marker_color="#22c55e",
        text=[f"{m:,.1f} MT" for m in cum_mt],
        textposition="outside",
        name="Avoided CO2e (Metric Tons)"
    ))
    fig_esg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8"),
        yaxis=dict(title="Avoided GHG (MT CO₂e)", gridcolor="#1e293b"),
        height=280,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_esg, use_container_width=True)

# Major Carrier ESG Benchmark Table
st.markdown("---")
st.markdown("### Enterprise ESG Impact Across Major Fleet Operators")
st.caption("Projected Scope 3 carbon avoidance for committed commercial EV deployment pipelines:")

carriers = [
    {"Carrier": "Amazon Logistics (The Climate Pledge)", "Fleet": 100000, "Pack": 135.0, "LifespanExt": 1.9},
    {"Carrier": "DHL Express (GoGreen Plus)",           "Fleet": 35000,  "Pack": 113.0, "LifespanExt": 1.8},
    {"Carrier": "UPS Fleet",                            "Fleet": 10000,  "Pack": 113.0, "LifespanExt": 1.8},
    {"Carrier": "FedEx Express (Carbon Neutral 2040)",  "Fleet": 5000,   "Pack": 160.0, "LifespanExt": 2.0}
]

esg_rows = []
for c in carriers:
    res = calculate_fleet_esg_impact(c["Fleet"], c["Pack"], c["LifespanExt"])
    esg_rows.append({
        "Enterprise Fleet": c["Carrier"],
        "Active EV Pipeline": f"{c['Fleet']:,} Units",
        "Annual Scope 3 CO₂e Avoided": f"{res['fleet_annual_co2_avoided_mt']:,.0f} MT",
        "5-Year Cumulative Carbon Avoided": f"{res['fleet_5yr_co2_avoided_mt']:,.0f} MT",
        "Equivalent Trees Seeded": f"{res['tree_equivalent_annual'] * 5:,}",
        "Carbon Credit Valuation": f"${res['carbon_credit_value_usd_5yr']:,.0f}"
    })

st.dataframe(pd.DataFrame(esg_rows), use_container_width=True, hide_index=True)
