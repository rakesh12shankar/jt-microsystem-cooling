"""Milestone 4: conditional benchmark checks, uncertainty screening and diagnosis.

No parameter fitting. Original baseline and empirical map remain unchanged.
"""
from dataclasses import replace
from itertools import product
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI
from model import ROOT
from realfluid import Cycle
from run_realfluid import at_platform_temperature


def budget(r,c):
    s=r['states']
    ideal=c.mass_flow_kg_s*(PropsSI('Hmass','P',c.outlet_pressure_Pa,'T',c.ambient_K,c.fluid)-s['1_warm_high_in']['enthalpy_J_kg'])
    deficit=c.mass_flow_kg_s*(PropsSI('Hmass','P',c.outlet_pressure_Pa,'T',c.ambient_K,c.fluid)-s['5_warm_low_out']['enthalpy_J_kg'])
    terms={'ideal_warm_enthalpy_mW':1000*ideal,'warm_outlet_deficit_mW':1000*deficit,
        'hx_radiation_mW':1000*r['hx_radiation_W'],'cold_radiation_mW':1000*r['cold_reference_radiation_W'],
        'axial_mW':1000*r['reference_axial_W'],'net_mW':1000*r['net_external_W']}
    terms['closure_residual_mW']=terms['ideal_warm_enthalpy_mW']-sum(terms[k] for k in ['warm_outlet_deficit_mW','hx_radiation_mW','cold_radiation_mW','axial_mW','net_mW'])
    return terms


def main():
    data=json.loads((ROOT/'data/qi2023_validation.json').read_text())
    out=ROOT/'results/validation';out.mkdir(parents=True,exist_ok=True)
    base=Cycle.load();rows=[]
    for d in data['points']:
        t=d['T_K'];c=replace(base,mass_flow_kg_s=d['flow_mg_s']*1e-6)
        r=at_platform_temperature(t,c);b=budget(r,c)
        samples=[];failures=[]
        # Table 1 instrument errors plus reading allowances, added conservatively.
        dm=.28 if t==153 else .24
        for st,sm,sh,sl in product([-1,1],repeat=4):
            cc=replace(c,mass_flow_kg_s=(d['flow_mg_s']+sm*dm)*1e-6,
                high_pressure_Pa=c.high_pressure_Pa+sh*60500,
                outlet_pressure_Pa=c.outlet_pressure_Pa+sl*15500)
            try:samples.append(at_platform_temperature(t+st*.8,cc)['net_external_W']*1000)
            except ValueError as e:failures.append(str(e))
        q=b['net_mW'];lo=min(samples);hi=max(samples)
        rows.append({**d,'predicted_mW':q,'error_mW':q-d['Q_mW'],
            'error_percent':100*(q-d['Q_mW'])/d['Q_mW'],
            'input_corner_min_mW':lo,'input_corner_max_mW':hi,'valid_corners':len(samples),
            'invalid_corners':failures,'overlap_with_measurement_allowance':lo<=d['Q_mW']+1.12 and hi>=d['Q_mW']-1.12,
            'budget':b,'fluid_K':r['states']['4_evaporator_return']['temperature_K'],
            'outlet_K':r['states']['5_warm_low_out']['temperature_K']})
    sensitivity=[];diagnosis=[]
    for d in data['author_model_diagnostics']:
        t=d['T_K'];ref=next(v for v in rows if v['T_K']==t)
        c=replace(base,mass_flow_kg_s=ref['flow_mg_s']*1e-6)
        variants=[('baseline',{}),('interface 0 K/W',{'fluid_to_platform_K_W':0}),
            ('interface 30 K/W',{'fluid_to_platform_K_W':30}),('interface 200 K/W',{'fluid_to_platform_K_W':200}),
            ('effectiveness 0.99',{'effectiveness':.99}),('effectiveness 0.9999',{'effectiveness':.9999}),
            ('radiation areas x0.5',{'hx_radiation_area_m2':c.hx_radiation_area_m2*.5,'reference_cold_area_m2':c.reference_cold_area_m2*.5}),
            ('radiation areas x1.5',{'hx_radiation_area_m2':c.hx_radiation_area_m2*1.5,'reference_cold_area_m2':c.reference_cold_area_m2*1.5}),
            ('low drop 0 kPa',{'low_drop_Pa':0}),('low drop 90 kPa',{'low_drop_Pa':90000}),
            ('high drop 0 kPa',{'high_drop_Pa':0}),('high drop 100 kPa',{'high_drop_Pa':100000})]
        for name,kw in variants:
            r=at_platform_temperature(t,replace(c,**kw))
            sensitivity.append({'T_K':t,'scenario':name,'predicted_mW':1000*r['net_external_W']})
        hw=PropsSI('Hmass','P',c.outlet_pressure_Pa,'T',d['warm_outlet_K'],c.fluid)
        hh=PropsSI('Hmass','P',c.high_pressure_Pa,'T',c.ambient_K,c.fluid)
        diagnostic=1000*c.mass_flow_kg_s*(hw-hh)-d['total_radiation_mW']
        diagnosis.append({**d,'measured_mW':ref['Q_mW'],
            'baseline_total_radiation_mW':ref['budget']['hx_radiation_mW']+ref['budget']['cold_radiation_mW'],
            'author_output_energy_balance_range_mW':[diagnostic-2,diagnostic],
            'qualification':'Conditional Eq. 5 reconstruction using author-model radiation/outlet, prescribed measured flow, and 0-2 mW axial conduction; not a corrected predictive model or independent validation.'})
    errors=np.array([v['error_mW'] for v in rows])
    record={'status':'Numerical verification passed; baseline capacity validation failed; package validation unavailable.',
        'method':'No fitting. Conditional on measured flow. 16 input corners per temperature are a deterministic screening range, not a statistical confidence interval or guaranteed global extrema. All model assumptions held fixed in that screen.',
        'comparisons':rows,'sensitivity':sensitivity,'diagnosis':diagnosis,
        'metrics':{'MAE_mW':float(np.mean(abs(errors))),'RMSE_mW':float(np.sqrt(np.mean(errors**2))),
            'screen_overlap_count':sum(v['overlap_with_measurement_allowance'] for v in rows),'points':len(rows)}}
    (out/'results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':10,'figure.dpi':140,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8,4.6));t=np.array([v['T_K'] for v in rows]);q=np.array([v['predicted_mW'] for v in rows])
    ax.errorbar(t,[v['Q_mW'] for v in rows],xerr=.8,yerr=1.12,fmt='o',capsize=3,color='#176b87',label='Qi experiment + reading/instrument allowance')
    ax.plot(t,q,'s-',color='#b35932',label='Unfitted real-fluid baseline')
    ax.fill_between(t,[v['input_corner_min_mW'] for v in rows],[v['input_corner_max_mW'] for v in rows],color='#b35932',alpha=.18,label='Input-corner screen (assumptions fixed)')
    ax.set(xlabel='Reference silicon-chip temperature (K)',ylabel='Net cooling capacity (mW)',title='Milestone 4: conditional capacity benchmark')
    ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.text(.02,.015,'Measured nitrogen flow supplied to model; bands are not confidence intervals.',fontsize=8)
    fig.tight_layout(rect=[0,.045,1,1]);fig.savefig(out/'benchmark.png');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4.5),sharey=True)
    keys=['net_mW','hx_radiation_mW','cold_radiation_mW','axial_mW','warm_outlet_deficit_mW']
    colors=['#176b87','#c86543','#dda56f','#777777','#b5bed0']
    labels=['Net cooling','HX radiation','Cold-region radiation','Axial conduction','Warm-outlet deficit']
    for ax,tval in zip(axes,[100,153]):
        ref=next(v for v in rows if v['T_K']==tval);bottom=0
        for k,col,label in zip(keys,colors,labels):
            v=ref['budget'][k];ax.bar(0,v,bottom=bottom,color=col,label=label);bottom+=v
        ax.bar(1,ref['Q_mW'],color='#176b87',alpha=.6)
        ax.set_xticks([0,1],['Model budget','Measured net']);ax.set_title(f'{tval} K');ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('Power (mW)');axes[1].legend(fontsize=8,loc='upper left',bbox_to_anchor=(1,1))
    fig.suptitle('Where the available warm-end enthalpy difference goes')
    fig.tight_layout();fig.savefig(out/'loss_budget.png');plt.close(fig)
    report=['# Milestone 4 — verification and validation assessment','',record['status'],'',
        '## Experimental comparison','',record['method'],'',
        '| Chip K | Measured mW | Predicted mW | Error % | Input-corner range mW | Overlap? |',
        '|---:|---:|---:|---:|---:|:---:|']
    for v in rows:report.append(f"| {v['T_K']} | {v['Q_mW']:.1f} | {v['predicted_mW']:.1f} | {v['error_percent']:+.1f} | {v['input_corner_min_mW']:.1f}–{v['input_corner_max_mW']:.1f} | {'yes' if v['overlap_with_measurement_allowance'] else 'no'} |")
    report+=['',f"MAE = {record['metrics']['MAE_mW']:.1f} mW; RMSE = {record['metrics']['RMSE_mW']:.1f} mW. {record['metrics']['screen_overlap_count']}/8 points overlap the input-corner screen and ±1.12 mW measurement/reading allowance.",
        '','These errors establish that the baseline does not reproduce the selected published experiment within this screening allowance. Uncertainty in the assumed heat-loss model is not included in the band. The 153 K power is reported in text; the same conservative power allowance is retained.','',
        '## Discrepancy diagnosis','',
        'The baseline radiation loss is about twice the radiation shown in the authors’ model, Figure 8(b). That comparison implicates effective exposed area, insulation representation and wall-temperature distribution; it does not identify which is wrong. Radiation and outlet-temperature values from the authors’ model are correlated with their fitted emissivity and must not be treated as independent experimental evidence.','',
        '| Chip K | Baseline total radiation mW | Author-model radiation mW | Eq. 5 diagnostic net mW |',
        '|---:|---:|---:|---:|']
    for d in diagnosis:report.append(f"| {d['T_K']} | {d['baseline_total_radiation_mW']:.1f} | {d['total_radiation_mW']:.0f} ±2 | {d['author_output_energy_balance_range_mW'][0]:.1f}–{d['author_output_energy_balance_range_mW'][1]:.1f} |")
    report+=['','The diagnostic range varies axial conduction from 2 to 0 mW; it excludes reading/property/flow uncertainties. It substitutes the authors’ modeled warm outlet (294.9 K) and radiation in the whole-cooler energy balance. It is an accounting check, not a new validated simulation.','',
        '## Assumption sensitivity','', '| Scenario | Capacity at 100 K, mW | Capacity at 153 K, mW |','|---|---:|---:|']
    for v in [x for x in sensitivity if x['T_K']==100]:
        other=next(x for x in sensitivity if x['T_K']==153 and x['scenario']==v['scenario'])
        report.append(f"| {v['scenario']} | {v['predicted_mW']:.1f} | {other['predicted_mW']:.1f} |")
    report+=['','Area multipliers probe the radiation closure; they are not proposed geometry changes or fitted corrections. The pressure-drop sweeps are assumption scenarios, not measured uncertainty.','',
        '## Packaging consequence','',
        'The approximately 92 K detector result is not a validated design prediction. The empirical capacity map remains usable for explicitly conditional package heat-budget comparisons within the reference experiment’s domain. Its heater data do not validate the added die interface, supports, leads, optical window or vacuum enclosure.','',
        'Milestone 5 should compare package architectures using the measured net-capacity map with uncertainty bounds, report assumptions, and keep the real-fluid cycle as a sensitivity model until radiation and hydraulic closures are substantiated.','',
        '## Evidence needed to close validation','',
        '- Raw temperature–flow–heater data would tighten digitization; no additional PDF is required for this assessment.',
        '- To resolve the physics discrepancy: exposed-area/insulation geometry and measured or independently calculated wall temperatures; temperature-dependent pressure drops and interface resistance.',
        '- To validate the proposed package: a separate experiment reporting die and platform temperatures, dissipated power, interface, supports, leads and enclosure conditions. Tong (2024) proposes a complete detector package but does not report a completed integrated detector test, so it cannot supply this validation.',
        '', 'Source: Qi et al. (2023), https://doi.org/10.1016/j.applthermaleng.2023.120361, Figures 5, 8(b), A2, Table 1, Eq. 5. Packaging status: Tong et al. (2024), https://doi.org/10.1016/j.cryogenics.2024.103929.',
        '', 'See ../../docs/validation.md for verification gates and scope. Original milestone-3 configuration and results are preserved.','']
    (out/'summary.md').write_text('\n'.join(report),encoding='utf-8')
    print(json.dumps({'metrics':record['metrics'],'diagnosis':diagnosis,'corners':[v['valid_corners'] for v in rows]},indent=2))

if __name__=='__main__':main()
