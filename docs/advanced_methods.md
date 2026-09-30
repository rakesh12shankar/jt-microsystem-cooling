# Methods and limits of the five extension studies

## 1. Package definition

See `01_array_specification.md`. The literature provides array format, pitch,
f-number and cooler geometry. The remaining specifications are explicit design
assumptions. A physically consistent surrogate can support a term-paper study;
it is not equivalent to a fully specified commercial detector assembly.

Optical power uses Planck hemispherical exitance integrated over a 3–5 um
scenario. The acceptance cone has sin(theta)^2 = 1/(1+4F^2), assuming a circular
pupil and tan(theta)=1/(2F). The active rectangle receives that angular fraction.
Out-of-band transmission is integrated over the remaining blackbody power.
Transmission and absorptance are gray within each band and are not measured
coating spectra. The warm window is not modeled as an independent thermal node.

## 2. Finite elements

`package_fem.py` implements scalar linear tetrahedra for steady conduction:

```
Ke = integral(grad(N)^T k grad(N)) dV
K T = f
```

The adapter, effective bond and homogenized detector have conforming interfaces.
Bond k_eff = t_bond / (t_bond/k_bulk + r_contact). The reference platform is a
Dirichlet bottom boundary; lateral boundaries are insulated. Top-face loading
combines uniform parasitics and 50% localized device heat in a Gaussian with
sigma=0.35 mm. Its discrete integral is normalized to the specified power on
each mesh. This is a heat-source scenario, not a measured readout power map.

The 2D mechanical cross-section uses constant-strain plane-stress triangles:

```
Ke = integral(B^T D B) dV
fthermal = integral(B^T D epsilon_thermal) dV
sigma = D (B u - epsilon_thermal)
epsilon_thermal = [alpha*dT, alpha*dT, 0]
```

The left-bottom pin and right-bottom vertical roller remove rigid motion while
allowing longitudinal contraction. They are analysis boundary conditions, not a
complete representation of the cooler mount. The cross-section is bonded
perfectly and uses constant effective material properties. The reported central
stress excludes the outer 1 mm at each end to reduce free-edge singularity
effects. No bond strength, fatigue or debonding criterion is available.

Analytical checks: uniform thermal flux recovers layered resistance exactly;
matched thermal expansion in all layers gives free contraction without stress;
zero cooldown gives zero thermal displacement. Mesh studies report both field
metrics and conservation residuals. These are numerical verification checks.

## 3. Calibration and evidence

A one-parameter empirical radiation-area multiplier is fitted only to Qi
measurements at 100, 120 and 140 K. Five other temperatures are held out. The
95 K failure highlights poor transfer into the wet-return transition. Neither
the fitted multiplier nor the held-out points establishes independent validation:
all geometry, fitted insulation emissivity and measured flow come from the same
reference experiment. Both Pei main papers have now been read. See the
[full-text source ledger](benchmark_candidates.md) and external evidence report.
Gas inventory/runtime can be compared under an assumed room temperature; the supplied
supplement allows reproduction of published heat-load estimates. Its exhaust loss
is inferred from measured net power, so net-capacity recovery would be circular.
See results/advanced/07_supplement_audit.md for calculations and limitations.

The independent legacy Derking result is used only for a heat-budget consistency
check. Matching an arithmetic identity is not predictive validation. No test
data from other coolers are spliced into Qi's capacity curve.

## 4. Constrained grid search

Each geometry is screened at nominal and adverse stiffness/resistivity. Only
adverse-screen-passing designs receive a thermal objective. Thermal power is
constrained using a finite-element peak-minus-mean influence coefficient:

```
Tpeak = Tmean + beta * (0.5 Pdevice)
```

This relation follows linear superposition for the constant-property, full-area
stack. beta depends on the bond thickness and contact condition. It does not
apply to partial bonding, temperature-dependent stack properties, moving hot
spots or localized wire attachment. The selected boundaries are rerun with the
full thermal FE solution. Geometric objectives refer to the cold support envelope;
the 60 mm cooler and enclosing volume are not optimized.

An exhaustive discrete search has a best grid candidate, not a global continuous
optimum. Thin-bond and thick-support boundary choices need manufacturing and
reliability review before expanding or narrowing the search. The prescribed
adverse case is a stress test of assumptions, not a statistically certified bound.

## 5. Local transient

Two thermal storage nodes are coupled to the measured steady capacity map.
The ODE is integrated with the implicit Radau method. An additional energy state
integrates the net external heat input; comparison with Cd*dTd + Cp*dTc checks
the global transient energy balance. The no-step solution must stay at the
initial equilibrium. Local Jacobian eigenvalues provide an independent time-scale
check; tighter integration tolerances check numerical sensitivity.

Thermal capacitances are constant local assumptions near 100 K. No valve,
recuperator, pressure, mass-flow or liquid-inventory dynamics are included. The
curve predicts a passive package response under a quasi-steady cooler assumption,
not the measured response of an actual JT assembly. Dynamic spatial hot spots
and feedback control are also outside its scope. Startup from 295 K cannot be
inferred from a cold-branch capacity curve.

## Reproduction order

```sh
python run_array_fem.py
python run_calibration_audit.py
python run_external_validation.py
python run_supplement_audit.py
python run_array_optimization.py
python run_array_transient.py
python -m unittest -v
```

All scripts read local numerical source records and make no network requests.
The installed numpy/scipy/matplotlib/CoolProp versions are recorded in the
advanced provenance file. Source PDFs and extracted full text remain outside
the shareable files. No GitHub publication has been performed.
