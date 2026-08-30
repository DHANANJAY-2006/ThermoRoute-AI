# ThermoRoute AI

> **Hyperlocal Thermal Routing & Multi-Component EV Fleet Intelligence Engine**  
> Powered by **FortyGuard Temperature API®** · FortyGuard Global AI Hackathon '26 · Track 03: Industrial & Enterprise

[![FortyGuard Temperature API](https://img.shields.io/badge/Powered%20by-FortyGuard%20Temperature%20API-1769b0?style=flat-square)](https://www.fortyguard.com)
[![Challenge Track](https://img.shields.io/badge/Track-03%20Industrial%20%26%20Enterprise-1f7ae0?style=flat-square)](https://www.fortyguard.com/hackathon26)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=flat-square&logo=python)](https://python.org)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.38-ff4b4b?style=flat-square&logo=streamlit)](https://streamlit.io)

---

## Executive Overview

Commercial EV delivery fleets (Amazon Logistics, DHL Express, FedEx Express, UPS) deploy hundreds of thousands of electric delivery vans using legacy route optimization platforms that factor in only **distance** and **transit duration**.

In primary US logistics hubs such as Phoenix, AZ, surface-level roadway temperatures frequently reach **111.4°F (44.1°C)**. Under high solar load, the electrochemical degradation rate of commercial lithium-ion battery packs accelerates by **4.20x** relative to nominal baseline operating conditions (Arrhenius kinetics with $E_a = 52.5\text{ kJ/mol}$). Furthermore, extreme roadway heat increases auxiliary HVAC cabin/battery cooling draw ($+8.5\text{ kWh/day}$) and reduces single-charge operating range ($0.35\%/\text{°F}$).

Operating an electric delivery van through unmanaged high-stress urban heat corridors imposes over **$15,598 per vehicle per year** in combined battery depreciation, auxiliary energy surcharges, and range overhead. ThermoRoute AI correlates street-level microclimate telemetry with turn-by-turn road geometry to redirect fleets to thermally optimal corridors, reducing annual operational exposure to **$8,260 per year**.

* **Net Unit Operational Savings:** **$7,338 per vehicle per year** across battery preservation, energy efficiency, and range overhead.
* **Fleet Scale (500 Active Units):** **$3.67M in annual operating value**, delivering a **5-year net benefit of $17.47M** with a capital payback horizon under **2 months**.

---

## Core System Architecture

ThermoRoute AI correlates 2-meter street-level temperature telemetry from the **FortyGuard Temperature API®** with vehicle-specific chassis specifications and turn-by-turn road networks:

1. **Fleet Dashboard** (`app/pages/1_Fleet_Dashboard.py`) — Multi-city regional thermal risk tracking across primary US logistics hubs (Phoenix, Las Vegas, Dallas, Houston).
2. **Route Planner** (`app/pages/2_Route_Planner.py`) — Spatial microclimate corridor evaluation with real turn-by-turn road geometry and 3-component operational cost breakdown.
3. **Battery Savings** (`app/pages/3_Battery_Savings.py`) — Quantitative financial modeling of CapEx preservation, stacked cost distribution, and multi-year cumulative fleet return.
4. **Forecast Planner** (`app/pages/4_Forecast_Planner.py`) — Time-series dispatch scheduling utilizing FortyGuard's 12-hour forward forecast to shift heavy payload cycles into low-thermal-stress windows.
5. **Executive Report** (`app/pages/5_Executive_Report.py`) — Automated operational briefing generator utilizing the FortyGuard `/v1/heat_intelligence` multi-dimensional synthesis endpoint with exportable PDF briefs.

---

## Comprehensive 3-Component EV Cost Engine

$$\text{Total Annual Operational Cost} = C_{\text{degrade}} + C_{\text{energy}} + C_{\text{range}}$$

| Component | Physical Mechanism | Formula / Standard | Phoenix Baseline Exposure (Route A) |
| :--- | :--- | :--- | :--- |
| **1. Battery Degradation** | High temperature SEI layer growth & active lithium loss | Arrhenius kinetics ($E_a = 52.5\text{ kJ/mol}$) | **$14,689 / \text{van} / \text{yr}** |
| **2. Energy & AC Surcharge** | Battery internal resistance + HVAC auxiliary cooling load | $0.25\%/\text{°F} + \text{up to } 8.5\text{ kWh/day}$ AC draw | **$547 / \text{van} / \text{yr}** |
| **3. Range Overhead** | Effective range reduction causing mid-route depot returns | $0.35\%/\text{°F}$ (NREL/DOE validated) | **$361 / \text{van} / \text{yr}** |
| **Total Unmanaged Cost** | Combined high-stress corridor exposure | All 3 components | **$15,598 / \text{van} / \text{yr}** |
| **Total Managed Cost** | Thermally optimized highway corridor (Route C) | Operating at 95.9°F | **$8,260 / \text{van} / \text{yr}** |
| **Net Preservation Value** | Direct annual savings per vehicle | $C_{\text{unmanaged}} - C_{\text{managed}}$ | **+$7,338 / \text{van} / \text{yr}** |

---

## FortyGuard API Implementation

ThermoRoute AI integrates all **six production endpoints** of the FortyGuard Temperature API®:

| Endpoint | Function | Analysis Layer |
| :--- | :--- | :--- |
| `POST /v1/heatmap` | Waypoint-level thermal corridor telemetry | `exceedance` & `snapshot` |
| `POST /v1/satellite` | Canopy cover & pavement thermal shielding | Default multispectral |
| `POST /v1/streetview` | Ground-level roadway thermal segmentation | `snapshot` @ 2m elevation |
| `POST /v1/heat_intelligence` | Multi-dimensional risk synthesis and executive briefs | Multi-dimensional synthesis |
| `POST /v1/env_params` | Solar irradiance, heat index, and thermal persistence | `persistence` |
| `GET /v1/status/{id}` | Asynchronous task polling lifecycle | Non-blocking async status |

Detailed API schemas, parameters, and analysis layer justifications are available in [`api_usage.md`](api_usage.md) and [`docs/04_fortyguard_api_integration.md`](docs/04_fortyguard_api_integration.md).

---

## Installation & Local Execution

```bash
# Clone the repository
git clone https://github.com/DHANANJAY-2006/ThermoRoute-AI.git
cd ThermoRoute-AI

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Set DEMO_MODE=false and provide your FORTYGUARD_API_KEY for live calls

# Launch the Streamlit application
streamlit run app/main.py
```

---

## Repository Structure

```
ThermoRoute-AI/
├── app/
│   ├── main.py                     # Enterprise landing & headline telemetry
│   └── pages/
│       ├── 1_Fleet_Dashboard.py    # Regional thermal risk monitor
│       ├── 2_Route_Planner.py      # Spatial thermal route engine & OSRM road curves
│       ├── 3_Battery_Savings.py    # 3-Component financial modeling & CapEx ROI
│       ├── 4_Forecast_Planner.py   # 12-hour predictive dispatch planner
│       └── 5_Executive_Report.py   # Executive risk brief & PDF generator
├── core/
│   ├── fortyguard_client.py        # Full 6-endpoint async client
│   ├── battery_model.py            # Arrhenius cell degradation kinetics
│   ├── ev_energy_model.py          # Temperature-dependent energy & range engine
│   ├── route_engine.py             # Spatial corridor scoring & OSRM integration
│   ├── cost_calculator.py          # Multi-year fleet scaling & ROI logic
│   └── alert_manager.py            # Real-time thermal threshold evaluation
├── data/
│   ├── demo_routes.json            # US logistics hub waypoint networks
│   ├── ev_specs.json               # Commercial EV chassis specifications
│   └── electricity_prices.json     # US EIA commercial rate benchmarks
├── docs/
│   ├── whitepaper.md               # Technical whitepaper & physical modeling
│   ├── architecture.md             # System architecture & module specification
│   ├── api_integration.md          # FortyGuard API endpoint documentation
│   ├── submission_brief.md         # Hackathon submission metadata & form fields
│   └── ThermoRoute_AI_Technical_Whitepaper.pdf # Formal PDF report
├── notebooks/
│   └── api_demo.ipynb              # Jupyter API verification notebook
├── api_usage.md                    # Formal FortyGuard API documentation
└── requirements.txt
```

---

## Compliance & Operational Standards

- **Geographic Scope:** United States logistics hubs exclusively (Phoenix AZ, Las Vegas NV, Dallas TX, Houston TX).
- **Forecast Horizon:** Strictly limited to $\le 12$ hours forward in compliance with FortyGuard API specifications.
- **Asynchronous Protocol:** Polling pattern implementation with zero credit consumption on failed tasks.
- **Data Provenance:** FortyGuard Temperature API® (trial license), US Energy Information Administration (public domain), OpenStreetMap / OSRM (ODbL).
