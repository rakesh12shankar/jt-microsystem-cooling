# Milestone 4 — verification and validation assessment

Numerical verification passed; baseline capacity validation failed; package validation unavailable.

## Experimental comparison

No fitting. Conditional on measured flow. 16 input corners per temperature are a deterministic screening range, not a statistical confidence interval or guaranteed global extrema. All model assumptions held fixed in that screen.

| Chip K | Measured mW | Predicted mW | Error % | Input-corner range mW | Overlap? |
|---:|---:|---:|---:|---:|:---:|
| 90 | 18.2 | 14.0 | -22.8 | 0.2–28.1 | yes |
| 95 | 48.6 | 40.1 | -17.6 | 34.6–45.6 | no |
| 100 | 63.0 | 41.8 | -33.6 | 36.3–47.4 | no |
| 110 | 69.8 | 48.4 | -30.6 | 42.8–54.0 | no |
| 120 | 97.0 | 72.6 | -25.1 | 66.9–78.4 | no |
| 130 | 121.9 | 96.8 | -20.6 | 90.9–102.8 | no |
| 140 | 142.7 | 116.9 | -18.1 | 110.8–123.0 | no |
| 153 | 146.9 | 121.1 | -17.6 | 114.2–128.0 | no |

MAE = 19.5 mW; RMSE = 21.1 mW. 1/8 points overlap the input-corner screen and ±1.12 mW measurement/reading allowance.

These errors establish that the baseline does not reproduce the selected published experiment within this screening allowance. Uncertainty in the assumed heat-loss model is not included in the band. The 153 K power is reported in text; the same conservative power allowance is retained.

## Discrepancy diagnosis

The baseline radiation loss is about twice the radiation shown in the authors’ model, Figure 8(b). That comparison implicates effective exposed area, insulation representation and wall-temperature distribution; it does not identify which is wrong. Radiation and outlet-temperature values from the authors’ model are correlated with their fitted emissivity and must not be treated as independent experimental evidence.

| Chip K | Baseline total radiation mW | Author-model radiation mW | Eq. 5 diagnostic net mW |
|---:|---:|---:|---:|
| 100 | 47.8 | 26 ±2 | 66.6–68.6 |
| 153 | 43.1 | 24 ±2 | 144.4–146.4 |

The diagnostic range varies axial conduction from 2 to 0 mW; it excludes reading/property/flow uncertainties. It substitutes the authors’ modeled warm outlet (294.9 K) and radiation in the whole-cooler energy balance. It is an accounting check, not a new validated simulation.

## Assumption sensitivity

| Scenario | Capacity at 100 K, mW | Capacity at 153 K, mW |
|---|---:|---:|
| baseline | 41.8 | 121.1 |
| interface 0 K/W | 42.3 | 123.1 |
| interface 30 K/W | 42.2 | 122.5 |
| interface 200 K/W | 41.3 | 119.2 |
| effectiveness 0.99 | 37.3 | 114.9 |
| effectiveness 0.9999 | 46.2 | 127.2 |
| radiation areas x0.5 | 65.5 | 142.4 |
| radiation areas x1.5 | 18.2 | 99.9 |
| low drop 0 kPa | 41.8 | 121.1 |
| low drop 90 kPa | 41.8 | 121.0 |
| high drop 0 kPa | 41.8 | 121.1 |
| high drop 100 kPa | 41.8 | 121.1 |

Area multipliers probe the radiation closure; they are not proposed geometry changes or fitted corrections. The pressure-drop sweeps are assumption scenarios, not measured uncertainty.

## Packaging consequence

The approximately 92 K detector result is not a validated design prediction. The empirical capacity map remains usable for explicitly conditional package heat-budget comparisons within the reference experiment’s domain. Its heater data do not validate the added die interface, supports, leads, optical window or vacuum enclosure.

Milestone 5 should compare package architectures using the measured net-capacity map with uncertainty bounds, report assumptions, and keep the real-fluid cycle as a sensitivity model until radiation and hydraulic closures are substantiated.

## Evidence needed to close validation

- Raw temperature–flow–heater data would tighten digitization; no additional PDF is required for this assessment.
- To resolve the physics discrepancy: exposed-area/insulation geometry and measured or independently calculated wall temperatures; temperature-dependent pressure drops and interface resistance.
- To validate the proposed package: a separate experiment reporting die and platform temperatures, dissipated power, interface, supports, leads and enclosure conditions. Tong (2024) proposes a complete detector package but does not report a completed integrated detector test, so it cannot supply this validation.

Source: Qi et al. (2023), https://doi.org/10.1016/j.applthermaleng.2023.120361, Figures 5, 8(b), A2, Table 1, Eq. 5. Packaging status: Tong et al. (2024), https://doi.org/10.1016/j.cryogenics.2024.103929.

See ../../docs/validation.md for verification gates and scope. Original milestone-3 configuration and results are preserved.
