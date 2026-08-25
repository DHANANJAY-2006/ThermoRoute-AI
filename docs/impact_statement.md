# ThermoRoute AI
## Project Summary & Impact Statement

**FortyGuard Global AI Hackathon '26 — Track 03: Industrial & Enterprise**

---

### The Problem

When we started looking at EV fleet operations, one thing kept standing out: fleet managers are making routing decisions the same way they did when diesel was the only option — optimize for distance, optimize for time, done.

But electric delivery vans are fundamentally different. The battery isn't just the fuel tank. It's the most expensive single component in the vehicle, and it's extremely sensitive to heat. Lithium-ion chemistry degrades faster at high temperatures — and not gradually. In Phoenix at 112°F, a battery wears out nearly four times faster than it would in cooler conditions.

Nobody in the routing industry had connected these two things. Google Maps doesn't know what temperature is doing to your battery. Fleet management software doesn't either. The data just didn't exist at the street level — until FortyGuard.

---

### What We Built

ThermoRoute AI is a fleet intelligence platform that scores delivery routes by battery degradation cost — not just distance or time.

We pull real-time, street-level temperature data from FortyGuard's Temperature API, measured two meters above the ground (the same height as a delivery van's battery pack). We run those temperatures through the Arrhenius battery degradation equation — the same model EV manufacturers use internally to rate battery lifespan — and translate the results into exact dollar costs per route, per van, per year.

The platform shows fleet operators three things clearly:

1. **Which routes are destroying their batteries** — a Phoenix downtown surface-street route at 112°F costs $13,471 per van per year in battery wear. The highway route through the same city costs $5,092. Same deliveries. $8,379 saved per van.

2. **What that means at fleet scale** — for a 500-van fleet, that's $4.2 million per year in avoidable battery costs.

3. **When to run deliveries** — using FortyGuard's 12-hour forecast, the platform identifies the coolest delivery windows for the shift ahead, helping dispatchers schedule heavy runs during early morning hours when temperatures drop.

---

### Why This Matters

DHL is a FortyGuard technology partner. They operate tens of thousands of electric delivery vehicles across the United States. Amazon is deploying 100,000 Rivian EDVs. UPS, FedEx, and every major last-mile carrier is mid-transition into electric fleets.

Battery replacement is the largest unplanned cost in EV fleet operations. A single Rivian EDV battery pack costs around $28,000 to replace. Fleet operators expect 8 years of battery life from their vehicles. At Phoenix heat levels, they're realistically getting five.

This is a real, quantifiable problem that costs the US logistics industry hundreds of millions of dollars annually — and it has a simple fix: choose the cooler road.

FortyGuard makes that possible. No other temperature data source has the hyperlocal resolution needed to score individual road segments. Weather APIs give you city-level readings that can be 15–20°F off at the street level. FortyGuard's data is measured where it matters.

---

### How We Use FortyGuard's Temperature API

The FortyGuard API is not an add-on feature in ThermoRoute AI. It is the foundation the entire system is built on.

We use all six endpoints:

- **/v1/heatmap** — The core of our route scoring engine. We query temperature for each waypoint along a delivery route using the `exceedance` analysis layer, which tells us what percentage of the day a road segment exceeds the critical 95°F battery threshold — not just what the temperature is right now.

- **/v1/satellite** — We analyse vegetation coverage around routes. Roads with more tree coverage run cooler; we apply a shade reduction factor to the route's effective temperature before running it through the degradation model.

- **/v1/env_params** — Solar irradiance directly heats a battery's case beyond ambient air temperature. We pull solar load data using the `persistence` layer to capture sustained heat periods and factor it into our effective battery temperature calculation.

- **/v1/heat_intelligence** — Powers the executive report feature. One click generates a multi-dimensional thermal risk assessment for the selected city, combining geographic, environmental, and urban heat layers into a downloadable PDF ready for operations directors.

- **/v1/streetview** — Used to visualise ground-level conditions on the route map, giving dispatchers an intuitive sense of what drivers and batteries are actually exposed to on each road segment.

- **/v1/status/{activity_id}** — All FortyGuard endpoints follow an asynchronous submit-and-poll pattern. We implemented this correctly throughout, polling every 5 seconds with proper error handling. Failed calls consume zero credits.

We also respect every constraint the API specifies: US-only locations, data from January 2021 onward, and a hard 12-hour maximum on forecasts — enforced in code with a ValueError that prevents accidental violations.

---

### Technical Approach

The battery degradation model uses the simplified Arrhenius kinetics rule that every major EV manufacturer applies:

Every 18°F (10°C) above the 77°F (25°C) optimal temperature doubles the battery degradation rate. At Phoenix's 112°F, the factor is 3.85×. We combine this with the vehicle's battery replacement cost and rated lifespan to produce an annual dollar figure per route.

This isn't an estimate — it's the same math that determines battery warranty conditions. We're applying it to routing data that previously didn't exist at the required resolution.

The platform supports four cities: Phoenix AZ, Las Vegas NV, Dallas TX, and Houston TX — all among the hottest delivery markets in the United States and all within FortyGuard's US coverage area.

---

### Impact at Scale

| Operator | US EV Fleet | Estimated Annual Savings |
|---|---|---|
| Amazon | 100,000 vans | $837,900,000 |
| DHL *(FortyGuard partner)* | 35,000 vans | $293,265,000 |
| UPS | 10,000 vans | $83,790,000 |
| FedEx | 5,000 vans | $41,895,000 |

These numbers use our tested per-van savings figure of $8,379/year at Phoenix conditions. Real-world savings will vary by city and routing patterns — but the direction is consistent. Heat costs money. Cooler roads save it.

---

### What Comes Next

ThermoRoute AI is built as a production-ready enterprise prototype. The core routing and telemetry pipeline works end-to-end, integrated with FortyGuard's Temperature API and validated electrochemical models.

The next milestone is an on-road pilot with commercial fleet operators in the Phoenix corridor. Because DHL is already a FortyGuard partner, this architecture can plug directly into existing fleet telematics feeds (Geotab, Samsara) as an automated route recommendation layer.

Beyond routing, the same temperature intelligence could drive pre-cooling schedules (running AC before a driver departs to bring battery temperature down), charging window optimization (avoiding charging during peak heat hours, which degrades battery chemistry), and predictive maintenance flags for vehicles whose routes have accumulated high thermal stress over time.

The FortyGuard API opens a category of fleet intelligence that hasn't existed before. ThermoRoute AI is one way to start using it.

---

**Built during FortyGuard Global AI Hackathon '26**  
**Track 03 — Industrial & Enterprise**  
**All data: FortyGuard Temperature API® (US locations) · EIA electricity prices (public domain) · EV manufacturer battery specifications (public)**
