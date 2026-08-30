# ThermoRoute AI — Hackathon Submission Brief & Checklist

**Event:** FortyGuard Global AI Hackathon '26  
**Track:** Track 03 — Industrial & Enterprise  
**Repository:** [https://github.com/DHANANJAY-2006/ThermoRoute-AI.git](https://github.com/DHANANJAY-2006/ThermoRoute-AI.git)  

---

## 1. Submission Metadata

- **Project Title:** ThermoRoute AI — Enterprise Thermal Fleet Intelligence
- **Track Selection:** Track 03: Industrial & Enterprise
- **Tagline:** Autonomous thermal microclimate routing and battery degradation management for commercial EV fleets powered by FortyGuard Temperature API®.
- **GitHub URL:** `https://github.com/DHANANJAY-2006/ThermoRoute-AI.git`
- **Tech Stack:** Python 3.11+, Streamlit, FortyGuard Temperature API®, Folium GIS, OpenStreetMap / OSRM, Plotly, FPDF, NumPy, Pandas.

---

## 2. Submission Form Field Answers

### Short Description (Under 200 words)
> Commercial EV fleets route vehicles based on distance and transit time, ignoring roadway thermal microclimates. In high-heat logistics hubs like Phoenix, summer asphalt temperatures reach 111.4°F, causing commercial Li-ion battery packs to degrade at 4.20x the nominal rate (Arrhenius kinetics). This imposes over $15,598 per van per year in premature battery depreciation, auxiliary HVAC energy surcharges, and range overhead.
>
> ThermoRoute AI integrates all six production endpoints of the FortyGuard Temperature API® (measured at 2.0m elevation to match chassis height) with turn-by-turn routing geometry. By evaluating street-level heatmaps, canopy shade, and solar persistence, the engine redirects delivery fleets to thermally optimal corridors.
>
> Result: $7,338 saved per vehicle per year, delivering $3.67M in annual fleet savings and $17.47M in 5-year net value for a 500-van fleet with a payback period under 2 months.

### How it uses FortyGuard API
> ThermoRoute AI integrates all 6 FortyGuard Temperature API® endpoints:
> 1. `POST /v1/heatmap` — Waypoint thermal corridor telemetry using `exceedance` and `snapshot` layers.
> 2. `POST /v1/satellite` — Canopy vegetation coverage and solar radiation shielding factors.
> 3. `POST /v1/streetview` — Street-level pavement thermography at 2m elevation.
> 4. `POST /v1/heat_intelligence` — Multi-dimensional operational risk synthesis and executive briefing generation.
> 5. `POST /v1/env_params` — Direct solar irradiance, heat index, and thermal persistence tracking.
> 6. `GET /v1/status/{id}` — Asynchronous task polling and lifecycle management.

---

## 3. Video Submission Instructions

1. **Record the Video:** Follow the structured 3:00–3:45 min walkthrough script provided in `video_script.md`.
2. **Hosting Options:**
   - **YouTube (Recommended):** Upload video, set visibility to **Unlisted** (so anyone with the link can watch, but it is not public on search).
   - **Loom / Google Drive:** Ensure link permissions are set to **"Anyone with the link can view"**.
3. **Submit URL:** Paste the video URL into the official FortyGuard submission portal form.
