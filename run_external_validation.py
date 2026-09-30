"""Unfitted gas-inventory comparison with Pei 2026; not package validation.

Run from the repository root. Numerical source values and their locators are
recorded in docs/benchmark_candidates.md. PDFs are not redistributed.
"""
import json
from CoolProp.CoolProp import PropsSI
from model import ROOT


def inventory(volume_m3, high_Pa, low_Pa, temperature_K):
    if not (volume_m3 > 0 and high_Pa > low_Pa > 0 and temperature_K > 0):
        raise ValueError('Require positive volume/temperature and high > low > 0 pressure')
    return volume_m3 * (PropsSI('Dmass', 'P', high_Pa, 'T', temperature_K, 'Nitrogen')
                       - PropsSI('Dmass', 'P', low_Pa, 'T', temperature_K, 'Nitrogen'))


def main():
    rows = []
    for temperature in [290, 295, 300, 305, 310]:
        main_mass = inventory(.0005, 29.5e6, 9e6, temperature)
        buffer_mass = inventory(.0001, 9e6, 7e6, temperature)
        rows.append(dict(assumed_gas_temperature_K=temperature,
                         usable_main_g=main_mass*1000,
                         main_runtime_min=main_mass/21e-6/60,
                         buffer_runtime_s=buffer_mass/25e-6))
    nominal = rows[2]
    result = {'doi': '10.1016/j.cryogenics.2026.104445',
              'source_locators': 'Main PDF p3 Sec2.1; p4 Sec3.1; p5 Sec3.2/Fig6',
              'assumptions': 'Isothermal inventory, constant flow; 300 K nominal is assumed, not reported. 290-310 K is a sensitivity range, not a confidence interval. Startup and purge excluded.',
              'reported_average_interval_approx_min': 75,
              'reported_inventory_approx_g_model_estimate': 95,
              'main_flow_kg_s': 21e-6, 'buffer_screen_flow_kg_s': 25e-6,
              'temperature_scenarios': rows,
              'nominal_runtime_difference_percent': (nominal['main_runtime_min']/75-1)*100,
              'heat_budget_mW': {'reported_estimated_gross': 234,
                                'reported_estimated_parasitic': 161,
                                'reported_estimated_exhaust_loss': 68,
                                'reconstructed_net': 234-161-68,
                                'measured_net_at_130K': 5.3},
              'decision': 'Conditional consistency with independently published gas-runtime observation. Heat-budget arithmetic is not independent prediction. Thermal package, passive transient and 100 K capacity remain unvalidated by these papers.'}
    out = ROOT/'results/advanced'
    (out/'external_comparison.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    table = '\n'.join(f"| {r['assumed_gas_temperature_K']} | {r['usable_main_g']:.2f} | {r['main_runtime_min']:.2f} | {r['buffer_runtime_s']:.1f} |" for r in rows)
    report = f'''# Full-text external evidence and reproducible comparison

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
{table}

At 300 K, the predicted interval is **{nominal['main_runtime_min']:.2f} min**,
compared with the reported approximate **75 min** average replacement interval
({result['nominal_runtime_difference_percent']:.2f}% difference, without a statistical
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
'''
    (out/'06_external_evidence.md').write_text(report, encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
