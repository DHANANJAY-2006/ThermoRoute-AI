# ThermoRoute AI: System Architecture Specification

## 1. Overview

ThermoRoute AI is a modular Python-based enterprise platform designed to process street-level temperature telemetry from the FortyGuard Temperature API® and calculate optimal delivery corridors for commercial electric vehicle fleets.

---

## 2. Directory & Module Structure

```
ThermoRoute-AI/
├── app/
│   ├── main.py                     # Landing page and key metrics
│   └── pages/
│       ├── 1_Fleet_Dashboard.py    # Multi-city regional thermal risk tracking
│       ├── 2_Route_Planner.py      # Spatial routing with OSRM turn-by-turn road geometry
│       ├── 3_Battery_Savings.py    # 3-component financial simulation & ROI modeling
│       ├── 4_Forecast_Planner.py   # 12-hour forward dispatch window optimization
│       └── 5_Executive_Report.py   # Automated brief generation & PDF export
├── core/
│   ├── fortyguard_client.py        # Asynchronous FortyGuard API client (all 6 endpoints)
│   ├── battery_model.py            # Arrhenius degradation kinetics engine
│   ├── ev_energy_model.py          # Temperature-dependent energy & range loss engine
│   ├── route_engine.py             # Spatial corridor scoring & OSRM integration
│   ├── cost_calculator.py          # Financial ROI, payback, and multi-year fleet scaling
│   └── alert_manager.py            # Real-time threshold evaluation for operations
├── data/
│   ├── demo_routes.json            # Logistics hub waypoint networks (Phoenix, Vegas, Dallas, Houston)
│   ├── ev_specs.json               # OEM battery specs (Rivian, Mercedes, Ford, BrightDrop)
│   └── electricity_prices.json     # Commercial electricity utility rates (US EIA)
├── docs/
│   ├── whitepaper.md               # Technical whitepaper & methodology
│   ├── architecture.md             # System architecture & module specification
│   ├── api_integration.md          # FortyGuard API endpoint documentation
│   ├── submission_brief.md         # Submission form answers & metadata
│   └── ThermoRoute_AI_Technical_Whitepaper.pdf # Formal PDF report
└── requirements.txt
```

---

## 3. Data Pipeline & Execution Flow

```
1. Input Selection
   ├── City: Phoenix, Las Vegas, Dallas, Houston
   ├── Chassis: Rivian EDV 500, Mercedes eSprinter, Ford E-Transit, BrightDrop EV600
   └── Fleet Size: e.g. 500 units

2. Telemetry Ingestion (FortyGuardClient)
   ├── POST /v1/heatmap (2m AGL roadway temperatures)
   ├── POST /v1/satellite (vegetation canopy coverage %)
   ├── POST /v1/env_params (solar irradiance W/m², persistence hours)
   └── POST /v1/streetview (pavement thermography)

3. Spatial Road Geometry (RouteEngine + OSRM)
   ├── Input: Ordered waypoint coordinates [lat, lon]
   ├── Query: OSRM driving routing service
   └── Output: 600–1,200 turn-by-turn coordinate pairs for realistic road rendering

4. Multi-Component Cost Calculation
   ├── BatteryDegradationModel: Arrhenius SEI rate constant -> annual pack depreciation ($)
   ├── EVEnergyModel: Efficiency loss % + AC HVAC load -> annual energy penalty ($)
   └── RangeOverheadModel: Effective range reduction -> operational overhead ($)

5. Output Rendering
   ├── Folium Dark GIS map with color-coded thermal exposure curves
   ├── Plotly point-by-point roadway telemetry charts
   ├── 3-Component stacked bar charts and 5-year cumulative ROI projections
   └── Automated FPDF executive operations brief with PDF download
```

---

## 4. Design Principles

- **Zero Client Latency:** Asynchronous non-blocking API polling with local fallback guarantees responsive user interaction.
- **Defensible Chemistry:** All degradation calculations rely on peer-reviewed Arrhenius kinetics ($E_a = 52.5\text{ kJ/mol}$) and empirical NREL/DOE EV operational datasets.
- **Clean Separation of Concerns:** Core computational modules (`core/`) have zero Streamlit dependencies, enabling CLI, API, or automated cron execution.
