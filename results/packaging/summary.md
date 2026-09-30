# Milestone 5 — packaging tradeoffs

Conditional package tradeoff study completed; no integrated-package experimental validation.

## Question and architecture

How much useful detector dissipation can an added package support at 100 K while limiting support deflection and lead resistance? The reference Qi chip remains the cold platform. A separate 3 × 3 mm die connects across an added interface. Four supports connect the platform to the warm enclosure; eight wires connect the die to warm feedthroughs. A gray optical aperture, exposed opaque surfaces and residual gas add heat.

The 10 mW device load and 100 K target are project assumptions, not requirements supplied by a detector manufacturer. The study is steady-state; startup, reliability and integrated-package performance are unvalidated.

## Results

| Architecture | Die K at 10 mW | Max device power mW | Capacity-only range mW | Combined adverse mW | Mechanical/electrical screen |
|---|---:|---:|---:|---:|---|
| A: steel supports | 137.8 | infeasible | infeasible–infeasible | infeasible | pass / pass |
| B: G10 compact | 91.3 | 44.6 | 39.0–50.3 | 29.2 | pass / pass |
| C: G10 long thin | 90.4 | 51.3 | 45.2–57.4 | 37.4 | pass / fail |
| D: G10 long reinforced | 90.9 | 48.4 | 42.2–54.3 | 34.1 | pass / pass |

Ranges cover only capacity-reading scenarios. Combined adverse values vary multiple package assumptions together. Neither is a statistical confidence interval. “Infeasible” means even zero device dissipation cannot meet 100 K in this branch. A thermal limit remains listed for C to show why thermal ranking alone is insufficient.

## Geometry and preliminary constraints

All supports: four tabs, width 0.30 mm. Leads: eight 304 stainless wires, diameter 25 um. The material choice is a low-current thermal candidate with assumed electrical resistivity; it is not a qualified detector interconnect.

| Architecture | Support L / thickness mm | Wire L mm | Interface K/W | Deflection um | Lead resistance ohm |
|---|---:|---:|---:|---:|---:|
| A: steel supports | 2.0 / 0.10 | 10 | 50 | 0.07 | 14.7 |
| B: G10 compact | 2.0 / 0.10 | 10 | 50 | 0.65 | 14.7 |
| C: G10 long thin | 3.0 / 0.10 | 20 | 20 | 2.21 | 29.3 |
| D: G10 long reinforced | 3.0 / 0.15 | 10 | 20 | 0.65 | 14.7 |

Mechanical screen: equal-load cantilever bending under a 5 mg payload at 10 g; deflection ≤10 um and stress ≤50 MPa. Electrical screen: ≤20 ohm per lead at 100 uA assumed current. Moduli and resistance limits are design assumptions. This is not a structural or electrical qualification.

## Interpretation

- The steel-support case demonstrates how a warm-to-cold mechanical path can consume the cooling budget. A working cooler alone does not establish package feasibility.
- Architecture C reduces support/wire heat leakage and passes the nominal bending screen; it fails the lead-resistance limit.
- B and D are candidates for further study. D changes both support geometry and interface resistance. The one-at-a-time interface sweep isolates the thermal advantage; reinforcement itself is not claimed to improve cooling.
- B and D have equal support thickness/length ratios, so this beam model gives equal support heat leakage and stiffness. Longer supports offer no free thermal gain when thickness is raised proportionally to preserve stiffness.
- No design is selected for fabrication. Required next evidence includes cryogenic joints, actual detector pin count/current, G10 directional stiffness, optical spectral response, and vacuum-compatible assembly.

## One-at-a-time changes from B

| Change | Max device power at 100 K, mW |
|---|---:|
| B baseline | 44.6 |
| interface 20 K/W | 48.4 |
| interface 100 K/W | 39.5 |
| 16 leads | 43.7 |
| 50 um leads | 41.8 |
| stage emissivity 0.2 | 39.1 |
| gas G = 20 uW/K | 41.3 |
| aperture diameter 2 mm | 44.3 |
| lead current 10 mA | 32.9 |

These comparisons hold all other inputs fixed. The 10 mA case includes conservative deposition of all wire Joule heat at the die. The model does not assess voltage drop, bandwidth or noise beyond the resistance screen.

## Added heat budget at 10 mW

| Path | B heat, mW | D heat, mW |
|---|---:|---:|
| device | 10.000 | 10.000 |
| supports | 8.005 | 8.005 |
| leads | 0.985 | 0.987 |
| lead joule | 0.001 | 0.001 |
| stage radiation | 2.128 | 2.128 |
| die radiation | 0.699 | 0.699 |
| optical | 0.167 | 0.167 |
| gas | 0.102 | 0.102 |

Only added loads appear here. Reference-cooler heat leaks are already embedded in Qi’s measured net capacity and are not subtracted a second time.

## Uncertainty and limitations

Capacity-only lower/upper: shift chip temperature by ±1.2 K and power by ±3.12 mW, inside common interpolation domain. Adverse case additionally combines support k +20%, lead k +10%, interface R x2, stage/die emissivity x2, gas G=10 uW/K, optical factor=1, resistivity +20%, modulus -30%. These are engineering scenarios, not confidence bounds or manufacturing tolerance guarantees.

- All geometry, payload, acceleration, interface, optical, vacuum and acceptance limits are project design assumptions, not dimensions demonstrated in Qi or Tong.
- Young modulus values are screening assumptions; G10 modulus is swept ±30%. Neither is an allowable or a temperature-dependent mechanical model.
- Lead resistivity is an assumed constant swept ±20%, not a sourced cryogenic electrical fit. Stainless leads represent a low-current thermal candidate; bonding, signal integrity and detector pin count require validation.
- Conservative electrical heating: all I^2R from eight leads deposited at detector; actual partition is unresolved.
- Four equal-load cantilevers under out-of-plane acceleration are a preliminary screen; no buckling, resonances, joint failure, cooldown mismatch, in-plane restraint or vacuum qualification is predicted.
- Extra gas conductance is an effective parameter; no chamber-pressure specification is inferred. Optical gray factor combines transmission, absorptance and view factor; spectral detector loading is not resolved.
- All paths are additional to the measured reference chip/cooler assembly. Aperture area is removed from opaque die radiation to avoid duplicate surface loading.

## Sources and reproducibility

- Cooler reference: Qi et al. (2023), Applied Thermal Engineering, https://doi.org/10.1016/j.applthermaleng.2023.120361.
- Packaging context: Tong et al. (2024), Cryogenics, https://doi.org/10.1016/j.cryogenics.2024.103929. Its proposed package is not treated as an integrated detector validation dataset.
- Conductivity: NIST cryogenic materials fits, linked with coefficients and ranges in `../../data/packaging_materials.json`. These are legacy property references supporting the recent journal case studies.
- Inputs: `../../config/packaging.json`; equations: `../../docs/packaging_model.md`; numerical records: `results.json`; table: `comparison.csv`.
- Reproduce: `python run_packaging.py`; verify: `python -m unittest -v`. No proprietary solver or network access required.

Milestone 5 is complete as a conditional design study. Milestone 6 will consolidate the term paper, repository documentation and a defensible project/resume summary.
