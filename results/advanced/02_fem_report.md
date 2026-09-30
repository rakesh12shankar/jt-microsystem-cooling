# Priority 2: thermal and mechanical finite-element study

3D tetrahedral stack, constant effective k, full-area bond/contact, isothermal bottom and adiabatic sides. Network supplies bottom temperature and heat budget; mean is identical to 1D stack in this geometry. Local top source is 5 mW Gaussian sigma 0.35 mm plus uniform remainder.

2D plane-stress tri-elements, constant effective E/nu/CTE, perfect bonded interfaces, left pin/right roller, uniform cooldown. No adhesive plasticity, creep, debonding or package restraint. Central die stress excludes outer 1 mm on both ends.

Revised array network: platform 94.992 K; mean die 95.460 K at 10 mW. Nominal mean-temperature device-power limit: 22.37 mW.

| Level | Thermal nodes | Maximum die K | Die range K | Energy residual W |
|---:|---:|---:|---:|---:|
| 2 | 572 | 95.62987 | 0.20840 | -2.08e-17 |
| 4 | 3150 | 95.65126 | 0.22954 | 1.39e-17 |
| 8 | 22099 | 95.65769 | 0.23585 | -4.40e-15 |

| Level | Mechanical nodes | Warpage um | Central die stress MPa | Edge-inclusive peak MPa |
|---:|---:|---:|---:|---:|
| 2 | 150 | 2.2822 | 15.3579 | 25.0671 |
| 4 | 539 | 2.9620 | 14.7871 | 29.1662 |
| 8 | 2037 | 3.2061 | 14.5764 | 30.6650 |
| 16 | 7913 | 3.2734 | 14.5240 | 31.1216 |
| 32 | 31185 | 3.2894 | 14.5135 | 31.2587 |

The highest-mesh change is reported rather than claiming universal mesh independence. Free-edge stress may be singular; use the interior stress and warpage for screening. Neither proves adhesive reliability. The thermal mean agrees with the analytical layered resistance because the bottom is isothermal and the sides are insulated; this is verification, not experimental validation.

## Property sensitivity

| Assumption | Maximum die K | Die range K |
|---|---:|---:|
| nominal | 95.651 | 0.230 |
| contact resistivity x0.5 | 95.493 | 0.220 |
| contact resistivity x2 | 95.960 | 0.238 |
| die k x0.5 | 95.828 | 0.423 |
| die k x2 | 95.555 | 0.120 |

## Interpretation

- The corrected payload and wiring materially reduce the earlier exploratory power budget.
- A finite bond and a localized readout heat source create a die hot spot; optimization must constrain peak temperature rather than the mean alone.
- Cooldown mismatch produces curvature and interior stress even without mechanical acceleration. Linear effective CTE/modulus assumptions dominate the physical interpretation.
- Supports, wires, seals, glass pressure channels and optical window are not meshed here. Supports/wires remain network and beam-screen elements. A full enclosure FEA requires qualified material, joint and mounting details.

Run `python run_array_fem.py`. The source model is `package_fem.py`; geometry and property assumptions are in `config/array_design.json`.
