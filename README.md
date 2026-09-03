<div align="center">
  <img src="assets/logo_circular.png" width="160" height="160" alt="ThermoRoute AI Logo" />
  
  # ThermoRoute AI
  
  ### *Hyperlocal Thermal Routing & Multi-Component EV Fleet Intelligence Engine*
  
  **FortyGuard Global AI Hackathon '26 · Track 03: Industrial & Enterprise**

  [![FortyGuard Temperature API](https://img.shields.io/badge/API-FortyGuard%20Temperature%20v1-1769b0?style=for-the-badge&logo=fastapi&logoColor=white)](https://www.fortyguard.com)
  [![Challenge Track](https://img.shields.io/badge/Track-03%20Industrial%20%26%20Enterprise-1f7ae0?style=for-the-badge&logo=google-cloud&logoColor=white)](https://www.fortyguard.com/hackathon26)
  [![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![Streamlit](https://img.shields.io/badge/UI-Streamlit%201.38-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

</div>

---

### 📊 Key Performance Metrics

| Metric | Baseline (Unmanaged) | ThermoRoute AI (Optimized) | Enterprise Impact |
| :--- | :---: | :---: | :---: |
| **Annual Operational Cost / Van** | `$15,598 / yr` | `$8,260 / yr` | **`$7,338 / van / yr` net savings** |
| **500-Van Fleet Annual Benefit** | `$7.80M` | `$4.13M` | **`$3.67M / year` net savings** |
| **5-Year Cumulative Enterprise Value** | — | — | **`$17.47M` net value** |
| **Arrhenius Cell Decay @ 111.4°F** | `4.20x rated wear` | `Optimized bypass` | **Under 2 months capital payback** |

---

## ⚡ Problem & Solution Overview

Commercial EV delivery fleets (**Amazon Logistics, DHL Express, FedEx Express, UPS**) deploy hundreds of thousands of electric delivery vans using legacy route optimization platforms that factor in only **distance** and **transit duration**.

In primary US Sunbelt logistics hubs such as **Phoenix, AZ**, surface-level roadway temperatures frequently reach **111.4°F (44.1°C)**. Under high solar load, the electrochemical degradation rate of commercial lithium-ion battery packs accelerates by **4.20x** relative to nominal baseline operating conditions (*Arrhenius kinetics with $E_a = 52.5\text{ kJ/mol}$*).

Operating an electric delivery van through unmanaged high-stress urban heat corridors imposes over **$15,598 per vehicle per year** in combined battery depreciation, auxiliary energy surcharges, and range overhead. **ThermoRoute AI** correlates street-level microclimate telemetry with turn-by-turn road geometry to redirect fleets to thermally optimal corridors, reducing annual operational exposure to **$8,260 per year**.

- **Net Unit Operational Savings:** **$7,338 per vehicle per year** across battery preservation, energy efficiency, and range overhead.
- **Fleet Scale (500 Active Units):** **$3.67M in annual operating value**, delivering a **5-year net benefit of $17.47M** with a capital payback horizon under **2 months**.

---

## 🛠️ System Architecture

```text
FortyGuard Temperature API® (/v1/heatmap, /v1/env_params, /v1/heat_intelligence)
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │            ThermoRoute AI Core Pipeline               │
 ├───────────────────────────┬────────────────────────────┤
 │ OSRM Real Road Geometry   │ Arrhenius Battery Kinetics │
 ├───────────────────────────┼────────────────────────────┤
 │ 3-Component Energy Model  │ Dynamic Cost Engine        │
 └───────────────────────────┴────────────────────────────┘
                             │
                             ▼
  Streamlit Enterprise UI (5 Interactive Operations Pages)
```

---

## 🚀 Quick Start Guide

### 1. Clone & Install
```bash
git clone https://github.com/DHANANJAY-2006/ThermoRoute-AI.git
cd ThermoRoute-AI
pip install -r requirements.txt
```

### 2. Configure FortyGuard API Key
Create a `.env` file in the project root:
```env
FORTYGUARD_API_KEY=c6f72638241a1bb121cc418de4aa82cd
```

### 3. Launch Dashboard
```bash
streamlit run app/main.py
```

---

## 📁 Repository Structure

```text
├── README.md                           # Main Architecture & Documentation
├── requirements.txt                    # Project Dependencies
├── assets/
│   ├── logo_circular.png               # High-Res Circular Brand Icon (Transparent PNG)
│   └── logo.png                        # App Icon Asset
├── app/
│   ├── main.py                         # Enterprise Executive Dashboard Landing
│   └── pages/
│       ├── 1_Fleet_Dashboard.py        # Regional Thermal Exposure Monitor
│       ├── 2_Route_Planner.py          # Turn-by-Turn Thermal Corridor Engine
│       ├── 3_Battery_Savings.py        # 3-Component Financial ROI Calculator
│       ├── 4_Forecast_Planner.py       # 12-Hour Shift Window Optimizer
│       └── 5_Executive_Report.py       # Operations Audit Brief & PDF Export
├── core/
│   ├── fortyguard_client.py            # FortyGuard 6-Endpoint Async Client
│   ├── battery_model.py                # Arrhenius Degradation Physics Engine
│   ├── ev_energy_model.py              # Auxiliary Energy & Range Overhead Model
│   ├── route_engine.py                 # OSRM Real Geometry & Scoring Pipeline
│   └── alert_manager.py                # Automated Thermal Risk Trigger System
└── docs/
    ├── whitepaper.md                   # Full Technical Whitepaper
    ├── architecture.md                 # System Architecture Reference
    ├── api_integration.md              # 6-Endpoint Reference Guide
    └── ThermoRoute_AI_Technical_Whitepaper.pdf
```

---

## 📜 Documentation & Technical Papers

- 📄 **[Technical Whitepaper](docs/whitepaper.md)**
- 📐 **[System Architecture Reference](docs/architecture.md)**
- 🔌 **[API Integration Guide](docs/api_integration.md)**
- 📋 **[Submission Brief](docs/submission_brief.md)**

---

<div align="center">
  <p><strong>ThermoRoute AI</strong> · Built for FortyGuard Global AI Hackathon '26</p>
</div>
