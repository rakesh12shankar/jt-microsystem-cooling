# First simulation results

Status: preliminary package predictions using a published measured-performance map; not independent experimental validation.

| Scenario | Platform (K) | Detector (K) | Maximum device load for 100 K (mW) |
|---|---:|---:|---:|
| baseline | 91.47 | 92.21 | 40.09 |
| lower support conductance | 90.49 | 91.24 | 45.27 |
| higher support conductance | 97.61 | 98.34 | 14.36 |
| lower interface resistance | 91.47 | 91.62 | 45.05 |
| higher interface resistance | 91.46 | 94.42 | 25.61 |
| higher stage emissivity | 93.17 | 93.91 | 30.81 |
| extra 5mW optical load | 92.27 | 93.26 | 35.09 |
| extra gas conductance 20uW per K | 92.12 | 92.86 | 36.64 |

## Interpretation

Only added package loads are shown. The platform is the reference silicon chip, not the nitrogen evaporator. The detector sits across an additional interface.
Changes to support conductance and emissivity are scenario assumptions, not demonstrated material substitutions.
Maximum load is a steady-state target boundary; it does not guarantee cooldown with the device powered.

## Capacity uncertainty scenario

Scaling all capacities by 0.9 and 1.1 is an engineering sensitivity bracket, not a measured confidence interval. It does not cover temperature-axis digitization error or model-form uncertainty.

- Capacity scale 0.9: detector 92.69 K; allowable device load 35.06 mW.
- Capacity scale 1: detector 92.21 K; allowable device load 40.09 mW.
- Capacity scale 1.1: detector 91.82 K; allowable device load 44.99 mW.

## Verification versus validation

Run `python -m unittest -v`. Tests check a closed-form two-node solution, energy conservation, zero-load behavior, monotonic design trends, overload handling, and domain restrictions.
Agreement at supplied curve points is calibration/interpolation, not independent validation. Independent package validation is still outstanding.
