# ThermoRoute AI

> **Hyperlocal Thermal Routing, Live Telematics & Battery Preservation Engine for Commercial EV Fleets**  
> Powered by **FortyGuard Temperature API®** · FortyGuard Global AI Hackathon '26 · Track 03: Industrial & Enterprise

[![FortyGuard Temperature API](https://img.shields.io/badge/Powered%20by-FortyGuard%20Temperature%20API-1769b0?style=flat-square)](https://www.fortyguard.com)
[![Challenge Track](https://img.shields.io/badge/Track-03%20Industrial%20%26%20Enterprise-1f7ae0?style=flat-square)](https://www.fortyguard.com/hackathon26)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=flat-square&logo=python)](https://python.org)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.38-ff4b4b?style=flat-square&logo=streamlit)](https://streamlit.io)

---

## Executive Overview

Commercial EV delivery fleets (Amazon Logistics, DHL Express, FedEx, UPS) route hundreds of thousands of medium- and heavy-duty electric vans using conventional routing engines optimized strictly for **distance** and **transit time**.

These legacy systems create a massive operational blind spot: in primary US logistics hubs such as Phoenix, AZ, surface-level roadway temperatures exceed **111.4°F (44.1°C)**. Under high solar load, the electrochemical degradation rate of commercial lithium-ion battery packs accelerates by **4.20x** relative to nominal baseline operating conditions (Arrhenius kinetics with $E_a = 52.5\text{ kJ/mol}$).

Operating an electric delivery van through unmanaged high-stress urban heat corridors imposes up to **$14,689 per vehicle per year** in premature battery depreciation. ThermoRoute AI autonomously identifies and redirects fleets to thermally optimal corridors, reducing annual degradation to **$7,836 per year**.

* **Net Verified Unit Savings:** **$6,853 per vehicle per year** in avoided battery depreciation.
* **Fleet Scale (500 Active Units):** **$3.43M in annual CapEx savings**, delivering a **5-year net benefit of $16.26M**.
* **Environmental Impact:** Avoids **~4,200 metric tons of Scope 3 embedded battery manufacturing $CO_2e$** over 5 years.

---

## Comprehensive Platform Modules

ThermoRoute AI is an enterprise fleet intelligence suite consisting of 9 modules:

1. **Regional Fleet Risk Monitor** — Multi-hub thermal exposure tracking across primary US logistics corridors (Phoenix, Las Vegas, Dallas, Houston).
2. **Thermal Route Engine** — Corridor microclimate scoring combining 2-meter ambient temperature, canopy shade relief, and solar irradiance.
3. **Live Telematics & In-Flight Rerouting** — Real-time telemetry command center simulating active commercial EV delivery vans with automated in-flight heat pocket diversion triggers.
4. **Physics-Informed ML Battery Health (SoH & RUL)** — 120,000-mile capacity retention simulator modeling life extension from 2.2 years (unmanaged) to 4.6 years (managed).
5. **Smart Depot Charging Optimizer** — Nighttime charging and pre-conditioning scheduler aligning FortyGuard 12-hour forecasts with utility Time-of-Use (TOU) tariffs.
6. **Financial & CapEx ROI Modeler** — Dynamic simulation of CapEx preservation, payback periods, and multi-year cumulative fleet return.
7. **12-Hour Predictive Dispatch Planner** — Forward-looking dispatch scheduler enforcing FortyGuard's 12-hour forecast limits to shift heavy transit into cool morning windows.
8. **Scope 3 ESG & Carbon Avoidance Ledger** — Life-Cycle Assessment (LCA) quantifying embedded manufacturing greenhouse gas emissions avoided.
9. **Executive Risk Brief & Audit Report** — Automated operational briefing generator utilizing FortyGuard's `/v1/heat_intelligence` endpoint with exportable PDF briefs.

---

## Scientific & Electrochemical Methodology

Cell degradation rates are computed using the **Arrhenius electrochemical kinetics model**, the global standard employed by automotive OEMs to rate battery longevity:

$$\frac{k(T)}{k(T_0)} = \exp\left( \frac{E_a}{R} \left( \frac{1}{T_0} - \frac{1}{T_{\text{effective}}} \right) \right)$$

Where:
- $E_a = 52.5\text{ kJ/mol}$ (Activation energy for commercial Li-ion SEI degradation)
- $R = 8.314\text{ J/(mol}\cdot\text{K)}$ (Universal gas constant)
- $T_0 = 298.15\text{ K}$ ($25.0^\circ\text{C} / 77.0^\circ\text{F}$ baseline)
- $T_{\text{effective}} = T_{\text{ambient}} + \Delta T_{\text{solar}} - \Delta T_{\text{shade}}$

| Roadway Microclimate | Degradation Multiplier | Nominal Battery Life (Rivian EDV) |
| :--- | :--- | :--- |
| **77.0°F (25°C)** | **1.00x** (Nominal Baseline) | **8.0 Years** |
| **95.0°F (35°C)** | **1.99x** | **4.0 Years** |
| **105.0°F (40.5°C)** | **2.86x** | **2.8 Years** |
| **111.4°F + Solar (Phoenix Urban Core)** | **4.20x** | **1.9 Years** |

FortyGuard provides street-level measurements at **2 meters elevation**, matching the chassis mount height of commercial EV battery packs.

---

## FortyGuard API Implementation

ThermoRoute AI integrates all **six production endpoints** of the FortyGuard Temperature API®:

| Endpoint | Function | Analysis Layer |
| :--- | :--- | :--- |
| `POST /v1/heatmap` | Waypoint-level thermal corridor telemetry | `exceedance` & `snapshot` |
| `POST /v1/satellite` | Canopy cover & pavement thermal shielding | Default |
| `POST /v1/streetview` | Ground-level roadway thermal segmentation | `snapshot` |
| `POST /v1/heat_intelligence` | Multi-dimensional risk synthesis and executive briefs | Multi-dimensional |
| `POST /v1/env_params` | Solar irradiance, heat index, and thermal persistence | `persistence` |
| `GET /v1/status/{id}` | Asynchronous task polling lifecycle | — |

Comprehensive API documentation, request/response schemas, and analysis layer justifications are detailed in [`api_usage.md`](api_usage.md).

---

## Installation & Deployment

```bash
# Clone the repository
git clone https://github.com/DHANANJAY-2006/ThermoRoute-AI.git
cd ThermoRoute-AI

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Set DEMO_MODE=false and provide your FortyGuard API key for live calls

# Launch the Streamlit application
streamlit run app/main.py
```

---

## Repository Structure

```
ThermoRoute-AI/
├── app/
│   ├── main.py                    # Enterprise landing & system telemetry
│   └── pages/
│       ├── 1_fleet_dashboard.py   # Regional thermal risk monitor
│       ├── 2_route_planner.py     # Spatial thermal route engine
│       ├── 3_live_telematics.py   # Live fleet telematics & in-flight rerouting
│       ├── 4_battery_health_ml.py # Physics-informed ML SoH & RUL predictor
│       ├── 5_depot_charging.py    # Smart depot charging & pre-conditioning
│       ├── 6_financial_roi.py     # CapEx preservation & ROI analysis
│       ├── 7_forecast_planner.py  # 12-hour predictive dispatch planner
│       ├── 8_carbon_esg.py        # Scope 3 ESG & carbon avoidance ledger
│       └── 9_executive_report.py  # Executive risk brief & PDF generator
├── core/
│   ├── fortyguard_client.py       # Full 6-endpoint async client
│   ├── battery_model.py           # Arrhenius cell degradation calculations
│   ├── route_engine.py            # Spatial corridor scoring pipeline
│   ├── telematics_simulator.py    # Real-time active fleet simulation
│   ├── ml_battery_health.py       # ML battery health & RUL prediction
│   ├── depot_optimizer.py         # Smart depot charging schedule optimizer
│   ├── cost_calculator.py         # Financial ROI & fleet scaling logic
│   ├── carbon_calculator.py       # Scope 3 LCA carbon avoidance engine
│   └── alert_manager.py           # Automated dispatch decision engine
├── data/
│   ├── demo_routes.json           # US logistics hub waypoint networks
│   ├── ev_specs.json              # Commercial EV chassis specifications
│   └── electricity_prices.json    # US EIA state utility benchmarks
├── docs/
│   └── impact_statement.md        # Comprehensive project & impact statement
├── notebooks/
│   └── api_demo.ipynb             # Interactive Jupyter API verification
├── api_usage.md                   # Formal FortyGuard API documentation
└── requirements.txt
```

---

## Compliance & Licensing

- **Geographic Scope:** United States logistics hubs exclusively (Phoenix AZ, Las Vegas NV, Dallas TX, Houston TX).
- **Forecast Window:** Strictly limited to $\le 12$ hours forward in compliance with FortyGuard API specifications.
- **Asynchronous Architecture:** Full polling implementation with zero credit consumption on failed tasks.
- **Data Provenance:** FortyGuard Temperature API® (trial license), US Energy Information Administration (public domain), OpenStreetMap (ODbL).
