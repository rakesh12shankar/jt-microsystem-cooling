# Milestone 3: real-fluid baseline

Baseline implementation complete; predictive capacity validation not passed. No parameter fitting performed in this run.

## Coupled baseline

- Nitrogen saturation temperature: 87.34 K (paper: 87.3 K).
- Reference platform: 91.31 K; additional detector: 92.05 K.
- Gross cold-region heat pickup: 39.68 mW.
- Net capacity after reference cold radiation and axial conduction: 27.14 mW.
- Recuperator radiation pickup (separate): 36.83 mW.
- No-extra-package-load platform: 88.60 K (paper: 88.5 K).
- Restriction diagnostic: 4.15 mg/s; cycle uses prescribed 4.2 mg/s.

## Five cycle states

| State | Pressure (MPa) | Temperature (K) | Enthalpy (kJ/kg) | Vapor mass fraction |
|---|---:|---:|---:|---:|
| 1 warm high in | 11.100 | 295.00 | 284.11 | single phase |
| 2 cold high before valve | 11.050 | 88.30 | -92.53 | single phase |
| 3 after valve | 0.285 | 87.34 | -92.53 | 0.047 |
| 4 evaporator return | 0.285 | 87.34 | -83.08 | 0.098 |
| 5 warm low out | 0.240 | 291.79 | 302.32 | single phase |

The wet return means liquid continues into the recuperator. This state is included thermodynamically; actual two-phase pressure drop and distributed heat transfer are not resolved. Enthalpy reference zero is arbitrary.

## Capacity comparison

| Platform temperature | Reference (mW) | Model (mW) | Difference |
|---|---:|---:|---:|
| 100 K | 63.0 | 41.6 | -34.0% |
| 153 K | 146.9 | 120.2 | -18.1% |

The near agreement in no-load temperature is insufficient to establish validity: platform thermal resistance is an assumed input and the same pressure boundary determines the saturation temperature. The capacity discrepancies are material.

## Numerical checks

- Maximum local/cycle/package energy residual: 3.80e-14 W.
- Valve enthalpy residual: 0.00e+00 J/kg.
- Minimum sampled recuperator temperature difference: 0.963 K.
- Detector temperature spread across 41/81/161 pinch samples: 0 K.

## Effectiveness sensitivity

- Effectiveness 0.98: equilibrium; detector 107.21097910624628 K.
- Effectiveness 0.995: equilibrium; detector 92.04924326420364 K.
- Effectiveness 0.999: equilibrium; detector 92.04924326420718 K.

## Interpretation and next milestone

Milestone 3 is complete for the agreed simplified steady-state baseline: real-fluid properties, recuperation, isenthalpic throttling, phase tracking, explicit reference heat leaks, and coupled package balance.
Milestone 4 must address independent validation, improved figure digitization, heat-transfer/radiation distribution, interface resistance and two-phase hydraulic closure. No allowable-load or design superiority claim should be based on this model yet.
See ../../docs/realfluid_model.md for equations, boundaries, assumptions and deferred physics.
