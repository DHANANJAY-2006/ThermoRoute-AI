# ThermoRoute AI — Technical Architecture & System Design

## 1. High-Level Architecture Overview

ThermoRoute AI is engineered as a multi-tier enterprise decision support platform. It bridges environmental temperature telemetry from FortyGuard's Large Temperature Models (LTMs) with commercial vehicle physics and financial optimization models.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       DATA ACQUISITION LAYER                            │
│  FortyGuard Temperature API® (2m Elevation Telemetry)                   │
│  - /v1/heatmap (Exceedance & Snapshot Layers)                           │
│  - /v1/satellite (Canopy Vegetation & Shielding)                        │
│  - /v1/env_params (Solar Irradiance, Heat Index, Persistence)           │
│  - /v1/streetview (Pavement Microclimate)                               │
│  - /v1/heat_intelligence (Multi-Dimensional Synthesis)                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SPATIAL & ROUTING CORRELATION                        │
│  - OpenStreetMap & OSRM Routing Engine (Turn-by-turn road geometry)     │
│  - Waypoint Microclimate Spatial Mapping                                │
│  - Elevation Matching (2.0m AGL vs Chassis Enclosure)                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   COMPUTATIONAL CORE ENGINE LAYER                       │
│  1. BatteryDegradationModel (Arrhenius Kinetics, Ea = 52.5 kJ/mol)      │
│  2. EVEnergyModel (Temperature-dependent kWh/mi & AC Draw)              │
│  3. RangeOverheadModel (Operational range degradation & stop modeling)  │
│  4. RouteEngine (Multi-corridor ranking & total exposure scoring)       │
│  5. CostCalculator (Fleet scaling, payback horizons, 5-yr net benefit) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ENTERPRISE PRESENTATION LAYER                      │
│  Streamlit Multi-Page Architecture (5 Specialized Workspaces)           │
│  1. Fleet Risk Monitor         2. Thermal Route Engine                  │
│  3. Financial Modeling & ROI   4. 12-Hour Forecast Dispatch             │
│  5. Executive Brief & PDF Generator                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Python Module Structure

| Module | File Path | Responsibilities |
| :--- | :--- | :--- |
| **`fortyguard_client.py`** | `core/fortyguard_client.py` | Asynchronous API client covering all 6 endpoints with submit-and-poll lifecycle, layer selection, and demo-mode resilience. |
| **`battery_model.py`** | `core/battery_model.py` | Electrochemical cell degradation modeling via Arrhenius kinetics, effective temperature synthesis, and route ranking. |
| **`ev_energy_model.py`** | `core/ev_energy_model.py` | Energy consumption penalties (kWh/mile) and range degradation cost calculation across ambient temperature bands. |
| **`route_engine.py`** | `core/route_engine.py` | Corridor scoring, OSRM turn-by-turn geometry synthesis, and cross-regional multi-city snapshot generation. |
| **`cost_calculator.py`** | `core/cost_calculator.py` | Enterprise fleet ROI synthesis, multi-year cumulative projections, and macro-industry validation calculations. |
| **`alert_manager.py`** | `core/alert_manager.py` | Real-time threshold evaluation for autonomous dispatch decision support. |

---

## 3. Data Flow & Execution Lifecycle

1. **User Selection:** Fleet operator selects an operating hub (e.g., Phoenix, AZ) and commercial vehicle chassis (e.g., Rivian EDV 500).
2. **Telemetry Ingestion:** `core/route_engine.py` queries `FortyGuardClient` for the hub's waypoint network, retrieving:
   - Street-level air temperatures at 2m AGL.
   - Canopy vegetation cover percentage (`/v1/satellite`).
   - Direct solar irradiance in $\text{W/m}^2$ (`/v1/env_params`).
   - Continuous heat persistence in hours (`/v1/env_params`).
3. **Turn-by-Turn Geometry:** The engine queries the routing service for candidate corridors, extracting coordinate pairs (600–1,200 points per corridor).
4. **Multi-Component Cost Calculation:**
   - Degradation annual cost ($C_{\text{degrade}}$) is computed using Arrhenius rate constants.
   - Energy penalty ($C_{\text{energy}}$) is computed based on temperature delta and HVAC cooling draw.
   - Range overhead ($C_{\text{range}}$) is computed from effective single-charge range reduction.
5. **Corridor Ranking:** Corridors are ranked by total annual operational exposure. The optimal corridor is designated with recommended status.
6. **Rendering:** Results are rendered across Folium GIS maps, Plotly interactive telemetry charts, and downloadable Latin-1 PDF briefings.
