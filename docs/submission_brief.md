# ThermoRoute AI: Hackathon Submission Information

**Event:** FortyGuard Global AI Hackathon '26  
**Track:** Track 03 — Industrial & Enterprise  
**Repository:** [https://github.com/DHANANJAY-2006/ThermoRoute-AI.git](https://github.com/DHANANJAY-2006/ThermoRoute-AI.git)  

---

## Submission Form Copy-Paste Fields

### Project Name
```text
ThermoRoute AI
```

### Track
```text
Track 03: Industrial & Enterprise
```

### Tagline / One-Liner
```text
Hyperlocal thermal routing and battery degradation mitigation for commercial electric vehicle fleets powered by FortyGuard Temperature API®.
```

### Short Description (Form Box)
```text
Commercial EV fleets route delivery vans based solely on distance and transit time. In summer heat across Sunbelt hubs like Phoenix (111.4°F ambient), battery packs degrade at over 4 times their rated baseline speed (Arrhenius kinetics), while auxiliary cooling and range loss add severe operating costs. This results in over $15,598 per van per year in premature battery depreciation, energy penalties, and range overhead.

ThermoRoute AI integrates all six production endpoints of FortyGuard's Temperature API (sampled at 2.0m elevation) with turn-by-turn road geometry to redirect fleets along thermally optimal corridors.

Key Results:
- $7,338 annual savings per vehicle across battery wear, energy, and range overhead.
- $3.67M annual operating savings for a 500-van fleet ($17.47M 5-year net value).
- Capital payback in under 2 months.
```

### How FortyGuard API Is Used
```text
ThermoRoute AI integrates all 6 FortyGuard Temperature API endpoints:
- POST /v1/heatmap: Queries waypoint temperatures using the exceedance layer to measure sustained heat exposure above 95°F.
- POST /v1/satellite: Ingests canopy vegetation percentages to calculate route shading relief.
- POST /v1/env_params: Pulls solar irradiance and heat persistence hours to determine effective battery cell temperatures.
- POST /v1/heat_intelligence: Synthesizes multi-dimensional risk scores for automated executive reporting.
- POST /v1/streetview: Inspects 2m-elevation ground pavement thermography.
- GET /v1/status/{id}: Non-blocking asynchronous task polling with exponential backoff.
```

### GitHub Repository URL
```text
https://github.com/DHANANJAY-2006/ThermoRoute-AI.git
```
