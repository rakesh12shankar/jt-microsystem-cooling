# Full-text benchmark evidence ledger

Both user-supplied main papers read on 2026-09-30. Page numbers below are physical
PDF pages; the RSI file includes a publisher cover. Numerical figure labels are
transcribed values, not high-precision digitization. PDFs and extracted text are
excluded from shareable project outputs.

## Pei et al. 2024 — controlled optical sample stage

**Micromachined Joule–Thomson cooling for long-time and precise thermal management**,
Review of Scientific Instruments 95, 085118. https://doi.org/10.1063/5.0214551

| Evidence | Location | Use / limitation |
|---|---|---|
| 60 x 9.5 x 1.3 mm three-layer glass cooler; silver adhesive and silicon holder; 10 x 8 mm QD-coated SiO2/Si sample | PDF p3, SecII | Different sample from our array; full bond and substrate properties missing |
| Nitrogen 7.5 MPa inlet, atmospheric 100 kPa outlet; vacuum below 0.1 Pa | PDF p3 | Different boundary conditions from Qi reference |
| Active PID heater; PT100; 5 mW incident 473 nm laser, estimated 2.2 um spot | PDF p3 | Absorbed fraction and controller parameters missing; not passive step validation |
| No-load 107.4 +/- 0.1 K after 65 min; camera adds about 0.5 mW by heater substitution | PDF p4-5, Fig2 | Stage-specific observations |
| Net heater mW at K: 32.9 at120, 36.5 at130, 37.9 at140, 35.9 at150, 29.7 at160 | PDF p4-5, Fig2d/e | Camera on; directly labeled steady plateaus, not our capacity map |
| 17.8 mW at170 K is not steady owing to clogging | PDF p4-5 | Exclude from steady benchmark fitting |
| Temperature uncertainty +/-0.1 K; heater power +/-0.1 mW | PDF p4 | Reported measurement uncertainties |
| Flow below10 mg/s estimated from earlier design; cylinder runtime over7 days estimated | PDF p4 | Neither is an independently measured operating-point/runtime datum |
| Local hot regions possibly due to adhesive gaps | PDF p7, SecIIIC | Qualitative interface motivation, not measured void geometry |
| Vibration tested at room temperature, 2 MPa | PDF p7, SecIIID | Not cryogenic nominal-pressure validation |

The optical PL comparison's inferred 8-9 K difference is relative to another
cooling setup; it is not a measured die-platform drop to impose on our package.

## Pei et al. 2026 — replaceable gas supply and detector demonstration

**A miniaturized low-vibration cryogenic cooling system enabling continuous
operation via in-situ gas cylinder replacement**, Cryogenics 161, 104445.
https://doi.org/10.1016/j.cryogenics.2026.104445 (online July30, September issue).

| Evidence | Location | Use / limitation |
|---|---|---|
| Main cylinder0.5 L, 29.5 to9 MPa; buffer0.1 L, 9 to7 MPa | p3 Sec2.1 | Inventory calculation inputs; gas temperature unspecified |
| Approximately95 g calculated usable main inventory; typical21 mg/s chip | p3 | Model estimate and gas-test chip operating flow |
| Approximately75 min average replacement interval; steady cycling after initial cooldown | p4 Sec3.1 | External runtime observation; exclude startup/purge |
| Gas supply198 x153 x294 mm, 8.5 kg; dewar1.1 kg | p3 | System scale, not cold package dimensions |
| 7 MPa operating pressure, atmospheric exhaust | p3-4 | Different reference conditions |
| Measured net heater capacity mW: 0.8 at125 K, 5.3 at130 K, 17.6 at140 K, 21.8 at150 K | p5 Fig6 | Gas-test chip; no justified extrapolation to100 K |
| Estimated gross234, parasitics161, exhaust loss68 mW; reported exchanger effectiveness about71% | p5 Sec3.2 | Definitions/calculation in SupplementS3; not independent measured components |
| Gas-supply chip differs from chip used for vibration and detector tests | p3 | Keep datasets separate |
| HgTe single-point3-5 um detector at102.5 K; coated window above97% transmission in3-5 um | p7-8 | Not FPA qualification; specific optical coating, not our assumed spectrum |
| Room-temperature2 MPa vibration tests; cold shield not integrated | p5-6, p8 | Cryogenic vibration and shielding remain open |

## Supplement received and reproduced

The five-page supplement S1-S3 was supplied on 2026-09-30. Tables S1/S2
(pp4-5) specify295 K, measured16.5 mg/s at130 K, inlet7 MPa and adopted
outlet0.285 MPa. This distinguishes dewar outlet pressure from atmospheric venting.
The [supplement audit](../results/advanced/07_supplement_audit.md) reproduces
cold radiation57.61 mW, exchanger radiation65.07 mW, six-lead conduction35.90 mW
and gross refrigeration234.05 mW. Axial conduction is bounded below2 mW.
The exhaust loss and effectiveness use measured net power as an input; they
are not independently measured validation targets. S1's stated constant-flow
startup budget has an apparent arithmetic inconsistency documented in the audit.
S2 supplies a dual-mode PID schematic/flowchart but no numerical gains or timing.

## Acceptance rule and status

The [computed comparison](../results/advanced/06_external_evidence.md) reproduces
gas inventory/runtime without fitting. Thermal package validation remains open:
it requires compatible measurement locations, geometry/interfaces, operating
conditions and load definitions. Same-paper loss arithmetic is a consistency
check, and fitted unknown boundary conditions would be calibration.
