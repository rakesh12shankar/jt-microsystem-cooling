# Priority 5: local power-step response

Conditional local passive transient. Quasi-steady cooler capacity; assumed heat capacities. No physical transient validation or startup prediction.

The selected grid candidate starts at equilibrium with 10 mW device dissipation. At t=0 the device dissipation increases to 15 mW; no heater controller is active. The platform and die store thermal energy while exchanging heat through the stack resistance.

```text
Cd dTd/dt = Pdevice + Qdie,parasitic - (Td-Tc)/R
Cp dTc/dt = Qplatform,parasitic + (Td-Tc)/R - Qmeasured(Tc)
```

Initial mean die: 94.130 K; final mean die: 95.031 K. Final steady hot-spot estimate: 95.324 K. The transient curve is the mean die temperature; spatial hot-spot dynamics are not solved.

| Heat capacity scale | 2% settling time s | Overshoot above final mean K | Energy residual J |
|---:|---:|---:|---:|
| 0.5 | 32.7 | 0 | 3.85e-15 |
| 1 | 65.4 | 0 | 1.34e-14 |
| 2 | 130.75 | 0 | 3.07e-14 |

Nominal local time constants: [0.15865142842851482, 17.181538796148736] s. Tightening solver tolerance from 1e-8 to 1e-10 changed the mean-temperature trace by at most 1.09e-07 K.

## Interpretation and limits

- The passive response for this positive power step is monotone: no overshoot above the new equilibrium is observed. This does not imply zero temperature excursion; the entire equilibrium rise is the excursion from the original setpoint.
- Heat capacities of 0.008 J/K for the die and 0.10 J/K for the platform assembly are assumptions near 100 K. Scaling both changes response time and leaves the steady equilibrium unchanged.
- The measured steady capacity map is assumed to respond instantly. Fluid inventory, phase redistribution, pressure/flow dynamics and the controller may introduce additional modes; the computed time constants are package-model estimates.
- The 15 mW endpoint is a nominal-case demonstration. It exceeds the selected design’s approximately 11.5 mW adverse-case limit; this step is not guaranteed to satisfy 100 K across the assumed uncertainty scenarios.
- This is not a 295 K cooldown simulation. All calculated states remain on the available cold capacity branch.
- The Pei 2024 laser-illumination result involves a different sample, optical absorption and temperature-control protocol. It is not used as validation for this open-loop electrical step.

Run `python run_array_transient.py` after optimization. The CSV stores the nominal trace; JSON includes all heat-capacity scenarios and numerical checks.
