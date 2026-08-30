# ThermoRoute AI: FortyGuard Temperature API® Integration Reference

## 1. Summary of Implemented Endpoints

ThermoRoute AI integrates all six production endpoints of the FortyGuard Temperature API®:

| Endpoint | Method | Analysis Layer | Usage in Platform |
| :--- | :--- | :--- | :--- |
| `/v1/heatmap` | POST | `exceedance`, `snapshot` | Waypoint-level corridor scoring & Regional Fleet Dashboard |
| `/v1/satellite` | POST | Default | Vegetation canopy shading factors |
| `/v1/streetview` | POST | `snapshot` @ 2m | Ground-level roadway thermal segmentation |
| `/v1/heat_intelligence` | POST | Multi-dimensional | Automated executive risk briefings |
| `/v1/env_params` | POST | `persistence` | Solar irradiance, heat index, and heat persistence hours |
| `/v1/status/{id}` | GET | — | Asynchronous task polling and lifecycle management |

---

## 2. Endpoint Implementation Details

### `POST /v1/heatmap`
- **Request Payload:** `{ "location": "33.4484,-112.0740", "analysis_layer": "exceedance" }`
- **Purpose:** Extracts temperature telemetry across transit corridors. The `exceedance` layer provides multi-hour exposure probability above the 95°F critical battery threshold.
- **Used In:** `core/route_engine.py` (corridor scoring) and `app/pages/1_Fleet_Dashboard.py`.

### `POST /v1/satellite`
- **Request Payload:** `{ "location": "33.4484,-112.0740" }`
- **Purpose:** Retrieves multispectral canopy vegetation percentages (`vegetation_pct`), which are used to apply a temperature discount to shaded route segments.
- **Used In:** `core/route_engine.py` and `app/pages/2_Route_Planner.py`.

### `POST /v1/env_params`
- **Request Payload:** `{ "location": "33.4484,-112.0740", "analysis_layer": "persistence" }`
- **Purpose:** Retrieves direct solar irradiance ($\text{W/m}^2$) and continuous heat duration (`persistence_hours`). Solar radiation is incorporated into effective cell temperature calculations.
- **Used In:** `core/battery_model.py` and `core/alert_manager.py`.

### `POST /v1/heat_intelligence`
- **Request Payload:** `{ "location": "33.4484,-112.0740" }`
- **Purpose:** Combines geographic, environmental, and urban microclimate layers into an operational risk synthesis.
- **Used In:** `app/pages/5_Executive_Report.py` (executive briefings).

### `POST /v1/streetview`
- **Request Payload:** `{ "location": "33.4484,-112.0740", "analysis_layer": "snapshot" }`
- **Purpose:** Street-level ground thermography at 2m elevation.
- **Used In:** Route telemetry strip and spatial inspection.

### `GET /v1/status/{activity_id}`
- **Purpose:** Polling endpoint for the asynchronous task lifecycle. The client polls every 5 seconds up to a 60-second deadline.

---

## 3. Compliance and Operational Guardrails

- **12-Hour Forecast Boundary:** The client strictly enforces `hours_ahead <= 12`, raising a `ValueError` if an invalid range is requested.
- **Geographic Boundaries:** Restricted to US logistics markets (Phoenix AZ, Las Vegas NV, Dallas TX, Houston TX).
- **Elevation Matching:** Telemetry is sampled at 2.0m above ground level, matching commercial delivery van battery chassis enclosures.
