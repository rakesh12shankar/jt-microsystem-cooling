# Priority 1: physically specified reference package

## Reference application

Use the 320 x 256, 15 um-pitch infrared-array format in Tong et al. (2024),
Cryogenics 143, 103929, Table 3 and detector integration discussion.
Its active dimensions are 4.80 x 3.84 mm. A 6 x 5 x 0.30 mm hybrid die envelope
is chosen to include an assumed border/readout allowance. This is a thermal
surrogate for that format, not a commercial detector with qualified performance.
The electrical pinout, substrate stack and 100 K imaging performance remain
unspecified by the available source. A 100 K temperature target and 10 mW
dissipation are project requirements, not attributed to Tong.

The reference cold platform remains Qi et al.'s 9.5 x 9.5 mm silicon chip on
a 60 mm-long glass nitrogen cooler. Tong's 26 mm package and performance of
its metal cooler are not transferred to Qi's cooler.

## Candidate construction

| Item | Specification | Evidence status |
|---|---|---|
| Array | 320 x 256, pitch 15 um | Tong 2024 |
| Active footprint | 4.80 x 3.84 mm | Derived |
| Optical cone | f/1.2 | Tong 2024 |
| Die envelope | 6 x 5 x 0.30 mm | Assumed |
| Added silicon adapter | 6 x 5 x 0.50 mm | Assumed |
| Adhesive bond | 50 um, full nominal area | Assumed; product not qualified |
| Reference platform | 9.5 x 9.5 x 0.50 mm | Qi 2023 |
| Supports | Four G10 warp-aligned tabs, 2 x 0.5 x 0.2 mm | Assumed geometry |
| Signal wiring | 12 wires, 25 um diameter, 8 mm thermal length | Assumed pin/current budget |
| Power/return wiring | Four wires, 75 um diameter, 8 mm thermal length | Assumed pin/current budget |
| Cold shield | Effective additional exposed area 200 mm2, epsilon 0.05 | Assumed thermal envelope |
| Enclosure | 70 x 25 x 15 mm internal allocation | Assumed clearance envelope |

The enclosure contains a 60 mm cooler along its long axis, warm pressure-rated
feedthroughs at one end, a window above the cold array and a pump/getter port.
Window thickness, seals, feedthrough pressure rating and vacuum hold time require
separate design. The 13.5 mm support envelope fits inside the 25 mm enclosure
width. The stack fits on the 9.5 mm reference platform. An f/1.2 cone requires
a widening optical opening: at a 1 mm standoff, a first-order clear rectangle
must be at least about 5.64 x 4.68 mm (active extent plus 2*z/(2*f-number));
field angle and actual pupil location are not included. The figure is a concept
layout, not fabrication CAD.

## Corrections to the previous exploratory study

1. A 3 x 3 mm die cannot contain this active area; it is replaced.
2. The 5 mg payload excluded much of the supported assembly. The new 450 mg
   mechanical allowance includes roughly 105 mg reference silicon, 262 mg cold
   glass, 35 mg adapter, 21 mg die-equivalent material, and an allowance for bond,
   shield and wiring. Existing cooler stiffness/load sharing is neglected, so
   added supports conservatively carry the whole allowance. These density-based
   estimates are approximate, not measured assembly masses.
3. Separate signal and power wires replace a uniform eight-wire assumption.
4. Optical loading integrates a specified 3–5 um scenario and finite optical
   cone; it does not expose the entire active area to a full warm hemisphere.

## Property and requirement ledger

`config/array_design.json` is the canonical machine-readable specification.
NIST conductivity fits for G10 and 304 steel are retained. All die/adapter
conductivities, elastic properties, CTE, contact resistance, electrical
resistivity and heat capacities are explicit screening assumptions. The die is
a homogenized hybrid; it is not modeled as pure silicon. Heat capacities are
local effective values near 100 K and cannot support a room-temperature cooldown
prediction. The adhesive is represented by bulk thermal resistance plus an
additional areal contact resistance. No named commercial adhesive is claimed.

The thermal finite-element model covers the added adapter/bond/die stack; its
bottom is the isothermal reference platform. Supports and wiring are separate
temperature-dependent paths in the network. The mechanical finite-element model
is a plane-stress bonded cross-section for cooldown mismatch. The support screen
remains a cantilever model. This combination is not a full three-dimensional
thermoelastic model of the enclosure and pressurized cooler.

## References

- Qi et al. (2023): https://doi.org/10.1016/j.applthermaleng.2023.120361.
- Tong et al. (2024): https://doi.org/10.1016/j.cryogenics.2024.103929.

Priority 1 is complete as a literature-based reference design. Procurement,
electrical interface qualification and detector performance requirements remain
open engineering inputs rather than invented manufacturer specifications.
