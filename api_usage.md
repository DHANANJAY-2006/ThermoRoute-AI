# FortyGuard Temperature API Usage Documentation

**Project:** ThermoRoute AI  
**Hackathon:** FortyGuard Global AI Hackathon '26 — Track 03: Industrial & Enterprise  
**Requirement:** FortyGuard Temperature API must be central to the project and documented.

---

## Overview

ThermoRoute AI uses **all 6 FortyGuard Temperature API endpoints** to power its EV fleet thermal routing engine. The API provides 2-meter above-ground, street-level ambient air temperature data for US cities, which we use to score delivery routes by battery degradation cost.

**Base URL:** `https://api.fortyguard.com`  
**Authentication:** `api-key: YOUR_API_KEY` header  
**Pattern:** Async submit-and-poll (all endpoints)  
**Coverage:** United States only  
**Data range:** January 1, 2021 → present + 12-hour forecast max  

---

## The Async Submit-and-Poll Pattern

All FortyGuard endpoints are **asynchronous**. You submit a task, receive an `activity_id`, then poll `/v1/status/{activity_id}` until completion.

```python
# Step 1: Submit task
response = requests.post(
    "https://api.fortyguard.com/v1/heatmap",
    headers={"api-key": API_KEY, "Content-Type": "application/json"},
    json={"location": "Phoenix, AZ", "analysis_layer": "exceedance"}
)
activity_id = response.json()["activity_id"]

# Step 2: Poll for result
while True:
    status = requests.get(
        f"https://api.fortyguard.com/v1/status/{activity_id}",
        headers={"api-key": API_KEY}
    ).json()
    
    if status["status"] == "completed":
        result = status["result"]
        break
    elif status["status"] == "failed":
        raise Exception(status["error"])  # failed = 0 credits consumed
    
    time.sleep(5)  # poll every 5 seconds
```

---

## Endpoint 1: POST /v1/heatmap

**Used for:** Temperature data per route segment (the core data source for route scoring)

**Analysis layers used:**
- `exceedance` — % of time above 95°F threshold → used for annual cost calculation
- `snapshot` — current temperature → used for real-time dashboard

**Request:**
```json
{
  "location": "33.4484,-112.0740",
  "analysis_layer": "exceedance",
  "timestamp": "now"
}
```

**Response:**
```json
{
  "status": "completed",
  "result": {
    "location": "Phoenix, AZ",
    "analysis_layer": "exceedance",
    "temperature_f": 112.0,
    "risk_level": "extreme",
    "exceedance_pct": 78.4,
    "resolution": "10mi²",
    "measured_at": "2m above ground",
    "geojson": { "type": "FeatureCollection", "features": [...] }
  }
}
```

**How we use it:** Called for each waypoint along a delivery route. The `exceedance` layer tells us what % of the operating day the road segment is above the critical battery temperature threshold — used to calculate annual battery degradation cost.

**Implementation:** `core/fortyguard_client.py → get_heatmap()` and `get_route_segment_temps()`

---

## Endpoint 2: POST /v1/satellite

**Used for:** Vegetation shield score — more vegetation = shaded roads = cooler routes

**Request:**
```json
{
  "location": "33.4484,-112.0740"
}
```

**Response:**
```json
{
  "status": "completed",
  "result": {
    "location": "Phoenix, AZ",
    "vegetation_pct": 8.2,
    "building_pct": 43.1,
    "pavement_pct": 38.7,
    "water_pct": 0.4,
    "other_pct": 9.6,
    "green_shield_score": 16.4
  }
}
```

**How we use it:** Low vegetation % → high pavement/building % → more radiated heat. We apply a shade reduction factor: roads with >30% vegetation are estimated to be up to 8°F cooler, which feeds into the effective temperature used in the Arrhenius degradation calculation.

**Implementation:** `core/fortyguard_client.py → get_satellite()`

---

## Endpoint 3: POST /v1/streetview

**Used for:** Ground-level thermal visualisation of hot vs cool route segments

**Request:**
```json
{
  "location": "33.4484,-112.0740"
}
```

**Response:**
```json
{
  "status": "completed",
  "result": {
    "location": "Phoenix, AZ",
    "ground_temp_f": 114.2,
    "surface_type": "asphalt",
    "shade_coverage_pct": 8.0
  }
}
```

**How we use it:** Visualise ground-level conditions on the Route Planner page. Shows the difference between a shaded road and an exposed asphalt surface street at driver/battery level.

**Implementation:** `core/fortyguard_client.py → get_streetview()`

---

## Endpoint 4: POST /v1/heat_intelligence

**Used for:** Auto-generated executive fleet thermal risk report

**Request:**
```json
{
  "location": "33.4484,-112.0740"
}
```

**Response:**
```json
{
  "status": "completed",
  "result": {
    "location": "Phoenix, AZ",
    "report_type": "multi_dimensional",
    "geographic_risk": "extreme",
    "environmental_risk": "extreme",
    "urban_risk": "critical",
    "overall_risk_score": 94.2,
    "summary": "Phoenix, AZ presents critical thermal conditions for fleet operations..."
  }
}
```

**How we use it:** Powers the Executive Report page. One click generates a full multi-dimensional risk assessment for the selected city, including geographic, environmental, and urban thermal risk layers. The summary text is included in the downloadable PDF report.

**Implementation:** `core/fortyguard_client.py → get_heat_intelligence()`, `app/pages/5_executive_report.py`

---

## Endpoint 5: POST /v1/env_params

**Used for:** Solar irradiance + heat index + persistence for effective battery temperature

**Analysis layer:** `persistence` — tracks sustained heat periods (heat waves)

**Request:**
```json
{
  "location": "33.4484,-112.0740",
  "analysis_layer": "persistence"
}
```

**Response:**
```json
{
  "status": "completed",
  "result": {
    "location": "Phoenix, AZ",
    "heat_index_f": 118.0,
    "solar_irradiance_wm2": 950.0,
    "aqi": 42,
    "humidity_pct": 14.0,
    "wind_speed_mph": 8.2,
    "analysis_layer": "persistence",
    "persistence_hours": 9.3
  }
}
```

**How we use it:**
- `solar_irradiance_wm2` → Added to ambient temperature to calculate **effective battery temperature** (direct sunlight heats the battery case beyond ambient air)
- `persistence_hours` → Input to the Alert Manager for heat wave detection
- `heat_index_f` → Shown in Executive Report as human health risk context

**Why `persistence` layer:** Sustained heat periods (not just peak moments) cause cumulative battery degradation. The `persistence` layer gives us total hours above the threshold — directly relevant to fleet operations planning.

**Implementation:** `core/fortyguard_client.py → get_env_params()`

---

## Endpoint 6: GET /v1/status/{activity_id}

**Used for:** Polling all async task results (used internally by all other endpoints)

**Request:** `GET https://api.fortyguard.com/v1/status/{activity_id}`

**Response states:**
```json
// Processing
{ "status": "processing" }

// Completed
{ "status": "completed", "result": { ... } }

// Failed (0 credits consumed)
{ "status": "failed", "error": "..." }
```

**How we use it:** Every API call above goes through the same poll loop in `core/fortyguard_client.py → _poll()`. We poll every 5 seconds with a 6-minute timeout. Failed tasks consume zero credits per FortyGuard documentation.

**Implementation:** `core/fortyguard_client.py → _poll()`

---

## Analysis Layer Selection Rationale

| Layer | When we use it | Why |
|---|---|---|
| `snapshot` | Real-time dashboard, current conditions | Point-in-time temperature reading |
| `exceedance` | Route cost calculations | % of day above threshold → annual cost impact |
| `persistence` | Alert system, heat wave detection | Sustained heat hours → cumulative degradation |

> **Key insight from Fawad Shah (FortyGuard Engineering Lead):** "Picking the wrong analysis layer will hand you a confident wrong answer." We use `exceedance` for cost calculations because a single snapshot temperature (even if extreme) doesn't tell you how long routes stay hot throughout the operating day.

---

## Forecast Usage

**Endpoint:** `POST /v1/heatmap` with `forecast_hours` parameter  
**Maximum:** 12 hours ahead (enforced in code — will raise `ValueError` if exceeded)  
**Used for:** Forecast Planner page — identifying optimal delivery windows for the shift ahead

```python
# Enforced in fortyguard_client.py
if hours_ahead > 12:
    raise ValueError("FortyGuard API only supports forecasts up to 12 hours ahead.")
```

---

## Credit Monitoring

```python
# POST /v1/system/fetch-api-key-usage
client.get_credit_usage()
# Returns: {"credits_used": N, "credits_remaining": M}
```

Used to monitor responsible API consumption throughout development.

---

## Data Compliance

| Rule | Our Implementation |
|---|---|
| US locations only | All demo cities: Phoenix AZ, Las Vegas NV, Dallas TX, Houston TX |
| Jan 2021 → present | All queries use `"timestamp": "now"` or recent historical dates |
| Max 12hr forecast | Enforced by `ValueError` in `get_forecast()` |
| Async pattern | All calls go through `_submit()` → `_poll()` |
| Failed = 0 credits | Handled in `_poll()` with `status == "failed"` branch |
| Proper licensing | All external data (EIA, Census) are public domain |
