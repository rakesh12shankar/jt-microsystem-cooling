# Supplement audit: Pei 2026

Source: supplied `1-s2.0-S0011227526001700-mmc1.pdf`, five pages;
DOI https://doi.org/10.1016/j.cryogenics.2026.104445.
S1-S3 have now been read, including visual inspection of the equations and tables.
This report supersedes earlier statements that the supplement or 130 K inputs were missing.

## Heat-budget reproduction

Tables S1/S2 give 130 K cold-head temperature, 295 K ambient, measured16.5 mg/s
flow, 7 MPa inlet and 0.285 MPa dewar outlet pressure. The outlet pressure is
adopted from the earlier identical exhaust line, not measured in this test.
Atmospheric vent pressure is not the same as pressure at the dewar outlet.
The 21 mg/s gas-runtime condition must not replace this heater-test flow.

The script evaluates the stated gray-radiation expressions, integrates the linear
MLI temperature profile analytically, uses the supplied copper conductivity integral,
and calculates nitrogen enthalpies with CoolProp. No parameter is fitted.

| Term | Reproduced mW | Paper approximate mW |
|---|---:|---:|
| Ideal gross | 234.05 | 234 |
| Cold-head radiation | 57.61 | 58 |
| CFHX radiation | 65.07 | 65 |
| Six copper leads | 35.90 | 36 |

Glass axial conduction is reported only as less than2 mW. Taking0-2 mW as a
bounding screen gives total parasitics **158.59-160.59 mW**.
The paper's approximately161 mW uses rounded terms and the upper conduction allowance.

Using the measured5.3 mW net power, the remaining exhaust term is
**68.16-70.16 mW**.
The derived effectiveness is **70.0-70.9%**.
These ranges reflect an axial-conduction bound, not measurement confidence intervals.

**Critical distinction:** exhaust loss is an energy-balance residual, not an
independent exhaust-temperature measurement. The paper defines effectiveness as
1 - Q_unrecovered/Q_gross. It is not automatically interchangeable with our
pinch-based cycle parameter. Subtracting the derived residual to recover5.3 mW
would be circular validation. This work reproduces the published heat-load
estimates; it does not independently predict net capacity.

## Packaging consequences

- Six connected copper traces contribute **35.90 mW**. Eight traces with a
  detector would contribute **47.87 mW** under the same temperature
  endpoints. The supplement says silver shielding may add about50%, giving a
  scenario of **71.80 mW**. These are alternative wiring loads,
  not incremental loads to add wholesale to a curve that already includes leads.
- The paper gives an alternative MLI temperature model yielding about25 mW,
  compared with65 mW from the linear-profile model. This roughly40 mW model
  dependence exceeds the measured5.3 mW net capacity. Fixing the measured net
  power makes this change transfer into the inferred exhaust loss; it does not
  establish an available40 mW performance improvement.
- Cold-head radiation includes exposed glass and silicon as well as the window.
  A lower-emissivity ZnSe window reduces the reported total only from58 to56 mW.
  Window changes alone therefore do not address the dominant total heat leak.
- The silicon-to-wall expression is reproduced as printed with view factor0.5.
  Because its complement also equals0.5, this case cannot verify how that printed
  expression should generalize to other view factors.
- Our reference-array estimates remain conditional on Qi's cooler. The new
  source supports interface/wiring/insulation priorities, not replacement of
  the cooler map or a qualified100 K array rating.

## Startup gas arithmetic — S1, pp1-2

The supplement adds useful purge data and one apparent arithmetic inconsistency:

| Scenario | Calculation from stated duration and mean flow | Reported |
|---|---:|---:|
| Dewar replacement | 47 min x8.3 mg/s =23.41 g |23 g |
| One-month air exposure |23 h x0.5 mg/s =41.4 g |41 g |
| Chip installation |14 h x0.7 mg/s =35.28 g |about35 g |

For replacement, the caption gives47 min while the prose says within1 hour;
using47 min explains the reported23 g. However, after a41 g purge from95 g,
the remaining54 g lasts **75 min total at12 mg/s**. Subtracting30 min cooldown
leaves **45 min steady operation**, not the stated60 min. The stated30+60 min
would require64.8 g at constant12 mg/s, or a lower time-averaged flow. Variable
flow could explain it, but a time-resolved flow trace is not supplied. Keep
this discrepancy explicit; do not use the90 min claim as a validation target.
At constant10-25 mg/s,54 g leaves6-60 min steady operation after30 min cooldown;
the paper's20-75 min range likewise requires different flow/time assumptions.
This does not invalidate the separately reported steady replacement experiment.

The earlier gas-runtime comparison retains300 K as an assumed cylinder temperature:
295 K in Table S2 describes the heat-load calculation's chamber temperature and
does not establish the cylinder temperature during every gas-supply trial.

## Controller and validation status

S2 provides the circuit and an aggressive/conservative dual-mode PID description.
It does not supply numerical gains, switching threshold, sample interval or raw
transient traces sufficient for reproduction. The passive electrical-step model
therefore remains separate from the controlled experiments.

No further PDF is needed to finish this source audit. Independent thermal validation
would require measured exhaust temperature (or another independently established
exchanger-loss model), uncertainty and compatible detector/bond geometry and data.
The term paper can accurately claim a reproduced published heat budget and a
conditional gas-runtime comparison, alongside verified package simulations.

Reproduce with `python run_supplement_audit.py`. Numerical inputs and results are
saved in `supplement_audit.json`; source PDFs remain outside shareable outputs.
