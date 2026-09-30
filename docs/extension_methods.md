# Distributed exchanger and bond-defect methods

These extensions address physical uncertainties identified in the original study.
They do not change the published source data or retrospectively fit the reference
capacity curve. Read the generated [extension report](../results/extensions/report.md)
for numerical results and model adequacy findings.

## 1. Distributed exchanger

### Domain and unknowns

`distributed_hx.py` represents the 42 mm Qi exchanger as axial cells, with
high-pressure and low-pressure gas temperatures at cell faces and a shared glass
wall and effective insulation temperature in each cell. Coordinate x runs from
warm to cold; the return gas flows in the opposite direction. Nitrogen enthalpy
and heat capacity are evaluated with CoolProp. Flow and linear pressure profiles
are prescribed, not calculated from a restriction/pressure-drop correlation.

The model is restricted to platform temperatures at least110 K and requires
single-phase vapor everywhere on the low-pressure return. The JT valve itself
may produce a wet mixture; the evaporator is represented only by an enthalpy
balance before vapor returns to the exchanger. Two-phase flow inside the
exchanger is unsupported. A rejected nonlinear solve does not establish absence
of a physical equilibrium; no rejected point is silently extrapolated or bridged.

### Conservative equations

For cell i, define positive qh as high-pressure gas to wall, ql as wall to
return gas, qi as insulation to wall, and qr as ambient radiation to insulation:

```text
m [hh(i) − hh(i+1)] = qh(i)
m [hl(i) − hl(i+1)] = ql(i)
qh − ql + qi + qax,in − qax,out = 0
qr − qi = 0
qi = (Gi/N) [Tinsulation − Twall]
qr = epsilon sigma (A/N) [Tambient^4 − Tinsulation^4]
```

Each gas side uses exponential heat exchange with an isothermal cell wall:
`q = m cp (Tin − Twall) [1 − exp(−Gcell/(m cp))]`, with the sign reversed for
wall-to-return exchange. Local cp is evaluated at mean gas temperature and
pressure; exact real-fluid enthalpy differences remain in the energy balances.
This local approximation avoids the temperature oscillations possible with
midpoint exchange at high cell NTU, but it still needs mesh refinement.

Wall axial conduction uses adjacent cell temperatures and half-cell distances
at the ends. The wall is anchored to ambient at its warm end and to the platform
at its cold end. Insulation has no axial conduction in this reduced model;
it exchanges radiation with ambient and heat with the wall locally. Its effective
emissivity does not resolve three individual insulation layers or spectral optics.

The cold-end and platform balances are:

```text
Qgross = m [hreturn,cold − hhigh,cold]      (isenthalpic valve)
Tplatform − Treturn,cold = Rfluid-platform Qgross
Qnet = Qgross − Qcold-radiation − Qwall-to-platform
```

Warm-anchor heat is included when checking the whole-device energy balance.
Wall heat reaching the platform is explicitly subtracted; it must not also be
counted as a separate lumped axial leak. The model can circulate substantial heat
internally between cold wall and evaporator. A plausible net result therefore
does not establish a plausible internal heat budget.

### Sources and assumptions

Qi (2023) supplies geometry, boundary conditions and condition-specific measured
flow. The previous project assumed high-side drop50 kPa; the 45 kPa return drop
is the paper's modeled value at one condition, here held fixed as a simplification.
The two-face radiation area is2 ×42 ×9.5 mm². Effective emissivity0.15 comes from
Qi's fitted insulation value, so the model is not wholly independent of that source.

Glass axial conductance uses `k Aglass/L`, with assumed constant k=1 W/(m K),
outer section9.5 ×1.3 mm² and subtraction of two8.13 ×0.040 mm² channels. This
is an idealized continuous cross-section, not a measured effective conductance.
The warm/cold wall anchoring, gas-to-wall conductances and insulation contact
conductance are assumptions. The study screens each gas-side total conductance
at 0.3,1 and 3 W/K and insulation contact at 0.0001,0.003 and 0.1 W/K. These are
exploratory constitutive scenarios, not measured distributions or fitted coefficients.

The main sweep assumes ideal fluid/platform contact (R=0). A separate0/50/100 K/W
screen exposes the effect of finite contact and identifies rejected cases.
Neither choosing ideal contact nor excluding colder points demonstrates adequacy
of the model at the original100 K requirement.

### Comparison and propagation

All five110–153 K Qi points are unfitted diagnostic comparisons; measured flow
is used at each point. No new training/holdout claim is made. The earlier fitted
model's split remains documented separately. A finite set of constitutive
scenarios is not a statistical uncertainty interval.

Only to illustrate sensitivity propagation, predicted curves are interpolated
within110–153 K and coupled to the selected package at a **130 K mean-die target**.
This is not the original100 K peak target, not a new detector operating
specification, and not a qualified rating. These calculations must not replace
the original measured-capacity package results.

## 2. Bond defects

`bond_defects.py` retains the original adapter/bond/die mesh and introduces
through-thickness regions of reduced effective bond conductivity. Requested
areas are10%,25% and 50%, with central rectangular, central circular, edge-strip
and corner rectangular footprints. Rectangles preserve the 6:5 die aspect ratio;
internal keys `center_square` and `corner_square` denote square footprints only
in normalized die coordinates. Shapes are snapped to mesh columns, and actual
meshed area is reported. Centered rectangular masks use symmetric even cell counts.

The main defect conductivity is10^-4 times intact effective bond conductivity.
Additional0.001,0.01 and 0.1 ratios test severity. These are thermal sensitivity
parameters, not measured vacuum-gap conductivities. The model does not predict
gap radiation, gas conduction, crack growth, detachment, or stress redistribution.
Original mechanical results cannot qualify the defective bond's strength.

### Two load bases and network coupling

For each defect geometry, the stiffness matrix is factored once and solved for
two independent1 W loads: a uniform load and the original centered Gaussian
hot spot. The complete nodal rise is then

```text
rise_vector = basis_uniform (Qdie − 0.5 Pdevice)
            + basis_hotspot (0.5 Pdevice).
```

The area-weighted mean of this vector is coupled back into the nonlinear package
network. This replaces the intact lumped interface resistance. The maximum is
taken after combining the two spatial fields; adding two separate maxima would
be wrong when their locations differ. The allowable device power is solved at
a 100 K peak using the original measured reference-capacity map. Uniform parasitic
loads can now create nonuniform temperatures because the interface is spatially
nonuniform.

The original selected geometry is screened under nominal and prescribed adverse
assumptions, rather than rerunning the entire geometry optimization. The same
electrical/support requirements remain fixed. The study therefore assesses
defect sensitivity of a candidate, not a new defect-tolerant optimum.

### Verification

The intact case must recover the existing thermal FE solver and its allowable
power. Uniformly degrading the whole bond must recover the analytical layered
resistance. Each1 W load basis must conserve energy. Mesh refinement uses an
exactly 25% centered rectangular footprint on levels 4,8 and 12 so that changing
area does not masquerade as convergence. The asymmetric/circular cases still
have discretized outlines and should not be used to claim precise defect-area
acceptance thresholds.

## Reproduce

After generating `results/advanced/optimization_results.json`:

```sh
python run_distributed_hx.py
python run_bond_defects.py
python build_extension_report.py
python -m unittest -v
python build_advanced_overview.py
```

Results, plots and short numerical records are under `results/extensions/`.
Source files and the original model configuration remain available for comparison.
