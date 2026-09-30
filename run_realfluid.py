"""Milestone 3: compute cycle states, compare benchmarks and save results."""
from dataclasses import asdict,replace
import json,platform,importlib.metadata
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from CoolProp.CoolProp import PropsSI
from model import ROOT,Package
from realfluid import Cycle,evaluate,solve_package,slit_flow_diagnostic

def at_platform_temperature(target,c):
    lo=PropsSI('Hmass','P',c.evaporator_Pa,'Q',0,c.fluid)
    hi=PropsSI('Hmass','P',c.evaporator_Pa,'T',160,c.fluid)
    h=brentq(lambda h:evaluate(h,c)['platform_K']-target,lo,hi,xtol=1e-6)
    return evaluate(h,c)

def main():
    out=ROOT/'results/realfluid';out.mkdir(parents=True,exist_ok=True)
    c=Cycle.load();p=Package.load();r=solve_package(p,c)
    if r['status']!='equilibrium':raise RuntimeError('Baseline has no equilibrium')
    no_load=solve_package(replace(p,device_power_W=0,support_W_per_K=0,lead_W_per_K=0,
        stage_area_m2=0,device_area_m2=0,optical_W=0,gas_W_per_K=0),c)
    comparisons=[]
    for t,m,measured in [(100,4.4e-6,63),(153,7.9e-6,146.9)]:
        case=at_platform_temperature(t,replace(c,mass_flow_kg_s=m))
        predicted=case['net_external_W']*1000
        comparisons.append({'platform_K':t,'prescribed_flow_mg_s':m*1e6,
            'reported_or_digitized_mW':measured,'predicted_mW':predicted,
            'relative_difference_percent':100*(predicted-measured)/measured,
            'qualification':'100 K power and both flows are approximate figure readings; 153 K peak power is text-reported. Pressure drops retained, not independently recomputed.'})
    convergence=[]
    for nodes in [41,81,161]:
        case=solve_package(p,replace(c,pinch_nodes=nodes))
        convergence.append({'pinch_nodes':nodes,'detector_K':case['detector_K'],'gross_W':case['gross_cold_W'],'pinch_K':case['pinch_K']})
    sensitivity=[]
    for eps in [.98,.995,.999]:
        case=solve_package(p,replace(c,effectiveness=eps))
        sensitivity.append({'effectiveness':eps,'status':case['status'],'detector_K':case.get('detector_K')})
    record={'cycle_inputs':asdict(c),'package_inputs':asdict(p),'baseline':r,
        'no_extra_load_platform_K':no_load['platform_K'],
        'reference_no_load_K':88.5,'reference_fluid_saturation_K':87.3,
        'slit_flow_diagnostic_mg_s':slit_flow_diagnostic(r['platform_K'],c)*1e6,
        'capacity_comparisons':comparisons,'pinch_sampling_convergence':convergence,
        'effectiveness_sensitivity':sensitivity,
        'runtime':{'python':platform.python_version(),'CoolProp':importlib.metadata.version('CoolProp')},
        'status':'Baseline implementation complete; predictive capacity validation not passed. No parameter fitting performed in this run.'}
    (out/'results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    plt.rcParams.update({'figure.dpi':140,'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8,4.5));pr=r['profile'];x=np.array(pr['x_warm_to_cold'])*42
    ax.plot(x,pr['high_K'],color='#b64b38',label='High-pressure stream: warm to cold')
    ax.plot(x,pr['low_K'],color='#176b87',label='Low-pressure stream: cold to warm')
    ax.set(xlabel='Axial coordinate from warm end (mm)',ylabel='Fluid temperature (K)',title='Real-fluid recuperator: baseline temperature profiles')
    ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.text(.02,.02,'Assumed distributed heat transfer and radiation profiles; sampled pinch constraint enforced.',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(out/'recuperator_profile.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.3));a=np.arange(len(comparisons));w=.32
    ax.bar(a-w/2,[v['reported_or_digitized_mW'] for v in comparisons],w,label='Published / approximate figure value',color='#176b87')
    ax.bar(a+w/2,[v['predicted_mW'] for v in comparisons],w,label='Real-fluid simplified model',color='#bd6435')
    ax.set_xticks(a,[f"{v['platform_K']} K" for v in comparisons]);ax.set(ylabel='Net external cooling capacity (mW)',title='Capacity discrepancy remains significant')
    ax.legend(fontsize=8)
    fig.text(.02,.02,'Measured-flow inputs used. This comparison is not independent validation.',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(out/'capacity_comparison.png');plt.close(fig)
    rows=['# Milestone 3: real-fluid baseline','',record['status'],'',
        '## Coupled baseline','',
        f"- Nitrogen saturation temperature: {c.saturation_K:.2f} K (paper: 87.3 K).",
        f"- Reference platform: {r['platform_K']:.2f} K; additional detector: {r['detector_K']:.2f} K.",
        f"- Gross cold-region heat pickup: {r['gross_cold_W']*1000:.2f} mW.",
        f"- Net capacity after reference cold radiation and axial conduction: {r['net_external_W']*1000:.2f} mW.",
        f"- Recuperator radiation pickup (separate): {r['hx_radiation_W']*1000:.2f} mW.",
        f"- No-extra-package-load platform: {no_load['platform_K']:.2f} K (paper: 88.5 K).",
        f"- Restriction diagnostic: {record['slit_flow_diagnostic_mg_s']:.2f} mg/s; cycle uses prescribed 4.2 mg/s.",
        '', '## Five cycle states','', '| State | Pressure (MPa) | Temperature (K) | Enthalpy (kJ/kg) | Vapor mass fraction |',
        '|---|---:|---:|---:|---:|']
    for name,s in r['states'].items():
        q='single phase' if s['quality']<0 else f"{s['quality']:.3f}"
        rows.append(f"| {name.replace('_',' ')} | {s['pressure_Pa']/1e6:.3f} | {s['temperature_K']:.2f} | {s['enthalpy_J_kg']/1000:.2f} | {q} |")
    rows+=['','The wet return means liquid continues into the recuperator. This state is included thermodynamically; actual two-phase pressure drop and distributed heat transfer are not resolved. Enthalpy reference zero is arbitrary.','',
        '## Capacity comparison','', '| Platform temperature | Reference (mW) | Model (mW) | Difference |','|---|---:|---:|---:|']
    for b in comparisons:rows.append(f"| {b['platform_K']} K | {b['reported_or_digitized_mW']:.1f} | {b['predicted_mW']:.1f} | {b['relative_difference_percent']:.1f}% |")
    rows+=['','The near agreement in no-load temperature is insufficient to establish validity: platform thermal resistance is an assumed input and the same pressure boundary determines the saturation temperature. The capacity discrepancies are material.',
        '', '## Numerical checks','',
        f"- Maximum local/cycle/package energy residual: {max(abs(r[k]) for k in ['hx_energy_residual_W','cycle_energy_residual_W','package_energy_residual_W']):.2e} W.",
        f"- Valve enthalpy residual: {r['valve_enthalpy_residual_J_kg']:.2e} J/kg.",
        f"- Minimum sampled recuperator temperature difference: {r['pinch_K']:.3f} K.",
        f"- Detector temperature spread across 41/81/161 pinch samples: {max(v['detector_K'] for v in convergence)-min(v['detector_K'] for v in convergence):.4g} K.",
        '', '## Effectiveness sensitivity','']
    for s in sensitivity:rows.append(f"- Effectiveness {s['effectiveness']}: {s['status']}; detector {s['detector_K']} K.")
    rows+=['','## Interpretation and next milestone','',
        'Milestone 3 is complete for the agreed simplified steady-state baseline: real-fluid properties, recuperation, isenthalpic throttling, phase tracking, explicit reference heat leaks, and coupled package balance.',
        'Milestone 4 must address independent validation, improved figure digitization, heat-transfer/radiation distribution, interface resistance and two-phase hydraulic closure. No allowable-load or design superiority claim should be based on this model yet.',
        'See ../../docs/realfluid_model.md for equations, boundaries, assumptions and deferred physics.','']
    (out/'summary.md').write_text('\n'.join(rows),encoding='utf-8')
    print(json.dumps({'baseline_detector_K':r['detector_K'],'capacity_comparisons':comparisons,'convergence':convergence,'effectiveness':sensitivity},indent=2))

if __name__=='__main__':main()
