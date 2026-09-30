# Verification and validation protocol — milestone 4

## Scope and decision

Verification asks whether the equations and numerical implementation behave
consistently. Validation asks whether those equations reproduce observations
for the intended use. An energy balance alone cannot validate heat-transfer
closures or a packaging design.

This milestone completes a documented **validation assessment**. The
simplified cycle fails the selected capacity benchmark. Predictive validation
and validation of the additional detector package remain open. This is a useful
research result, not grounds for tuning parameters without independent evidence.

## Gates

| Gate | Evidence | Outcome / limit |
|---|---|---|
| Unit and boundary consistency | Kelvin, pascal, W, kg/s; outlet pressure plus low-side drop gives evaporator pressure | Pass for implemented cases |
| Numerical energy closure | Separate HX, cycle and package residuals; analytical two-node solution; loss decomposition | Pass within test tolerances |
| Thermodynamic admissibility | Isenthalpic valve, nonnegative valve and whole-cooler entropy production, sampled positive pinch | Pass at tested states; no local wall solution |
| Ideal limit | Lossless, perfect-recuperation warm-end capacity equals analytical real-fluid enthalpy difference | Pass for warm-end-limited test |
| Sampling | 41/81/161 pinch nodes in milestone 3 | No baseline change; endpoint-controlled result does not prove distributed mesh convergence |
| Published capacity | Eight Qi experimental points, with measured flow prescribed | Fail; see generated comparison |
| Independent cooler prediction | Restriction flow and temperature-dependent drops solved from geometry | Not implemented |
| Integrated package validation | Additional detector, supports, leads and interface compared to separate measurements | Not available |

## Benchmark extraction and uncertainty

`data/qi2023_validation.json` stores manual pixel coordinates, calibrated axes,
rounded readings and provenance. It is a separate validation dataset; the
original empirical interpolation map is preserved. Only clearly identifiable
experimental points and the text-reported peak are selected. The enlarged
error-bar example is excluded. Flow at the peak is approximate because the
markers overlap. Raster coordinates and short derived numerical records can be
shared; the publisher's figure and full text are excluded from the repository.

The deterministic input screen evaluates all 16 combinations of signs for:

- Chip temperature: ±0.8 K (±0.6 K reading plus ±0.2 K instrument).
- Flow: ±0.24 mg/s (±0.04 reading plus ±0.2 instrument); ±0.28 at the peak,
  allowing another ±0.04 mg/s for interpolation.
- High pressure: ±60.5 kPa; outlet pressure: ±15.5 kPa (Table 1).

The measured power comparison uses ±1.12 mW (reading plus instrument). These
are additive screening allowances, not standard deviations; no probability or
confidence level is assigned. Corner extrema are sampled bounds, not a proof of
global extrema. Input correlations, ambient uncertainty, property uncertainty
and model-form error are not quantified. Invalid corners are explicitly logged.
No tolerance was fitted to make the model pass.

The experiment also supplied geometry, insulation emissivity and flow to the
baseline. Therefore this is a conditional benchmark against the same reference
experiment, not independent system validation. The authors themselves fitted
the insulation emissivity. Agreement with their calculated radiation cannot
provide independent validation.

## What the discrepancy identifies

The whole-cooler balance provides a useful decomposition:

```
Qnet = mdot*[h(Pout, Tamb)-h(Pin, Tamb)]
       - mdot*[h(Pout, Tamb)-h(Pout, Tout)]
       - Qrad,HX - Qrad,cold - Qaxial
```

The first term is a warm-end thermodynamic upper bound for this specified
flow and pressure pair. The second is the finite warm-outlet temperature
deficit. These terms prevent an apparent capacity error from being incorrectly
assigned entirely to the expansion valve.

Figure 8(b) of Qi gives modeled total radiation near 26 mW at 100 K and 24 mW
at 153 K (approximate ±2 mW readings), appreciably below the baseline's
two-face, linear-wall estimate. Figure A2 gives a modeled outlet near 294.9 K.
Substitution of these author outputs into Eq. 5 is a diagnostic only. The
underlying area convention, insulation exposure, distributed wall temperature
and fitted emissivity must be resolved before implementing a physical correction.
Halving radiation areas in a sensitivity run does not establish a valid geometry.

No parameter calibration, optimization or post hoc correction is applied.
Sensitivity scenarios are reported separately from measurement uncertainty.

## Next milestone: package tradeoffs

Proceed with the measured net-capacity map for conditional package design
comparisons. Use actual support/wire dimensions and temperature-dependent
conductivity where sourced; separate optical, radiation and residual-gas heat
loads. Evaluate maximum useful device power at a temperature requirement,
interface temperature rise and sensitivity to uncertain package inputs.
Retain original reference losses inside the empirical map to avoid double counting.
Label all package results as model estimates until an integrated benchmark exists.

Sources: Qi et al. (2023), doi:10.1016/j.applthermaleng.2023.120361;
Tong et al. (2024), doi:10.1016/j.cryogenics.2024.103929.
