# Real-fluid model: scope and equations

Milestone 3 adds a real-fluid steady-state baseline. It is not a full replication
of Qi's distributed wall model. Existing `model.py` remains the measured-capacity
reference; `realfluid.py` does not read its capacity data.

## Scope

- CoolProp HEOS nitrogen supplies enthalpy, temperature, saturation and entropy.
- Open-cycle gas supply; no compressor/COP or cylinder depletion calculation.
- Prescribed inlet/outlet pressures and finite recuperator pressure drops.
- Prescribed mass flow from the experimental operating point.
- Recuperator heat transfer expressed as a fraction of pinch-limited maximum
  heat transfer, using real-fluid enthalpy profiles on both streams.
- Isenthalpic restriction; phase flash at evaporator pressure.
- Cold-return enthalpy is solved, including a wet two-phase return.
- A reference cold-platform resistance and heat leaks couple the cycle to the
  existing two-node detector package.

This meets the roadmap's simplified thermodynamic baseline scope. Predicting
mass flow, UA or pressure losses from fabricated geometry is an additional
model refinement, not claimed here. The Cao (2019) correlations are relevant
to that refinement; they have NOT been implemented in this effectiveness model.

## Boundaries and state numbering

1. Warm high-pressure inlet: 295 K, 11.1 MPa.
2. Recuperator high-pressure outlet: inlet pressure minus assumed 50 kPa drop.
3. Restriction outlet: 0.240 + 0.045 = 0.285 MPa; h3 = h2.
4. Cold-region outlet/recuperator return: same 0.285 MPa; enthalpy is unknown.
5. Warm low-pressure outlet: 0.240 MPa.

The 45 kPa return drop is Qi's modeled estimate at the reported no-load flow.
It is not a direct pressure measurement and is not recomputed at other flows.
All pressures are treated as absolute; paper absolute/gauge conventions should
be confirmed during final replication. The vapor-pressure benchmark supports
the absolute interpretation for the return pressure.

## Recuperator

Let x run from warm end (0) to cold end (1), m denote mass flow, Qr the modeled
radiation absorbed by the recuperator, and Qx heat transferred between streams.
The assumed profiles are:

```text
ph(x) = ph,in - dp,h*x
pl(x) = pl,out + dp,l*x
hh(x) = h1 - Qx*x/m
hl(x) = h4 + (Qx + Qr)*(1-x)/m
```

Thus the low-pressure stream receives both inter-stream heat and ambient
radiation. This is a simplified allocation: all recuperator ambient pickup is
assigned to the return stream. It is not a local wall energy solution.

Radiation uses a linear assumed wall-temperature profile from cold-return
temperature to ambient, with analytical integration of T^4. This assumed wall
profile is NOT identical to the calculated fluid temperature profiles.
The chosen effective area is the two large faces of the 42 x 9.5 mm recuperator;
edge radiation, detailed MLI view factors and shields are omitted.

Endpoint enthalpy bounds are calculated first. If necessary, the maximum
transfer is reduced until every sampled location satisfies Th >= Tl. Then:

```text
Qx = effectiveness * Qmaximum
```

Effectiveness 0.995 is an assumption. Its definition differs from Qi's Eq. A2,
which compares low-side enthalpy gain with its ambient-temperature limit.
It must not be described as an extracted measured effectiveness.
41/81/161-point checks assess pinch sampling for the baseline only; they are
not a finite-volume grid convergence test or a proof between sample points.

## Cold region and package

```text
Qgross = m*(h4 - h3)
Tplatform = Tfluid,4 + Rfluid-platform*Qgross
Qreference,cold = eps*sigma*Aref*(Tamb^4 - Tplatform^4)
Qreference,axial = Gaxial*(Tamb - Tplatform)
Qnet,external = Qgross - Qreference,cold - Qreference,axial
Qnet,external = sum(additional package loads)
```

Reference losses are included explicitly here because capacity is calculated
from fluid enthalpy, rather than taken from a net experimental curve. Additional
package loads are the same paths as version 0.1. No measured-capacity subtraction
is used. Recuperator radiation is counted in the cycle once, separately from
cold-face radiation and axial conduction.

Reference emissivity 0.15 comes from Qi's fitted insulation value. The reference
platform resistance of 100 K/W and axial conductance of 5 microW/K are assumed,
not fitted or measured properties. In particular, agreement in no-load temperature
depends on that assumed resistance and is not an independent validation result.

The equation solver scans cold-return enthalpy from saturated liquid through
vapor up to 160 K, brackets roots and selects the lowest-enthalpy solution.
A missing root means no equilibrium in that search domain, not universal
infeasibility. Dynamic stability and startup are not established by this selection.

## Restriction diagnostic

Qi's isothermal laminar slit formula is evaluated separately:

```text
m_slit = N * W*H^3/(12*L) * integral(rho(T,p)/mu(T,p), p_low, p_high)
```

N=14, W=140 micrometers, H=0.7 micrometers, L=1000 micrometers.
Properties are integrated separately on either side of saturation pressure
when applicable. This is an isothermal equilibrium estimate; it has no choking,
metastability or slip closure. It uses platform temperature as Qi did and does
not determine the cycle's mass flow. Agreement at one point is not sufficient
to promote it to a predictive hydraulic model.

## Verification and comparison

Tests check saturation temperature, pressure bookkeeping, isenthalpic throttling,
nonnegative valve entropy generation, recuperator and global energy closure,
wet-return handling, pinch constraints, ideal warm-end capacity bound, and a
no-recuperation limiting case. Existing package analytical tests remain in place.

Capacity comparisons use prescribed mass flows approximated from Qi's figures
(4.4 mg/s near 100 K and 7.9 mg/s near 153 K). Those are comparison inputs,
not outputs, and the assumed pressure drops remain fixed. A complete validation
study must use better digitization, measured uncertainties and an independent
dataset; it is milestone 4.

## Sources

- Qi et al. (2023), Sections 2-3, Fig.5, Eq.5 and Appendix A:
  https://doi.org/10.1016/j.applthermaleng.2023.120361
- CoolProp API documentation for P-H and P-Q property flashes:
  https://coolprop.org/coolprop/HighLevelAPI.html
- Cao et al. (2019), future geometry-based correlation refinement:
  https://doi.org/10.1016/j.ijrefrig.2018.10.005
