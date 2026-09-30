# Full-text external evidence and reproducible comparison

## Outcome

Both supplied Pei papers have been read. The subsequently supplied supplement is
audited in [the supplement report](07_supplement_audit.md), which supersedes the
main-paper-only evidence gaps below. They strengthen the packaging discussion
and support a gas-supply calculation, but do not validate our 100 K array rating
or passive electrical-step transient. See the [source ledger](../../docs/benchmark_candidates.md).

## Unfitted gas-runtime comparison — Pei 2026

Use m = V [rho(P_initial,T) - rho(P_final,T)], and runtime = m / mass flow.
Nitrogen densities come from CoolProp. Main volume is 0.5 L, pressures 29.5 to
9 MPa, flow 21 mg/s. Buffer volume is 0.1 L, pressures 9 to 7 MPa; its conservative
flow screen is 25 mg/s. Source: p3 Sec2.1 and p4 Sec3.1.

**300 K is an explicit assumption**, since the inventory calculation's temperature
is not specified in the main paper. No input is fitted to the reported runtime.
The temperature range below is a scenario sensitivity, not measurement uncertainty.

| Assumed gas K | Main usable g | Main runtime min | Buffer runtime s |
|---:|---:|---:|---:|
| 290 | 98.70 | 78.34 | 92.3 |
| 295 | 96.89 | 76.90 | 90.3 |
| 300 | 95.14 | 75.51 | 88.4 |
| 305 | 93.46 | 74.18 | 86.6 |
| 310 | 91.85 | 72.90 | 84.8 |

At 300 K, the predicted interval is **75.51 min**,
compared with the reported approximate **75 min** average replacement interval
(0.68% difference, without a statistical
accuracy claim). The buffer screen exceeds 60 s in all listed cases. The paper's
approximately 95 g inventory is itself calculated, not a separate measured
validation target. Initial cooldown and purge consumption are excluded.
This tests gas-supply bookkeeping under stated assumptions, not thermal performance.

## Heat budget and transferability

Pei 2026 reports 234 mW estimated gross refrigeration, 161 mW estimated parasitic
load and 68 mW estimated unrecovered exhaust enthalpy. Subtraction yields **5.0 mW**,
consistent to rounding with **5.3 mW measured net heater capacity at 130 K**.
The loss components are model estimates; reproducing their subtraction is not
an independent predictive validation. Supplement S3 has now been reproduced in 07_supplement_audit.md; the exhaust
term is a residual using measured net power, not an independently measured loss.

Pei 2024 reports **36.5 mW at 130 K** on its sample stage. The newer paper explicitly
attributes its lower capacity to chip batch variation. Neither curve may be spliced
into Qi's 11.1 MPa reference curve: pressures, vacuum, mounted loads and chips differ.
Neither measured stage provides a justified extrapolation to our 100 K requirement.
Our 28.5 mW nominal / 11.5 mW adverse package ratings remain conditional on Qi's
measured reference cooler and the documented package assumptions.

## Consequences for the term paper

- Separate reservoir/system dimensions from the cold package. The 2026 gas system
  occupies about 8.91 L and weighs 8.5 kg; its dewar adds 1.1 kg. Small cold hardware
  does not imply a comparably small complete cooling installation.
- Report net capacity of the assembled stage. Gross JT refrigeration alone cannot
  establish usable detector power; parasitics and exhaust losses dominate this example.
- Pei 2024 uses active PID heater compensation. Its 5 mW incident laser is not a
  known absorbed electrical load, so the small controlled temperature excursion
  cannot validate our passive 10-to-15 mW electrical-step model.
- Adhesive gaps are suggested as a possible cause of spatial hot regions in Pei
  2024. This supports investigating interfaces but does not validate our assumed
  full-area bond or contact resistance.
- The 2026 detector demonstration uses a separate chip and a single-point HgTe
  quantum-dot detector, not a 320 x 256 array. Its 102.5 K result and the gas-test
  chip's capacity curve must not be combined as measurements of one assembly.
- Vibration tests at room temperature and 2 MPa do not qualify vibration at the
  nominal cryogenic 7 MPa operating condition. Cold shielding remains future work.

## Remaining evidence needed

The supplementary file S1-S3 has now been supplied and audited in
[07_supplement_audit.md](07_supplement_audit.md). No further PDF is needed for
this audit. Independent thermal validation still requires compatible detector/bond
geometry and independent exhaust/control measurements. The supplementary numerical
inputs allow reproduction of published estimates, not independent net-capacity prediction.
