"""Priority 3: predeclared same-experiment holdout and benchmark eligibility.

Radiation area multiplier is an empirical correction, not a physical redesign.
Original model/config remain unchanged. This is not independent validation.
"""
from dataclasses import replace
import json
import numpy as np
from scipy.optimize import minimize_scalar
from model import ROOT
from realfluid import Cycle
from run_realfluid import at_platform_temperature

def main():
    data=json.loads((ROOT/'data/qi2023_validation.json').read_text(encoding='utf-8'))['points']
    training=[100,120,140];heldout=[90,95,110,130,153]
    c=Cycle.load();cache={}
    def predicted(d,a):
        key=(d['T_K'],float(a))
        if key not in cache:
            cc=replace(c,mass_flow_kg_s=d['flow_mg_s']*1e-6,hx_radiation_area_m2=c.hx_radiation_area_m2*a,reference_cold_area_m2=c.reference_cold_area_m2*a)
            cache[key]=at_platform_temperature(d['T_K'],cc)['net_external_W']*1000
        return cache[key]
    def objective(a):return np.mean([(predicted(d,a)-d['Q_mW'])**2 for d in data if d['T_K'] in training])
    fit=minimize_scalar(objective,bounds=(.2,1.2),method='bounded',options={'xatol':.003})
    if not fit.success:raise RuntimeError(fit.message)
    a=float(fit.x);rows=[]
    for d in data:
        rows.append({**d,'split':'train' if d['T_K'] in training else 'holdout',
            'baseline_mW':predicted(d,1),'corrected_mW':predicted(d,a),
            'corrected_error_mW':predicted(d,a)-d['Q_mW']})
    metrics={}
    for subset in ['train','holdout']:
        e=[r['corrected_error_mW'] for r in rows if r['split']==subset]
        metrics[subset]={'RMSE_mW':float(np.sqrt(np.mean(np.square(e)))),'MAE_mW':float(np.mean(np.abs(e)))}
    result={'training_K':training,'heldout_K':heldout,'fitted_area_multiplier':a,'bounds':[.2,1.2],
        'fit_parameters':1,'fixed_parameters':'All remaining Cycle.load defaults; measured mass flow at each point.',
        'comparisons':rows,'metrics':metrics,
        'decision':'Empirical correction assessed on same-experiment holdout. Independent validation remains open; never substitute this fit for measured package capacity.',
        'external_evidence':[
            {'source':'Pei et al. RSI 95,085118 (2024)','doi':'10.1063/5.0214551','status':'Supplied full text read; see docs/benchmark_candidates.md. Different quantum-dot sample stage, temperature control, 120-300 K optical study. Reported <0.2 K response to 5 mW incident laser power cannot validate our open-loop absorbed-power step.'},
            {'source':'Derking et al. RSI 83,045117 (2012)','doi':'10.1063/1.4705988','status':'Legacy author-repository abstract: nitrogen 143 mW at 100 K, radiation40+detector50+wire53=143 mW. This checks bookkeeping only, not our geometry or reference cooler.'}]}
    out=ROOT/'results/advanced';out.mkdir(exist_ok=True)
    (out/'calibration_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    rowsout=['# Priority 3: calibration, holdout and independent-benchmark audit','',
        'The original radiation closure remains physically unresolved. This audit asks whether a single empirical area multiplier transfers to held-out temperatures within Qi’s experiment. The split is fixed in the script before fitting; no held-out values enter the objective.','',
        f'Training: {training} K. Held out: {heldout} K. Fitted multiplier: {a:.4f}, bounded to 0.2–1.2. Both reference radiation areas are multiplied together. All other parameters are frozen; measured flow remains prescribed.','',
        '| Chip K | Split | Measurement mW | Baseline mW | Corrected mW | Corrected error mW |','|---:|---|---:|---:|---:|---:|']
    for r in rows:rowsout.append(f"| {r['T_K']} | {r['split']} | {r['Q_mW']:.1f} | {r['baseline_mW']:.1f} | {r['corrected_mW']:.1f} | {r['corrected_error_mW']:+.1f} |")
    rowsout+=['',f"Training RMSE: {metrics['train']['RMSE_mW']:.2f} mW. Holdout RMSE: {metrics['holdout']['RMSE_mW']:.2f} mW.",'',
        'The fitted area multiplier absorbs multiple possible errors: wall temperature distribution, insulation exposure, emissivity and other omitted losses. Its value is not evidence that a physical surface has this fraction of the original area. No confidence interval or parameter identifiability is claimed. The low-temperature wet-return region is especially demanding; a fit at higher temperatures does not establish applicability there.','',
        '## Independent evidence audit','',
        '- **Pei et al. (2024), Review of Scientific Instruments 95, 085118:** supplied full text confirms active PID compensation and incident laser loading. Missing absorbed fraction and interface/control details prevent passive power-step validation. See 06_external_evidence.md for the full-text audit of both Pei papers.',
        '- **Derking et al. (2012), Review of Scientific Instruments 83, 045117:** legacy integration study with explicit detector/wire/radiation budgeting. Its nitrogen heat budget closes as 143 = 40 + 50 + 53 mW. That is an independent literature consistency check of bookkeeping, not predictive validation of our package or Qi’s cooler.',
        '- **Tong et al. (2024):** detector-format and packaging context; prototype cooler measurements do not establish a tested complete detector package.',
        '', '## What is still needed','',
        'Both Pei main PDFs have been read. The 2026 Supplement S3 has been reproduced; see 07_supplement_audit.md. Its exhaust residual is not independent validation. Independent thermal validation requires: cold-stage and sample dimensions, interfaces, operating pressures/flow, thermometer locations, heater-control protocol, incident-to-absorbed optical power, heat capacities or material stack, time-resolved temperature data and uncertainty. A geometrically compatible experiment must be reproduced without tuning to its test outputs before claiming independent validation.',
        '', 'Priority 3 is complete as an audit and same-experiment holdout study; independent quantitative validation remains open because compatible geometry, boundary conditions and thermal data are incomplete. Subsequent optimization and transients remain explicitly conditional.',
        '', 'Sources: https://doi.org/10.1063/5.0214551; author lab record https://qiu.lab.westlake.edu.cn/info/1079/1672.htm; https://research.utwente.nl/en/publications/a-miniature-joule-thomson-cooler-for-optical-detectors-in-space/; Qi https://doi.org/10.1016/j.applthermaleng.2023.120361.','']
    (out/'03_validation_audit.md').write_text('\n'.join(rowsout),encoding='utf-8')
    print(json.dumps({'multiplier':a,'metrics':metrics},indent=2))

if __name__=='__main__':main()
