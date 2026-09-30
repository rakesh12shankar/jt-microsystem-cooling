# Historical project README

Preserved before final-paper consolidation. Earlier milestone/next-step statements
are historical; use the root README and milestone status for the current project.

# JT cooling for microsystems packaging

A term-project research prototype studying how package heat leaks and thermal
interfaces affect a cryogenic detector. Version 0.2 adds a real-fluid nitrogen
JT cycle coupled to the package, alongside the version 0.1 measured-performance map.

**Status:** expanded reference-array design, finite-element analysis, calibration
audit, constrained optimization and local transients implemented; 35 verification
tests pass. Independent quantitative validation remains open. The original
real-fluid baseline fails the selected capacity benchmark; package studies use
measured cooler capacity. No publication novelty is claimed.

## Start here: expanded array study

Read [the five-study overview](../results/advanced/overview.md) and
[the methods and limitations](../docs/advanced_methods.md).

The 320 x 256, 15 um-pitch array has a 4.80 x 3.84 mm active area. It requires
a larger die and supported-mass allowance than the original exploratory model.
The revised 6 x 5 mm die, grouped power/signal wiring and 450 mg payload
supersede the earlier 3 x 3 mm / 5 mg assumptions for this reference application.

The selected candidate among 1,134 grid designs supplies approximately 28.5 mW
nominally and 11.5 mW under the prescribed adverse scenario at a 100 K peak-die
limit. Only seven designs meet the 10 mW requirement in that scenario. These
estimates do not qualify a manufactured detector package.

```sh
python run_array_fem.py
python run_calibration_audit.py
python run_external_validation.py
python run_supplement_audit.py
python run_array_optimization.py
python run_array_transient.py
python -m unittest -v
```

The transient script requires the optimization result. All generated files are
in `results/advanced/`; `config/array_design.json` records sourced versus assumed
inputs. Both supplied Pei full texts are reviewed in the
[external evidence report](../results/advanced/06_external_evidence.md). An unfitted
gas-runtime comparison is complete; independent thermal validation remains open.
The supplied [2026 supplement audit](../results/advanced/07_supplement_audit.md)
reproduces the heat loads and identifies residual-based exchanger effectiveness
and an apparent startup-gas arithmetic inconsistency.

## Reproduce

Python 3.10 or newer:

```sh
python -m pip install -r requirements.txt
python -m unittest -v
python run_analysis.py
python run_realfluid.py
python run_validation.py
python run_packaging.py
```

Run from this directory. Empirical results are written to `results/`; the new
cycle states, figures, comparisons and report are in `results/realfluid/`.
The eight-point benchmark, input uncertainty screen and discrepancy diagnosis
are in `results/validation/` (the validation script can take several minutes).
Geometry-based package comparisons, uncertainty scenarios and constraint screens
are in `results/packaging/`.
Source PDFs are not required to run the model
and are not redistributed. The scripts make no network requests.

## Earlier exploratory packaging tradeoffs (milestone 5)

[The package study](../results/packaging/summary.md) compares four support/wire/interface
architectures using NIST temperature-dependent conductivity, explicit dimensions,
added radiation, gray optical loading and residual-gas conduction. Beam deflection
and lead resistance are preliminary screens with stated assumptions.

Two G10 candidates pass those screens: nominal device-power limits are about
45–48 mW at 100 K, falling to 29–34 mW in the combined adverse scenario. The
steel-support case cannot meet 100 K even at zero device power; the longest-wire
case fails the assumed resistance limit despite its favorable thermal result.
These are conditional estimates, not experimentally validated package ratings.
These earlier estimates use a smaller placeholder die and payload; they do not
describe the larger literature-format array in the expanded study above.
Read [the model and limitations](../docs/packaging_model.md) before using them.

## Real-fluid baseline (version 0.2)

`realfluid.py` uses CoolProp nitrogen properties, a simplified enthalpy-based
recuperator, finite prescribed pressure drops, isenthalpic throttling and phase
tracking. The cold-return enthalpy is solved together with the package balance;
wet return is permitted. Reference cooler heat leaks are explicit in this model.
The cycle does not use the measured cooling-capacity map. Mass flow and pressure
drops are prescribed inputs; a separate slit-flow diagnostic does not close the
hydraulic model. Recuperator effectiveness and thermal resistances are assumptions.

Read [the equations and limitations](../docs/realfluid_model.md) and
[the generated result report](../results/realfluid/summary.md). Current capacity
errors are material; the model is ready for validation work, not design qualification.

## Validation assessment (milestone 4)

Read [the validation report](../results/validation/summary.md) and
[the verification gates and scope](../docs/validation.md). Eight paired capacity
and flow points from Qi's Figure 5 are compared without parameter fitting.
Sixteen input corners per point screen measurement and digitization allowances.
These are deterministic ranges, not statistical confidence intervals.

The whole-cooler loss budget and assumption sweeps identify radiation modeling
as a major discrepancy to investigate. A reconstruction using the authors'
modeled radiation and outlet temperature is an accounting diagnostic only.
The baseline configuration and earlier results remain unchanged.

## Measured-performance reference (version 0.1)

The reference is Qi et al. (2023): nitrogen, 11.1 MPa high pressure, 0.24 MPa
outlet pressure, 295 K environment, insulated cooler in vacuum below 1e-4 Pa.
The capacity map is approximate manual readings of experimental markers in
Figure 5(a), with the no-load and peak endpoints taken from the article text.
Only the increasing 88.5-153 K branch is used; linear interpolation prevents
overshoot. No extrapolation, pressure sweep, or ambient-temperature sweep is allowed.

The reference temperature is the measured silicon-chip temperature, NOT the
fluid temperature. The proposed detector is an additional die connected to this
reference platform through an additional thermal resistance. This is a
conceptual integration architecture, not a reproduction of Tong's metal MMR.

```text
295 K enclosure
  |-- extra leads + radiation + optical power --> detector Td (device power P)
  |                                                    |
  |                                           extra interface R
  |                                                    |
  |-- extra supports + radiation + residual gas --> reference platform Tc
                                                       |
                                            measured net capacity Q(Tc)
```

Let Hd(Td) be device dissipation plus all extra loads entering the detector,
and Hc(Tc) be all extra loads entering the platform. The steady-state equations are:

```text
Td - Tc = R * Hd(Td)
Q_reference(Tc) = Hd(Td) + Hc(Tc)
Q_conduction = G * (Tambient - Tnode)
Q_radiation = sigma * A * emissivity * (Tambient^4 - Tnode^4)
```

The reference measured cooling power is the averaged steady-state heater power.
Its existing radiation, conduction, gas connections, bonding and instrumentation
are already embedded in that measurement. They must NOT be subtracted again.
Extra radiating areas in this model represent additional effective exposed
hardware; replacing reference insulation would require a different model.

All temperatures are kelvin; powers watts; conductances W/K; resistance K/W.
Inputs and assumptions are in `config/baseline.json`. The default 3 x 3 mm
detector is an assumption, separate from Qi's 9.5 x 9.5 mm reference silicon chip.
Support and lead conductances are effective averaged values, not validated
material/geometry combinations. Mechanical stiffness and electrical impedance
constraints have not yet been applied. Surface radiation uses a small-body,
large-enclosure approximation; optical-window spectral transmission is not modeled.

## Verification and uncertainty

- An analytical linear-capacity, two-node case tests both temperatures independently.
- Energy and interface balances are checked to numerical tolerance.
- Zero-load, overload, emissivity bounds and out-of-domain conditions are tested.
- The digitized curve is a calibration input, not a validation dataset.
- Manual graph-reading allowances are recorded in the data file. Values should
  be replaced with higher-resolution digitization or author data before reporting
  precise performance. Report rounded temperatures and powers in the term paper.
- A +/-10% capacity scaling study illustrates sensitivity, not statistical confidence.
- The reference paper itself reports difficulty modeling liquid extending into
  the return channel in the low-temperature regime. Using measurements avoids
  relying on that simplified fluid model here, but does not remove uncertainty.
- Only steady-state equilibria are computed. No transient stability, startup,
  finite cylinder duration, closed-cycle efficiency, or COP is predicted.

## Files

- `model.py`: thermal network, capacity interpolation and target-load calculation.
- `run_analysis.py`: baseline, design comparisons and figures.
- `test_model.py`: physical and numerical checks.
- `data/qi2023_capacity.json`: approximate capacity data with provenance.
- `docs/evidence.md`: extracted model inputs and packaging evidence.
- `results/summary.md`: generated findings.
- `realfluid.py`: nitrogen cycle, recuperator and package coupling.
- `config/realfluid.json`: cycle inputs with source/assumption notes.
- `run_realfluid.py`: real-fluid results, benchmark comparisons and sampling checks.
- `test_realfluid.py`: thermodynamic and numerical verification.
- `results/realfluid/summary.md`: milestone 3 report.
- `data/qi2023_validation.json`: higher-resolution paired readings and allowances.
- `run_validation.py`: conditional benchmark, input screen and loss diagnosis.
- `test_validation.py`: ideal-limit, loss-budget and whole-cooler entropy checks.
- `results/validation/summary.md`: milestone 4 assessment.
- `packaging_model.py`: conductivity integrals, geometry and constraint screens.
- `config/packaging.json`: four candidate architectures and stated assumptions.
- `data/packaging_materials.json`: NIST property coefficients, ranges and sources.
- `run_packaging.py`: tradeoff study, plots and CSV output.
- `test_packaging.py`: integration, target-boundary and geometry checks.
- `results/packaging/summary.md`: milestone 5 findings.
- `config/array_design.json`: revised reference-array specification.
- `array_model.py`: grouped leads, band-integrated optical load and stack resistance.
- `package_fem.py`: 3D thermal and 2D thermoelastic finite-element solvers.
- `array_optimization.py`: peak-temperature power limit and adverse assumptions.
- `array_transient.py`: local passive two-node dynamics.
- `test_array_studies.py`: analytical FE limits, optical bounds, energy and transient checks.
- `results/advanced/overview.md`: five-study status, results and remaining evidence gaps.

## Next research stage

1. Milestone 6: consolidate the term paper, figures, reproducibility instructions
   and project/resume summary; publishing has not been performed.
2. Refine the real-fluid baseline's radiation closure before claiming predictive
   validation. Geometry-based heat transfer
   and hydraulic closure using Cao et al. (2019) remain an optional refinement
   beyond the implemented effectiveness model; wet-flow applicability needs care.
3. Replace screening mechanical/electrical assumptions with detector and material
   specifications; check cryogenic joints and cooldown thermal strain.
4. Refine spectral optical-window and pressure-dependent gas loads, then obtain
   an independent integrated-package benchmark.

## References

- Qi et al. (2023), *Applied Thermal Engineering* 227, 120361.
  https://doi.org/10.1016/j.applthermaleng.2023.120361
- Tong et al. (2024), *Cryogenics* 143, 103929.
  https://doi.org/10.1016/j.cryogenics.2024.103929
- Cao et al. (2019), *International Journal of Refrigeration* 98, 334-342.
  https://doi.org/10.1016/j.ijrefrig.2018.10.005

The reference list for the final paper will retain the recent-paper emphasis
established in the literature review. The older correlation paper is a specific
method dependency, not the basis for a claim about the current state of the field.

## Sharing

This folder is prepared for local review; it has not been published to GitHub.
`tmp/` contains private working extractions and is excluded by `.gitignore`.
Publish original code, provenance, short derived data and generated plots;
do not upload publisher PDFs or extracted full article text.
