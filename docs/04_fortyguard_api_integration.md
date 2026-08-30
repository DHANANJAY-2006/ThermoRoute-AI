# ThermoRoute AI — FortyGuard Temperature API® Integration

## 1. Overview of FortyGuard Integration

ThermoRoute AI integrates all six production endpoints provided by the **FortyGuard Temperature API®**, utilizing Large Temperature Models (LTMs) to pull high-precision 2-meter street-level thermal data.

| # | Endpoint | HTTP Method | Analysis Layer Used | Platform Feature |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `/v1/heatmap` | `POST` | `exceedance`, `snapshot` | Waypoint corridor scoring & Fleet Dashboard |
| 2 | `/v1/satellite` | `POST` | Default multispectral | Canopy shade & vegetation percentage |
| 3 | `/v1/streetview` | `POST` | `snapshot` @ 2m elevation | Ground-level pavement thermography |
| 4 | `/v1/heat_intelligence` | `POST` | Multi-dimensional synthesis | Automated executive risk briefings |
| 5 | `/v1/env_params` | `POST` | `persistence` | Solar irradiance, heat index, and heat persistence |
| 6 | `/v1/status/{id}` | `GET` | — | Non-blocking asynchronous task lifecycle polling |

---

## 2. Analysis Layer Technical Selection

### `exceedance` vs `snapshot` on `/v1/heatmap`
- **Why `exceedance`:** For logistics route optimization, evaluating instantaneous temperature alone is insufficient because fleet delivery cycles span multiple hours. The `exceedance` layer provides the probability and temporal proportion of a roadway exceeding the 95°F critical threshold, giving robust multi-hour operational reliability.
- **When `snapshot` is used:** Used for current-state regional comparison across the multi-city Fleet Risk Monitor.

### `persistence` on `/v1/env_params`
- Battery degradation accelerates exponentially when elevated temperatures are sustained for prolonged periods. The `persistence` layer quantifies continuous high-heat hours (e.g., 9.3 continuous hours in Phoenix), informing the Arrhenius kinetic multiplier and autonomous alert dispatching.

---

## 3. Asynchronous Lifecycle Implementation

All FortyGuard endpoints implement an asynchronous polling architecture:
1. **Task Dispatch:** A `POST` request is sent with the coordinate payload, returning an `activity_id` and initial status.
2. **Polling Loop:** The client polls `GET /v1/status/{activity_id}` at 5-second intervals with exponential backoff up to a 60-second deadline.
3. **Credit Preservation:** If a task returns an error status, execution halts immediately without consuming extraneous API credits.
4. **Fallback & Demo Mode:** When running in demonstration mode or if external connectivity is interrupted, the client falls back to local calibrated telemetry vectors derived from FortyGuard US regional baseline records.

---

## 4. API Constraint Adherence

- **Geographic Scope:** Strictly United States territory (Phoenix AZ, Las Vegas NV, Dallas TX, Houston TX).
- **Temporal Horizon:** Forecast queries strictly enforce a maximum of 12 hours forward (`hours_ahead <= 12`), raising an explicit `ValueError` if an out-of-bounds horizon is requested.
- **Elevation Match:** Telemetry is anchored to 2.0 meters above ground level (AGL), matching the physical mounting height of commercial EV battery enclosures.
