"""
ThermoRoute AI — Enterprise Thermal Fleet Intelligence
Powered by FortyGuard Temperature API®
FortyGuard Global AI Hackathon '26 · Track 03: Industrial & Enterprise
"""

import streamlit as st

st.set_page_config(
    page_title="ThermoRoute AI — Thermal Routing System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── High-End Industrial Styling ───────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

  html, body, [class*="css"] {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }

  /* Clean up Streamlit header */
  header[data-testid="stHeader"] {
      background: rgba(4, 9, 28, 0.8) !important;
      backdrop-filter: blur(8px);
  }
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }

  /* Capitalize First Letter of Sidebar Page Names */
  [data-testid="stSidebarNav"] span {
      text-transform: capitalize !important;
      font-weight: 500 !important;
      font-size: 0.92rem !important;
  }

  /* Deep obsidian/navy background */
  [data-testid="stAppViewContainer"] {
      background: radial-gradient(circle at 50% 0%, #0c1729 0%, #050a14 70%, #03060c 100%);
      color: #e2e8f0;
  }
  
  [data-testid="stSidebar"] {
      background-color: #060b14;
      border-right: 1px solid #172439;
  }

  /* Unified Metrics Grid */
  .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin: 12px 0 24px 0;
  }
  .metric-card {
      background: rgba(15, 23, 42, 0.65);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 108px;
      box-sizing: border-box;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }
  .metric-card-highlight {
      background: rgba(14, 165, 233, 0.08);
      border: 1px solid rgba(56, 189, 248, 0.4);
      box-shadow: 0 0 16px rgba(14, 165, 233, 0.08);
  }
  .metric-label {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #94a3b8;
      font-weight: 600;
      margin-bottom: 4px;
  }
  .metric-value {
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.75rem;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.1;
      margin-bottom: 4px;
  }
  .metric-value-highlight {
      color: #38bdf8;
  }
  .metric-delta {
      font-size: 0.78rem;
      font-weight: 500;
  }
  .delta-normal { color: #4ade80; }
  .delta-inverse { color: #f87171; }
  .delta-highlight { color: #38bdf8; font-weight: 600; }

  /* API Endpoint Grid */
  .api-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin: 14px 0 24px 0;
  }
  .api-card {
      background: rgba(15, 23, 42, 0.65);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
  .api-card-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
  }
  .http-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.65rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
  }
  .http-post {
      background: rgba(14, 165, 233, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(14, 165, 233, 0.3);
  }
  .http-get {
      background: rgba(34, 197, 94, 0.15);
      color: #4ade80;
      border: 1px solid rgba(34, 197, 94, 0.3);
  }
  .api-path {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      font-weight: 600;
      color: #f1f5f9;
      white-space: nowrap;
  }
  .api-desc {
      font-size: 0.82rem;
      color: #94a3b8;
      line-height: 1.5;
      margin-bottom: 10px;
      flex-grow: 1;
  }
  .api-layer {
      font-size: 0.72rem;
      color: #64748b;
      border-top: 1px solid #1e293b;
      padding-top: 8px;
  }
  .api-layer code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      color: #38bdf8;
      background: rgba(15, 23, 42, 0.8);
      padding: 1px 4px;
      border-radius: 3px;
  }

  /* Headers */
  h1 {
      font-weight: 800 !important;
      letter-spacing: -0.03em !important;
      color: #ffffff !important;
  }
  h2, h3, h4 {
      font-weight: 700 !important;
      letter-spacing: -0.02em !important;
      color: #f1f5f9 !important;
  }
  p, li {
      color: #94a3b8 !important;
      font-size: 0.95rem;
      line-height: 1.6;
  }

  /* Enterprise badge */
  .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 8px;
      border-radius: 4px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      background: rgba(14, 165, 233, 0.1);
      border: 1px solid rgba(14, 165, 233, 0.25);
      color: #38bdf8;
  }
  .system-pill {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.68rem;
      padding: 2px 8px;
      border-radius: 3px;
      background: #0f172a;
      border: 1px solid #334155;
      color: #cbd5e1;
  }

  /* Glass panels */
  .panel-card {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 20px;
  }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 12px 0 14px 0;">
  <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <span class="status-badge">TRACK 03: INDUSTRIAL & ENTERPRISE</span>
    <span class="system-pill">HYPERLOCAL THERMAL INTELLIGENCE</span>
  </div>
  <h1 style="font-size: 2.6rem; margin: 0 0 8px 0;">
    ThermoRoute AI
  </h1>
  <p style="font-size: 1.1rem; color: #94a3b8; max-width: 820px; margin: 0;">
    Autonomous thermal degradation management for commercial EV fleets.
    Translating 2-meter street-level temperature telemetry into battery lifespan extension and verified capital expenditure savings.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Unified Real-Time Metrics Strip ───────────────────────────────────────────
st.markdown("""
<div class="metrics-grid">
  <div class="metric-card">
    <div class="metric-label">Primary Test Corridor</div>
    <div class="metric-value">111.4°F</div>
    <div class="metric-delta delta-inverse">Urban Core Peak Exposure</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Peak Degradation Rate</div>
    <div class="metric-value">4.20x</div>
    <div class="metric-delta delta-inverse">NMC/LFP SEI Growth</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Unit CapEx Savings</div>
    <div class="metric-value">$6,853</div>
    <div class="metric-delta delta-normal">Highway vs Surface Grid</div>
  </div>
  <div class="metric-card metric-card-highlight">
    <div class="metric-label">5-Year Fleet Value (500 Vans)</div>
    <div class="metric-value metric-value-highlight">$16.26M</div>
    <div class="metric-delta delta-highlight">Net Financial Benefit</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Core Pillars ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
    <div class="panel-card">
      <h3 style="margin-top:0; font-size:1.25rem; color:#f8fafc;">The Fleet Telemetry Blind Spot</h3>
      <p>
        Commercial fleet routing platforms optimize strictly for two dimensions: <strong>distance</strong> and <strong>transit duration</strong>. 
        Neither parameter reflects the thermodynamic cost of high-stress urban heat corridors on heavy commercial lithium-ion packs.
      </p>
      <p>
        At 111.4°F ambient surface temperatures in major logistics hubs such as Phoenix, accelerated chemical degradation (Arrhenius kinetics) increases battery capacity loss by <strong>4.20x</strong> compared to baseline operating conditions.
      </p>
      <p style="margin-bottom:0;">
        Operating an electric delivery vehicle through unshaded downtown corridors imposes up to <strong>$14,689 per vehicle per year</strong> in premature battery depreciation.
      </p>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="panel-card">
      <h3 style="margin-top:0; font-size:1.25rem; color:#f8fafc;">Hyperlocal Thermal Resolution</h3>
      <p>
        ThermoRoute AI integrates FortyGuard's street-level Temperature API—measured at <strong>2 meters above ground level</strong>, exactly matching the elevation of commercial EV battery chassis enclosures.
      </p>
      <p>
        By correlating roadway microclimate temperatures with the Arrhenius electrochemical degradation model, ThermoRoute AI autonomously evaluates candidate transit corridors and redirects fleets to thermally optimal routes.
      </p>
      <p style="margin-bottom:0;">
        <strong>Result:</strong> An average of <strong>$6,853 per vehicle per year</strong> in preserved asset life with zero loss in package delivery volume.
      </p>
    </div>
    """, unsafe_allow_html=True)

# ── Scientific Foundation ─────────────────────────────────────────────────────
st.markdown("### Electrochemical Degradation Model")
st.markdown("Lithium-ion cell aging follows the **Arrhenius degradation relationship**, where elevated operating temperature accelerates solid electrolyte interphase (SEI) layer growth (Activation Energy: 52.5 kJ/mol):")
st.latex(r"\frac{k(T)}{k(T_0)} = \exp\left( \frac{E_a}{R} \left( \frac{1}{T_0} - \frac{1}{T_{\text{effective}}} \right) \right)")

st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric(label="Nominal Baseline (77°F)", value="1.00x", delta="Rated Life: 8.0 Years")
with s2:
    st.metric(label="Elevated Threshold (95°F)", value="1.99x", delta="Rated Life: 4.0 Years", delta_color="inverse")
with s3:
    st.metric(label="High Heat (105°F)", value="2.86x", delta="Rated Life: 2.8 Years", delta_color="inverse")
with s4:
    st.metric(label="Critical Ambient (111.4°F + Solar)", value="4.20x", delta="Rated Life: 1.9 Years", delta_color="inverse")

st.markdown("---")

# ── FortyGuard API Architecture ───────────────────────────────────────────────
st.markdown("### FortyGuard API Architecture & Endpoint Implementation")
st.caption("Full production integration across all 6 FortyGuard Temperature API® endpoints:")

st.markdown("""
<div class="api-grid">
  <div class="api-card">
    <div class="api-card-header">
      <span class="http-badge http-post">POST</span>
      <span class="api-path">/v1/heatmap</span>
    </div>
    <div class="api-desc">Waypoint-level thermal corridor telemetry and 2-meter air temperature mapping.</div>
    <div class="api-layer">Layers: <code>exceedance</code> · <code>snapshot</code></div>
  </div>

  <div class="api-card">
    <div class="api-card-header">
      <span class="http-badge http-post">POST</span>
      <span class="api-path">/v1/satellite</span>
    </div>
    <div class="api-desc">Canopy vegetation coverage, NDVI metrics, and solar radiation shielding factors.</div>
    <div class="api-layer">Source: High-resolution multispectral imagery</div>
  </div>

  <div class="api-card">
    <div class="api-card-header">
      <span class="http-badge http-post">POST</span>
      <span class="api-path">/v1/streetview</span>
    </div>
    <div class="api-desc">Street-level pavement thermography and microclimate ground segment analysis.</div>
    <div class="api-layer">Layer: <code>snapshot</code> @ 2m elevation</div>
  </div>

  <div class="api-card">
    <div class="api-card-header">
      <span class="http-badge http-post">POST</span>
      <span class="api-path">/v1/heat_intelligence</span>
    </div>
    <div class="api-desc">Multi-dimensional operational risk synthesis and autonomous fleet advisory generation.</div>
    <div class="api-layer">Outputs: Executive risk brief & audit reports</div>
  </div>

  <div class="api-card">
    <div class="api-card-header">
      <span class="http-badge http-post">POST</span>
      <span class="api-path">/v1/env_params</span>
    </div>
    <div class="api-desc">Direct solar irradiance (W/m²), heat index (°F), AQI, and continuous thermal persistence.</div>
    <div class="api-layer">Layer: <code>persistence</code> (hours duration)</div>
  </div>

  <div class="api-card">
    <div class="api-card-header">
      <span class="http-badge http-get">GET</span>
      <span class="api-path">/v1/status/{task_id}</span>
    </div>
    <div class="api-desc">Unified asynchronous task polling and lifecycle status verification engine.</div>
    <div class="api-layer">Protocol: Non-blocking async task polling</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 1px solid #1e293b;">
  <p style="font-size: 0.8rem; color: #64748b;">
    ThermoRoute AI · Developed for FortyGuard Global AI Hackathon '26 · Track 03: Industrial & Enterprise<br>
    Powered by FortyGuard Temperature API® — Enterprise Urban Thermal Intelligence
  </p>
</div>
""", unsafe_allow_html=True)
