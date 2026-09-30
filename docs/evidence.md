# Evidence ledger: inputs and interpretation

Extracted from the two user-supplied full journal PDFs. Article page numbers
below are printed page numbers. Published results and project assumptions must
remain separate. Publisher source files are not redistributed in this repository; use the DOI links to obtain them.

## Qi et al. (2023), DOI 10.1016/j.applthermaleng.2023.120361

| Input / finding | Value | Location / qualification |
|---|---|---|
| Cooler | 60 x 9.5 x 1.3 mm, three borosilicate layers | Section 2.1, p.3 |
| Reference silicon chip | 9.5 x 9.5 x 0.5 mm; conductive silver glue | Section 2.1, p.3 |
| CFHX effective length | 42 mm | Section 2.1 |
| Channel section | 8.13 mm x 40 micrometers | Section 2.1 |
| Restriction | 14 parallel slits; each 1000 x 140 x 0.7 micrometers | Section 2.1; manufacturing dimensions |
| Gas / configuration | 99.999% nitrogen; purifier; open cycle | Section 2.1; no compressor modeled |
| Vacuum | Less than 1e-4 Pa | Section 2.1; specific laboratory condition |
| High pressure | 11.1 MPa; pressure controller upstream | Fig.1(e), Sections 2.1-2.2 |
| Low pressure | 0.240 MPa at room-temperature outlet pressure sensor | Section 2.2; not evaporator pressure |
| Return-channel pressure drop | 0.045 MPa | Calculated by authors, not directly measured |
| Evaporator pressure | Approximately 0.285 MPa | Derived by authors from outlet plus calculated drop |
| Fluid boiling temperature | 87.3 K | Authors' EES calculation |
| Measured no-load temperature | 88.5 K | Chip thermometer, 1.2 K above calculated fluid temperature |
| Cooldown mass flow | 2.2 mg/s initially; 8.0 mg/s at 152.8 K; 4.2 mg/s finally | Section 2.2; not a constant throughout the curve |
| Insulation | Three layers; effective emissivity 0.15 | Section 2.1 and Table A2; fitted value |
| Emissivity: silicon / glass | 0.25 / 0.785 | Table A2; silicon fitted, glass from cited literature |
| Peak net heater capacity | 146.9 mW at 153 K | Section 3.2; not capacity at 100 K |
| Uninsulated no-load temperature | 102.4 K at 11.1 MPa | Section 3.3 |
| Uninsulated cooldown failure | Stabilizes at 250.1 K at 10.1 MPa | Section 3.4; colder points required pressure intervention |
| Heat-exchanger effectiveness | Greater than 99% | Model estimate, not direct experimental validation |

### Measurement and capacity definition

Section 2.2 (pp.3-4) defines cooling power as averaged electrical heater input
at steady conditions, with temperature and mass-flow fluctuations below 0.1%
of readout. This does not mean measurement accuracy is 0.1%.

Table 1 reports errors: high pressure +/-0.0605 MPa; low pressure +/-0.0155 MPa;
heater power +/-0.12 mW; temperature +/-0.2 K; mass flow +/-0.2 mg/s. These
instrument errors do not include graph-reading or package-model uncertainty.

Equation 5 subtracts the modeled longitudinal conduction and radiation losses
from the warm-end enthalpy-flow difference to obtain cooling power. The measured
net heater curve therefore cannot be treated as gross evaporator capacity.

Section 3.2 acknowledges a two-phase modeling discrepancy below about 100 K
when liquid enters the low-pressure recuperator. Appendix Table A1 refers heat
transfer and pressure-drop correlations to reference 30 (Cao et al., 2019).
The appendix also notes that measured cooldown mass flow was used because the
restriction flow calculation did not fully match measurements.

### Curve extraction

`data/qi2023_capacity.json` contains approximate visual marker readings from
Figure 5(a), page 5. The zero-load and peak points are text-supported. The large
error-bar illustration near 128 K, 35 mW is excluded. No author raw data were
obtained. Linear interpolation uses only the increasing branch, deliberately
avoiding the descending branch and its potentially different stability behavior.

## Tong et al. (2024), DOI 10.1016/j.cryogenics.2024.103929

| Packaging evidence | Location | Interpretation |
|---|---|---|
| Proposed detector axial length 26 mm vs 75 mm conventional | Table 3, p.8 | Design comparison; complete detector not manufactured |
| Array 320 x 256, 15 micrometer pitch; cold-end diameter enlarged from 3 to 10 mm | Section 4, p.8 | Active array extent is not automatically overall die size |
| Replace O-ring high-pressure seal with brazing; low-pressure outlet uses indium plate sealing | Section 4 | Integration choice; no leak-rate qualification extracted |
| Optical window, filter, thermal shield, detector, gas connection and supports | Fig.17 | Package architecture for literature discussion |
| Extend adiabatic slots; change metal material | Section 4 | Both geometry and material change; effects cannot be isolated from reported combined result |
| Conductive loss decreases 385 to 96 mW | Section 4, p.8 | Calculated under stated common boundaries, not independently measured package losses |
| Nitrogen stainless-steel MMR: 503 mW at 107 K, 10 MPa | Section 3.2, p.7 | Different cooler; do not merge with Qi dataset |
| 38 s cooldown at 60 C is the argon case; nitrogen case 93 s | Section 4, p.9 | Do not attribute 38 s to nitrogen |

The paper calls the selected material 'Kovar alloy 4J36'. This designation
needs independent verification before choosing thermal-expansion or conductivity
data. Preserve the authors' wording as a reported label; do not silently assign
generic Kovar properties to it. No material-specific simulation uses this label.

## Project assumptions (not literature results)

Reference platform retained; additional 3 x 3 mm die; 10 mW dissipation;
50 K/W additional interface; extra support conductance 50 microW/K; extra lead
conductance 20 microW/K; additional effective stage area 100 mm2 at emissivity
0.05; die area 9 mm2 at emissivity 0.2. Baseline optical and residual-gas loads
are zero, with separate nonzero sensitivity cases. Package geometry, vacuum
lifetime, stiffness and electrical performance have not been qualified.

## Decisions

1. Use Qi's measured net capacity to isolate the package problem in version 0.1.
2. Treat Tong as architecture evidence, not numerical validation of this package.
3. Keep 100 K as a detector target, not a fixed evaporator temperature.
4. Do not claim independent validation, high-pressure qualification, or real-fluid
   cycle prediction from the present empirical model.
