# 🚗⚡ ThermoRoute AI

> **Route EV delivery fleets by battery damage, not just distance.**  
> Powered by **FortyGuard Temperature API®** — FortyGuard Global AI Hackathon '26 · Track 03: Industrial & Enterprise

[![FortyGuard API](https://img.shields.io/badge/Powered%20by-FortyGuard%20Temperature%20API-1769b0?style=flat-square)](https://www.fortyguard.com)
[![Track](https://img.shields.io/badge/Track-03%20Industrial%20%26%20Enterprise-1f7ae0?style=flat-square)](https://www.fortyguard.com/hackathon26)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-ff4b4b?style=flat-square&logo=streamlit)](https://streamlit.io)

---

## 🔍 The Problem Nobody Solved

EV delivery fleets — Amazon, DHL, UPS, FedEx — route their vans using Google Maps: shortest distance or fastest time. **Nobody considers temperature.**

At **112°F in Phoenix**, lithium-ion batteries degrade **3.78× faster** than at the ideal 77°F baseline. A van routing through downtown Phoenix surface streets loses **$3,200/year** in battery wear. The same delivery via the highway route costs only **$1,400/year**.

**Same stops. Same driver. $1,800 saved — just by choosing a cooler road.**

For a fleet of 500 vans: **$900,000 saved annually.**

---

## ⚡ What ThermoRoute AI Does

1. **🗺️ Route Planner** — Scores every route by thermal damage using FortyGuard street-level temperature data. Recommends the coolest path.
2. **💰 Savings Calculator** — Translates temperature into exact dollar cost using the Arrhenius battery degradation equation.
3. **📅 Forecast Planner** — Uses FortyGuard's 12-hour forecast to find the safest delivery windows for the shift ahead.
4. **📄 Executive Report** — Auto-generates fleet thermal risk PDF using FortyGuard's `/v1/heat_intelligence` endpoint.
5. **🚨 Autonomous Alerts** — Flags critical heat days and recommends actions without human input.

---

## 🔬 The Science

Based on the **Arrhenius battery degradation equation** — the same kinetics model used by Tesla, Rivian, and GM to rate battery lifespan.

```
Degradation Factor = 2 ^ ((T - 77°F) / 18°F)

At 77°F  → 1.0× (baseline)
At 95°F  → 2.0× (twice as fast)
At 112°F → 3.78× (Phoenix, AZ)
At 130°F → 7.1× (extreme)
```

FortyGuard provides **2-meter above ground, street-level temperature data** — the same height as a delivery van's battery pack.

---

## 📡 FortyGuard API Usage

All **6 Temperature API endpoints** are used. See [`api_usage.md`](api_usage.md) for full documentation with payloads and responses.

| Endpoint | Usage | Analysis Layer |
|---|---|---|
| `POST /v1/heatmap` | Temperature per route segment | `exceedance` + `snapshot` |
| `POST /v1/satellite` | Vegetation shade coverage | Default |
| `POST /v1/streetview` | Ground-level road visualisation | `snapshot` |
| `POST /v1/heat_intelligence` | Executive PDF report | Multi-dimensional |
| `POST /v1/env_params` | Solar irradiance + heat index | `persistence` |
| `GET /v1/status/{id}` | Async task polling | — |

**API Compliance:**
- ✅ US locations only (Phoenix AZ, Las Vegas NV, Dallas TX, Houston TX)
- ✅ Historical data: January 2021 → present
- ✅ Forecast: max 12 hours ahead (enforced in code)
- ✅ Async submit-and-poll pattern implemented
- ✅ Failed calls = 0 credits (error handling built in)
- ✅ All datasets with open licenses

---

## 🛠️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/thermoroute-ai.git
cd thermoroute-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env: add your FortyGuard API key
# Set DEMO_MODE=false to use live API

# 4. Run the app
streamlit run app/main.py
```

**Demo Mode:** Set `DEMO_MODE=true` in `.env` to run without an API key using realistic simulated data.

---

## 📁 Project Structure

```
thermoroute-ai/
├── app/
│   ├── main.py                    # Homepage
│   └── pages/
│       ├── 1_fleet_dashboard.py   # City-wide heat risk
│       ├── 2_route_planner.py     # Core thermal routing
│       ├── 3_battery_savings.py   # Financial calculator
│       ├── 4_forecast_planner.py  # 12-hour window planner
│       └── 5_executive_report.py  # PDF report generator
├── core/
│   ├── fortyguard_client.py       # FortyGuard API wrapper (all 6 endpoints)
│   ├── battery_model.py           # Arrhenius degradation model
│   ├── route_engine.py            # Route scoring logic
│   ├── cost_calculator.py         # ROI calculations
│   └── alert_manager.py           # Autonomous alerts
├── data/
│   ├── demo_routes.json           # Phoenix, Vegas, Dallas, Houston routes
│   ├── ev_specs.json              # Rivian EDV, Mercedes eSprinter, Ford E-Transit
│   └── electricity_prices.json    # US EIA state prices
├── api_usage.md                   # FortyGuard API documentation
└── requirements.txt
```

---

## 💰 Impact

| Operator | EV Fleet | Annual Battery Savings |
|---|---|---|
| Amazon | 100,000 vans | $180,000,000 |
| DHL *(FortyGuard partner)* | 35,000 vans | $63,000,000 |
| UPS | 10,000 vans | $18,000,000 |
| FedEx | 5,000 vans | $9,000,000 |

> DHL is a **FortyGuard technology partner**. ThermoRoute AI is built for their fleet.

---

## 🏆 Hackathon

- **Event:** FortyGuard Global AI Hackathon '26 — *Building the World's Temperature AI*
- **Track:** 03 — Industrial & Enterprise
- **Deadline:** August 30, 2026 · 11:59 PM GST

---

*Built with ❤️ using FortyGuard Temperature API® — NVIDIA-recognized technology*
