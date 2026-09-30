"""Priority 5: passive power steps on selected optimized array package."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import ROOT
from array_transient import simulate

def main():
    out=ROOT/'results/advanced'
    opt=json.loads((out/'optimization_results.json').read_text(encoding='utf-8'));p=opt['selected_inputs']
    cases=[]
    fig,ax=plt.subplots(figsize=(8,4.8))
    for scale in [.5,1,2]:
        r=simulate(p,capacity_scale=scale,duration=240)
        cases.append({k:v for k,v in r.items() if not isinstance(v,np.ndarray)})
        ax.plot(r['time_s'],r['die_K'],label=f'Heat capacities x{scale:g}')
        if scale==1:
            np.savetxt(out/'power_step.csv',np.c_[r['time_s'],r['platform_K'],r['die_K']],delimiter=',',header='time_s,platform_K,mean_die_K',comments='')
            nominal=r
    ax.axhline(nominal['final']['die_K'],ls=':',color='#888',label='Final equilibrium')
    ax.set(xlabel='Time after power step (s)',ylabel='Mean die temperature (K)',title='Selected package: passive device power step, 10 to 15 mW')
    ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'power_step.png');plt.close(fig)
    tightened=simulate(p,duration=240,rtol=1e-10)
    maxdifference=float(np.max(np.abs(tightened['die_K']-nominal['die_K'])))
    beta=next(d['beta'] for d in opt['FE_beta_K_W'] if d['condition']=='nominal' and abs(d['bond_um']-opt['selected']['bond_um'])<1e-6)
    record={'step_W':[.01,.015],'cases':cases,'tolerance_check_max_difference_K':maxdifference,
        'steady_final_peak_K':nominal['final']['die_K']+beta*.5*.015,
        'status':'Conditional local passive transient. Quasi-steady cooler capacity; assumed heat capacities. No physical transient validation or startup prediction.'}
    (out/'transient_results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    rows=['# Priority 5: local power-step response','',record['status'],'',
        'The selected grid candidate starts at equilibrium with 10 mW device dissipation. At t=0 the device dissipation increases to 15 mW; no heater controller is active. The platform and die store thermal energy while exchanging heat through the stack resistance.','',
        '```text\nCd dTd/dt = Pdevice + Qdie,parasitic - (Td-Tc)/R\nCp dTc/dt = Qplatform,parasitic + (Td-Tc)/R - Qmeasured(Tc)\n```','',
        f"Initial mean die: {nominal['initial']['die_K']:.3f} K; final mean die: {nominal['final']['die_K']:.3f} K. Final steady hot-spot estimate: {record['steady_final_peak_K']:.3f} K. The transient curve is the mean die temperature; spatial hot-spot dynamics are not solved.",'',
        '| Heat capacity scale | 2% settling time s | Overshoot above final mean K | Energy residual J |','|---:|---:|---:|---:|']
    for d in cases:rows.append(f"| {d['capacity_scale']} | {d['settling_2percent_s']} | {d['overshoot_above_final_K']:.3g} | {d['energy_residual_J']:.2e} |")
    rows+=['',f"Nominal local time constants: {nominal['time_constants_s']} s. Tightening solver tolerance from 1e-8 to 1e-10 changed the mean-temperature trace by at most {maxdifference:.3g} K.",'',
        '## Interpretation and limits','',
        '- The passive response for this positive power step is monotone: no overshoot above the new equilibrium is observed. This does not imply zero temperature excursion; the entire equilibrium rise is the excursion from the original setpoint.',
        '- Heat capacities of 0.008 J/K for the die and 0.10 J/K for the platform assembly are assumptions near 100 K. Scaling both changes response time and leaves the steady equilibrium unchanged.',
        '- The measured steady capacity map is assumed to respond instantly. Fluid inventory, phase redistribution, pressure/flow dynamics and the controller may introduce additional modes; the computed time constants are package-model estimates.',
        '- The 15 mW endpoint is a nominal-case demonstration. It exceeds the selected design’s approximately 11.5 mW adverse-case limit; this step is not guaranteed to satisfy 100 K across the assumed uncertainty scenarios.',
        '- This is not a 295 K cooldown simulation. All calculated states remain on the available cold capacity branch.',
        '- The Pei 2024 laser-illumination result involves a different sample, optical absorption and temperature-control protocol. It is not used as validation for this open-loop electrical step.',
        '', 'Run `python run_array_transient.py` after optimization. The CSV stores the nominal trace; JSON includes all heat-capacity scenarios and numerical checks.','']
    (out/'05_transient.md').write_text('\n'.join(rows),encoding='utf-8')
    print(json.dumps({'initial_K':nominal['initial']['die_K'],'final_K':nominal['final']['die_K'],'settling_s':nominal['settling_2percent_s'],'steady_peak_K':record['steady_final_peak_K'],'numerical_difference_K':maxdifference},indent=2))

if __name__=='__main__':main()
