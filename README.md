# ThermoRoute AI

> **Hyperlocal Thermal Routing & Battery Preservation Engine for Commercial EV Fleets**  
> Powered by **FortyGuard Temperature API®** · FortyGuard Global AI Hackathon '26 · Track 03: Industrial & Enterprise

[![FortyGuard Temperature API](https://img.shields.io/badge/Powered%20by-FortyGuard%20Temperature%20API-1769b0?style=flat-square)](https://www.fortyguard.com)
[![Challenge Track](https://img.shields.io/badge/Track-03%20Industrial%20%26%20Enterprise-1f7ae0?style=flat-square)](https://www.fortyguard.com/hackathon26)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=flat-square&logo=python)](https://python.org)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.38-ff4b4b?style=flat-square&logo=streamlit)](https://streamlit.io)

---

## Executive Overview

Commercial EV delivery fleets (Amazon Logistics, DHL Express, FedEx, UPS) route hundreds of thousands of medium- and heavy-duty electric vans using conventional routing engines optimized strictly for **distance** and **transit time**.

These engines ignore roadway microclimates. In major logistics hubs such as Phoenix, AZ, surface-level ambient air temperatures reach **111.4°F (44.1°C)**. Under these conditions with direct solar radiation, the electrochemical degradation of commercial lithium-ion battery packs accelerates by **4.20x** relative to nominal baseline operating conditions (Arrhenius kinetics with $E_a = 52.5\text{ kJ/mol}$).

Operating a commercial EV delivery vehicle through unmanaged high-stress urban heat corridors imposes up to **$14,689 per vehicle per year** in premature battery capacity loss. Redirecting that same vehicle to a thermally optimal corridor through ThermoRoute AI reduces annual degradation cost to **$7,836 per year**.

**Net Verified Impact:** **$6,853 per vehicle per year** in avoided battery depreciation.  
**Fleet Scale (500 Active Units):** **$3.43M in annual CapEx savings**, delivering a **5-year net benefit of $16.26M**.

---

## Core System Architecture

ThermoRoute AI correlates 2-meter street-level temperature telemetry from the **FortyGuard Temperature API®** with vehicle-specific battery pack degradation parameters.

1. **Fleet Risk Monitor** — City-wide thermal exposure tracking across primary US logistics corridors (Phoenix, Las Vegas, Dallas, Houston).
2. **Thermal Route Engine** — Microclimate corridor evaluation combining roadway heatmaps, canopy shade metrics, and ground-level exposure into optimal transit recommendations.
3. **Financial & ROI Modeler** — Dynamic simulation of CapEx preservation, payback periods, and multi-year cumulative fleet return.
4. **12-Hour Shift Planner** — Time-series dispatch scheduling utilizing FortyGuard's 12-hour forward forecast to shift heavy transit cycles into low-thermal-stress windows.
5. **Executive Risk Brief** — Automated operational briefing generator utilizing the FortyGuard `/v1/heat_intelligence` multi-dimensional synthesis endpoint with exportable PDF briefs.

---

## Scientific Methodology

Cell degradation rates are computed using the **Arrhenius electrochemical kinetics model**, the global standard employed by automotive OEMs to rate battery longevity:

$$\frac{k(T)}{k(T_0)} = \exp\left( \frac{E_a}{R} \left( \frac{1}{T_0} - \frac{1}{T_{\text{effective}}} \right) \right)$$

Where:
- $E_a = 52.5\text{ kJ/mol}$ (Activation energy for commercial Li-ion SEI degradation)
- $R = 8.314\text{ J/(mol}\cdot\text{K)}$ (Universal gas constant)
- $T_0 = 298.15\text{ K}$ ($25^\circ\text{C} / 77.0^\circ\text{F}$ baseline)
- $T_{\text{effective}}$ accounts for ambient roadway temperature, direct solar radiation load (from `/v1/env_params`), and canopy shading offsets (from `/v1/satellite`).

| Roadway Conditions | Degradation Multiplier | Nominal Battery Life (Rivian EDV) |
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
│       ├── 1_fleet_dashboard.py   # Fleet-wide thermal exposure monitor
│       ├── 2_route_planner.py     # Interactive spatial route engine
│       ├── 3_battery_savings.py   # CapEx preservation & ROI analysis
│       ├── 4_forecast_planner.py  # 12-hour predictive dispatch planner
│       └── 5_executive_report.py  # Executive brief & PDF generator
├── core/
│   ├── fortyguard_client.py       # Full 6-endpoint async client
│   ├── battery_model.py           # Arrhenius cell degradation calculations
│   ├── route_engine.py            # Spatial corridor scoring pipeline
│   ├── cost_calculator.py         # Financial ROI & fleet scaling logic
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
