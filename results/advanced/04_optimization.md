# Priority 4: constrained package optimization

Best within enumerated assumed design grid; not a continuous global optimum or a qualified hardware design.

Evaluated 1134 geometries; 372 pass adverse mechanical/electrical screens; 7 also provide at least 10 mW useful device power at a 100 K peak-temperature limit.

## Search space

- Support length: 1–4 mm in 0.5 mm steps; thickness: 0.10–0.35 mm in 0.05 mm steps; width: 0.3, 0.5, 0.7 mm.
- Wire thermal length: 5, 8, 12 mm; wire diameters/count/current remain fixed by the provisional array requirements.
- Bond thickness: 25, 50, 100 um. Manufacturing suitability and bond reliability are not demonstrated.
- Objective pair: maximize adverse useful device power and minimize cold support envelope. Warm cooler length/enclosure remain fixed.
- Constraints: peak die ≤100 K; adverse deflection ≤10 um; stress ≤50 MPa; signal/power resistance ≤20/2 ohm; four-support geometry fits enclosure.

## Selected grid candidate

- support_length_mm: 3.0
- support_thickness_mm: 0.3500000000000001
- support_width_mm: 0.3
- lead_length_mm: 8.0
- bond_um: 25.0
- envelope_mm: 15.5
- nominal_screens_pass: True
- adverse_screens_pass: True
- nominal_peak_power_mW: 28.526377855408033
- adverse_peak_power_mW: 11.457156640172357
- adverse_deflection_um: 6.61673177842565

## Peak-temperature correction

A fine-mesh FE influence coefficient maps the localized 50% of device heat into peak-minus-mean temperature. Each candidate bond thickness has its own coefficient in nominal and adverse conditions. The full-area, constant-property stack is linear, so this superposition is exact within that FE model. Wire and other die loads are treated as uniformly distributed. Final boundary designs are independently rerun through the FE solver.

| Condition | Device power mW | FE peak K | Mean die K |
|---|---:|---:|---:|
| nominal | 28.526 | 100.000000 | 99.4430 |
| adverse | 11.457 | 100.000000 | 99.7680 |

The selected bond is also rechecked in the mechanical cross-section:

| Level | Warpage um | Central die stress MPa |
|---:|---:|---:|
| 16 | 3.6897 | 16.821 |
| 32 | 3.7077 | 16.803 |

## Adverse scenario

Use the lower measured-capacity reading scenario; support conductivity +20%; wire conductivity +10%; contact resistivity x2; opaque emissivities x2; residual-gas conductance 10 uW/K; out-of-band window transmission 0.03; wire electrical resistivity +20%; support modulus -30%. Other properties remain fixed. This is a prescribed engineering scenario, not a guaranteed worst case or probability statement.

## Limits

The optimum is conditional on laminate stiffness, heat transfer, hypothetical detector power/pinout, bond quality and the chosen hot-spot distribution. Full-area bond contact and fine wire attachment have not been manufactured or tested. Thermoelastic bond stress is reported in the separate FE study; it is not a qualified reliability constraint here because no applicable failure criterion is available. A grid optimum at a bond-thickness bound is a candidate for qualification, not a recommendation to fabricate the thinnest bond.

Run `python run_array_optimization.py`. Complete grid: `design_grid.csv`; selected reproducible inputs and FE checks: `optimization_results.json`.
