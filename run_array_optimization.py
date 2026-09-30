"""Priority 4: reproducible enumeration with mechanical/electrical constraints."""
import csv,json,itertools
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import ROOT
from array_model import design,solve,screens,die_heat
from array_optimization import adverse,peak_power
from packaging_model import ScreenCapacity
from package_fem import thermal,mechanical

def main():
    p=design();out=ROOT/'results/advanced';out.mkdir(exist_ok=True)
    # FE local-source influence coefficient at each bond thickness/condition.
    betas={}
    for bond in [25e-6,50e-6,100e-6]:
        for condition in ['nominal','adverse']:
            pp={**p,'bond_thickness_m':bond}
            if condition=='adverse':pp=adverse(pp)
            r=thermal(pp,8,total_W=.01,hotspot_W=.005,base_K=0)
            beta=(r['max_die_K']-r['mean_die_K'])/.005
            betas[(bond,condition)]=beta
    rows=[]
    for l,t,w,ll,bond in itertools.product(np.arange(1,4.01,.5)*1e-3,np.arange(.10,.351,.05)*1e-3,[.3e-3,.5e-3,.7e-3],[.005,.008,.012],[25e-6,50e-6,100e-6]):
        pp={**p,'support_length_m':float(l),'support_thickness_m':float(t),'support_width_m':w,'lead_length_m':ll,'bond_thickness_m':bond}
        nom=screens(pp);bad=adverse(pp);worst=screens(bad)
        r={'support_length_mm':l*1000,'support_thickness_mm':t*1000,'support_width_mm':w*1000,'lead_length_mm':ll*1000,'bond_um':bond*1e6,
            'envelope_mm':nom['cold_support_envelope_mm'],'nominal_screens_pass':nom['pass'],'adverse_screens_pass':worst['pass'],
            'nominal_peak_power_mW':None,'adverse_peak_power_mW':None,'adverse_deflection_um':worst['deflection_um']}
        if worst['pass']:
            qnom=peak_power(pp,betas[(bond,'nominal')]);qbad=peak_power(bad,betas[(bond,'adverse')],ScreenCapacity('lower'))
            r['nominal_peak_power_mW']=None if qnom is None else 1000*qnom
            r['adverse_peak_power_mW']=None if qbad is None else 1000*qbad
        rows.append(r)
    feasible=[r for r in rows if r['adverse_peak_power_mW'] is not None and r['adverse_peak_power_mW']>=10]
    if not feasible:raise RuntimeError('No design meets 10mW in adverse scenario')
    # Pareto objectives: maximize adverse useful power; minimize cold support envelope.
    pareto=[r for r in feasible if not any(s['envelope_mm']<=r['envelope_mm'] and s['adverse_peak_power_mW']>=r['adverse_peak_power_mW'] and (s['envelope_mm']<r['envelope_mm'] or s['adverse_peak_power_mW']>r['adverse_peak_power_mW']) for s in feasible)]
    best=max(feasible,key=lambda r:r['adverse_peak_power_mW'])
    selected={**p,'support_length_m':best['support_length_mm']/1000,'support_thickness_m':best['support_thickness_mm']/1000,'support_width_m':best['support_width_mm']/1000,'lead_length_m':best['lead_length_mm']/1000,'bond_thickness_m':best['bond_um']/1e6}
    selected['mechanical_layers']=[dict(layer) for layer in selected['mechanical_layers']]
    selected['mechanical_layers'][1]['thickness_m']=selected['bond_thickness_m']
    # Re-run FE at optimized power for the actual nominal and adverse boundaries.
    boundary_checks=[]
    for condition in ['nominal','adverse']:
        pp=selected if condition=='nominal' else adverse(selected);c=ScreenCapacity() if condition=='nominal' else ScreenCapacity('lower')
        power=best[condition+'_peak_power_mW']/1000;pp={**pp,'device_power_W':power}
        eq=solve(pp,c);f=thermal(pp,8,total_W=die_heat(eq['loads_W']),hotspot_W=.5*power,base_K=eq['platform_K'])
        boundary_checks.append({'condition':condition,'power_W':power,'FE_peak_K':f['max_die_K'],'network_mean_K':eq['die_K'],'balance_W':eq['energy_residual_W']})
    # The selected bond thickness also changes the bonded mechanical stack.
    selected_mechanical={**selected,'mechanical_layers':[dict(layer) for layer in selected['mechanical_layers']]}
    selected_mechanical['mechanical_layers'][1]['thickness_m']=selected['bond_thickness_m']
    mech_checks=[]
    for level in [16,32]:
        result=mechanical(selected_mechanical,level)
        mech_checks.append({'level':level,'warpage_um':result['warpage_um'],'central_die_stress_MPa':result['central_die_von_mises_MPa'],'peak_stress_MPa':result['peak_von_mises_MPa']})
    with (out/'design_grid.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    record={'designs_evaluated':len(rows),'adverse_screen_pass_count':sum(r['adverse_screens_pass'] for r in rows),
        'adverse_10mW_feasible_count':len(feasible),'selected':best,'selected_inputs':selected,'pareto':pareto,
        'FE_beta_K_W':[{'bond_um':k[0]*1e6,'condition':k[1],'beta':v} for k,v in betas.items()],
        'boundary_checks':boundary_checks,'selected_bond_mechanical_mesh':mech_checks,
        'status':'Best within enumerated assumed design grid; not a continuous global optimum or a qualified hardware design.'}
    (out/'optimization_results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    fig,ax=plt.subplots(figsize=(8,4.8));ax.scatter([r['envelope_mm'] for r in feasible],[r['adverse_peak_power_mW'] for r in feasible],s=15,alpha=.3,color='#628694',label='Feasible grid designs')
    frontier=sorted(pareto,key=lambda r:r['envelope_mm']);ax.plot([r['envelope_mm'] for r in frontier],[r['adverse_peak_power_mW'] for r in frontier],'o-',color='#a64239',label='Nondominated tradeoff')
    ax.set(xlabel='Cold support envelope (mm)',ylabel='Adverse-case useful device power (mW)',title='Peak-temperature and constraint-aware package search')
    ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'optimization_frontier.png');plt.close(fig)
    report=['# Priority 4: constrained package optimization','',record['status'],'',
        f"Evaluated {len(rows)} geometries; {record['adverse_screen_pass_count']} pass adverse mechanical/electrical screens; {len(feasible)} also provide at least 10 mW useful device power at a 100 K peak-temperature limit.",'',
        '## Search space','',
        '- Support length: 1–4 mm in 0.5 mm steps; thickness: 0.10–0.35 mm in 0.05 mm steps; width: 0.3, 0.5, 0.7 mm.',
        '- Wire thermal length: 5, 8, 12 mm; wire diameters/count/current remain fixed by the provisional array requirements.',
        '- Bond thickness: 25, 50, 100 um. Manufacturing suitability and bond reliability are not demonstrated.',
        '- Objective pair: maximize adverse useful device power and minimize cold support envelope. Warm cooler length/enclosure remain fixed.',
        '- Constraints: peak die ≤100 K; adverse deflection ≤10 um; stress ≤50 MPa; signal/power resistance ≤20/2 ohm; four-support geometry fits enclosure.',
        '', '## Selected grid candidate','',*['- '+k+': '+str(v) for k,v in best.items()],
        '', '## Peak-temperature correction','',
        'A fine-mesh FE influence coefficient maps the localized 50% of device heat into peak-minus-mean temperature. Each candidate bond thickness has its own coefficient in nominal and adverse conditions. The full-area, constant-property stack is linear, so this superposition is exact within that FE model. Wire and other die loads are treated as uniformly distributed. Final boundary designs are independently rerun through the FE solver.',
        '', '| Condition | Device power mW | FE peak K | Mean die K |','|---|---:|---:|---:|']
    for d in boundary_checks:report.append(f"| {d['condition']} | {d['power_W']*1000:.3f} | {d['FE_peak_K']:.6f} | {d['network_mean_K']:.4f} |")
    report+=['','The selected bond is also rechecked in the mechanical cross-section:',
        '', '| Level | Warpage um | Central die stress MPa |','|---:|---:|---:|']
    for d in mech_checks:report.append(f"| {d['level']} | {d['warpage_um']:.4f} | {d['central_die_stress_MPa']:.3f} |")
    report+=['','## Adverse scenario','',
        'Use the lower measured-capacity reading scenario; support conductivity +20%; wire conductivity +10%; contact resistivity x2; opaque emissivities x2; residual-gas conductance 10 uW/K; out-of-band window transmission 0.03; wire electrical resistivity +20%; support modulus -30%. Other properties remain fixed. This is a prescribed engineering scenario, not a guaranteed worst case or probability statement.',
        '', '## Limits','',
        'The optimum is conditional on laminate stiffness, heat transfer, hypothetical detector power/pinout, bond quality and the chosen hot-spot distribution. Full-area bond contact and fine wire attachment have not been manufactured or tested. Thermoelastic bond stress is reported in the separate FE study; it is not a qualified reliability constraint here because no applicable failure criterion is available. A grid optimum at a bond-thickness bound is a candidate for qualification, not a recommendation to fabricate the thinnest bond.',
        '', 'Run `python run_array_optimization.py`. Complete grid: `design_grid.csv`; selected reproducible inputs and FE checks: `optimization_results.json`.','']
    (out/'04_optimization.md').write_text('\n'.join(report),encoding='utf-8')
    print(json.dumps({'counts':[len(rows),len(feasible)],'selected':best,'FE':boundary_checks},indent=2))

if __name__=='__main__':main()
