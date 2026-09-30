# Reproduce the final reference-array study

Run commands from the repository root using Python 3.10 or newer. Create a local
virtual environment if desired, then install dependencies:

```sh
python -m pip install -r requirements.txt
python -m unittest -v
```

The recorded environment is Python 3.12.14, numpy 2.3.5, scipy 1.18.1,
matplotlib 3.11.2 and CoolProp 8.0.0. `requirements.txt` permits ranges for the
numerical libraries; exact recorded versions and input hashes are in
`results/advanced/provenance.json`. Small platform/version differences are possible.

## Final study: generation order

```sh
python run_array_fem.py
python run_calibration_audit.py
python run_external_validation.py
python run_supplement_audit.py
python run_array_optimization.py
python run_array_transient.py
python run_distributed_hx.py
python run_bond_defects.py
python build_extension_report.py
python build_advanced_overview.py
```

The optimization runs multiple FE calculations and may take time. The transient
reads the selected optimization result; the overview requires all earlier
results. Scripts overwrite their corresponding generated results. No PDF or
network access is needed. Source inputs are already transcribed in local files
or explicitly documented calculation scripts.

## Map from paper claims to evidence

| Claim | Inputs / method | Saved evidence |
|---|---|---|
| Reference geometry | `config/array_design.json` | `docs/01_array_specification.md` |
| Baseline temperatures and mesh study | `run_array_fem.py`, `package_fem.py` | `results/advanced/fem_results.json` |
| Calibration/holdout error | `data/qi2023_validation.json`, `run_calibration_audit.py` | `results/advanced/calibration_audit.json` |
| Seven feasible designs, selected rating | `array_optimization.py`, `run_array_optimization.py` | `results/advanced/design_grid.csv`, `optimization_results.json` |
| Local transient and capacitance sensitivity | `array_transient.py`, `run_array_transient.py` | `results/advanced/transient_results.json`, `power_step.csv` |
| Gas-runtime comparison | `run_external_validation.py` | `results/advanced/external_comparison.json` |
| Supplement reproduction | `run_supplement_audit.py` | `results/advanced/supplement_audit.json` |
| Source integrity | `data/pei_source_files.json` | SHA256 of supplied source files |

Paths in the last column without a directory prefix share the preceding directory.

## Earlier exploratory work

`run_analysis.py`, `run_realfluid.py`, `run_validation.py` and `run_packaging.py`
reproduce the earlier network, real-fluid baseline and placeholder-package studies.
Those outputs are preserved for traceability. Their smaller placeholder detector
does not represent the final array and their power limits must not be mixed into
the final paper's results. The failed baseline capacity comparison is retained,
not hidden by calibration.

## Verification versus validation

The automated suite checks thermal/energy balances, analytical limits, optical
bounds, FE consistency, target recovery and transient behavior. Supplement
reproduction also checks the analytic radiation integral against numerical
quadrature. These establish implementation consistency, not accuracy of assumed
properties or experimental validation of the new detector package.

## Sharing contents

Include source code, configuration, short derived data, original figures, reports,
requirements and `.gitignore`. Exclude `tmp/`, `papers/`, `.venv/`, `__pycache__/`
and publisher PDFs/full-text extractions. This project currently has no chosen
open-source license; select a license before advertising reuse rights. No remote
repository has been created or published as part of this milestone.

## Physical extensions

`distributed_hx.py` and `run_distributed_hx.py` generate the vapor-return exchanger
scenarios and mesh study. `bond_defects.py` and `run_bond_defects.py` generate
spatial defect results using the selected package. `build_extension_report.py`
assembles the results and an independent entropy/energy verification record.
All outputs are in `results/extensions/`; see `docs/extension_methods.md`.
The new eight tests in `test_extensions.py` bring the full suite to 43 tests.
The fine exchanger and FE studies take several minutes.
