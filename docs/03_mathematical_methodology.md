# ThermoRoute AI — Mathematical & Electrochemical Methodology

## 1. Electrochemical Battery Degradation Model

### Arrhenius Reaction Rate Kinetics
The aging of lithium-ion cells (specifically Solid Electrolyte Interphase / SEI growth and active lithium inventory loss) is accelerated by thermal excitation according to the **Arrhenius reaction rate equation**:

$$k(T) = A \cdot \exp\left( -\frac{E_a}{R \cdot T} \right)$$

Taking the ratio against the nominal manufacturer rated baseline temperature ($T_0 = 298.15\text{ K} / 25.0^\circ\text{C} / 77.0^\circ\text{F}$):

$$\text{Degradation Factor } D(T) = \frac{k(T_{\text{effective}})}{k(T_0)} = \exp\left( \frac{E_a}{R} \left( \frac{1}{T_0} - \frac{1}{T_{\text{effective}}} \right) \right)$$

Where:
- $E_a = 52,500\text{ J/mol}$ ($52.5\text{ kJ/mol}$): Activation energy for SEI layer growth in commercial graphite anode / transition metal oxide cathode cells.
- $R = 8.314\text{ J/(mol}\cdot\text{K)}$: Universal gas constant.
- $T_0 = 298.15\text{ K}$: Baseline operating temperature.
- $T_{\text{effective}}$: Effective pack temperature in Kelvin, computed as:

$$T_{\text{effective}} = T_{\text{ambient}} + \Delta T_{\text{solar}} - \Delta T_{\text{shade}}$$

Where:
$$\Delta T_{\text{solar}} = \frac{I_{\text{solar}} \times \alpha}{100} \times 0.6$$
$$\Delta T_{\text{shade}} = T_{\text{ambient}} \times \left( \frac{\text{Shade \%}}{100} \right) \times 0.08$$

- $I_{\text{solar}}$: Direct solar irradiance ($\text{W/m}^2$) from FortyGuard `/v1/env_params`.
- $\alpha = 0.85$: Pavement/chassis absorptivity constant.

### Effective Battery Lifespan & CapEx Depreciation
Given nominal cycle lifespan $L_{\text{nominal}}$ (years) and battery replacement cost $C_{\text{replacement}}$ (USD):

$$\text{Effective Lifespan } L_{\text{effective}} = \max\left( 1.0, \frac{L_{\text{nominal}}}{D(T)} \right)$$

$$\text{Annual Battery Depreciation } C_{\text{degrade}} = \frac{C_{\text{replacement}}}{L_{\text{effective}}}$$

$$\text{Excess Degradation Cost } \Delta C_{\text{degrade}} = C_{\text{degrade}} - \frac{C_{\text{replacement}}}{L_{\text{nominal}}}$$

---

## 2. EV Energy Consumption Penalty Model

High ambient roadway temperatures increase EV energy consumption through two distinct mechanisms:
1. **Electrochemical Internal Resistance & Motor Inefficiencies:** $0.25\%$ increase in $\text{kWh/mile}$ per $^\circ\text{F}$ above $77.0^\circ\text{F}$.
2. **Auxiliary Thermal Management Load (HVAC & Pack Chilling):**
   - At $T \ge 105.0^\circ\text{F}$: Auxiliary draw of up to $8.5\text{ kWh/day}$.
   - At $85.0^\circ\text{F} \le T < 105.0^\circ\text{F}$: Auxiliary draw of $2.8\text{ kWh/day}$.

$$\text{Annual Efficiency Extra kWh} = (\text{Base kWh/mi} \times \Delta T \times 0.0025) \times \text{Daily Miles} \times 260\text{ Days}$$

$$\text{Annual Energy Penalty } C_{\text{energy}} = (\text{Annual Efficiency kWh} + \text{Annual Auxiliary kWh}) \times \text{Electricity Rate (\$/kWh)}$$

*Electricity Rate:* Commercial fleet utility benchmark ($0.14\text{ \$/kWh}$, US EIA).

---

## 3. Operational Range Overhead Model

Elevated temperatures reduce single-charge operating range at a rate of $0.35\%$ per $^\circ\text{F}$ above baseline (DOE Alternative Fuels Data Center benchmark):

$$\text{Range Reduction \%} = \max(0, T_{\text{ambient}} - 77.0) \times 0.0035$$

$$\text{Effective Range (miles)} = \text{Rated Range} \times (1 - \text{Range Reduction \%})$$

$$\text{Annual Range Overhead } C_{\text{range}} = \text{Range Reduction \%} \times \$30.00/\text{yr}$$

*Cost Basis:* Represents mid-route depot return labor, unscheduled DC fast charging overhead, and driver scheduling buffer.

---

## 4. Total Route Cost & ROI Synthesis

$$\text{Total Annual Route Exposure } C_{\text{total}} = C_{\text{degrade}} + C_{\text{energy}} + C_{\text{range}}$$

$$\text{Annual Savings per Van } S = C_{\text{unmanaged}} - C_{\text{optimized}}$$

$$\text{Total Fleet Annual Benefit } B_{\text{annual}} = S \times N_{\text{fleet}}$$

$$\text{5-Year Net Financial Benefit} = (B_{\text{annual}} - P_{\text{annual}}) \times 5$$

Where $P_{\text{annual}} = \$29.00/\text{van/month} \times 12 \times N_{\text{fleet}}$ (SaaS platform overhead).
