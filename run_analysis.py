"""Reproduce the baseline, sensitivity plots, and result records."""
from dataclasses import replace,asdict
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import Package,Capacity,solve,maximum_device_power,ROOT

def main():
    out=ROOT/'results'; out.mkdir(exist_ok=True)
    p=Package.load(); c=Capacity(); baseline=solve(p,c)
    scenarios={
        'baseline':p,
        'lower_support_conductance':replace(p,support_W_per_K=20e-6),
        'higher_support_conductance':replace(p,support_W_per_K=200e-6),
        'lower_interface_resistance':replace(p,interface_K_per_W=10),
        'higher_interface_resistance':replace(p,interface_K_per_W=200),
        'higher_stage_emissivity':replace(p,stage_emissivity=.3),
        'extra_5mW_optical_load':replace(p,optical_W=.005),
        'extra_gas_conductance_20uW_per_K':replace(p,gas_W_per_K=20e-6)
    }
    results={k:{**solve(v,c),'maximum_device_power_W':maximum_device_power(v,c)} for k,v in scenarios.items()}
    # Engineering bracket, not a statistical confidence interval.
    uncertainty={str(scale):{**solve(p,Capacity(scale=scale)),
        'maximum_device_power_W':maximum_device_power(p,Capacity(scale=scale))} for scale in [.9,1,1.1]}
    record={'model':'v0.1 empirical reference-platform + incremental package',
            'baseline_inputs':asdict(p),'scenarios':results,'capacity_scale_sensitivity':uncertainty,
            'limitations':['Not an independently validated JT cycle model',
                'Figure points manually approximated; no raw experimental dataset',
                'Fixed 295 K ambient, 11.1/0.24 MPa and reference insulation',
                'Only 88.5-153 K increasing branch; startup not predicted',
                'Added package conductances, areas and interface resistance are assumed']}
    (out/'results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
    fig,ax=plt.subplots(figsize=(7.5,4.4))
    t=np.linspace(c.minimum,c.maximum,500)
    ax.plot(t,1000*c(t),color='#176b87',label='Piecewise-linear measured-performance map')
    ax.scatter(c.T,c.Q*1000,color='#176b87',s=20,label='Figure readings / text endpoints')
    ax.axvline(100,color='#bd6435',ls='--',label='100 K (platform temperature here)')
    ax.scatter([baseline['platform_K']],[baseline['capacity_W']*1000],color='#b12f5b',s=60,zorder=5,label='Assumed package baseline')
    ax.set(xlabel='Reference platform temperature (K)',ylabel='Additional cooling capacity (mW)',title='Reference cooler: Qi et al. (2023), Fig. 5(a)')
    ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.text(.02,.015,'Approximate figure readings; fixed published operating conditions. No extrapolation.',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(out/'capacity_map.png');plt.close(fig)

    fig,ax=plt.subplots(figsize=(8,4.5))
    heat={k:v*1000 for k,v in baseline['loads_W'].items() if v>0}
    labels=[k.replace('_',' ') for k in heat]
    bars=ax.barh(labels,list(heat.values()),color=['#176b87','#45818e','#6fa8a8','#bd6435','#c9925b'][:len(heat)])
    ax.bar_label(bars,fmt='%.2f',padding=4)
    ax.set_xlim(0,max(heat.values())*1.25)
    ax.set(xlabel='Additional load (mW)',title='Assumed package: extra heat-load budget')
    ax.invert_yaxis()
    fig.text(.02,.015,'Existing cooler losses are already included in the capacity map and are not counted again.',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(out/'heat_budget.png');plt.close(fig)

    conductance=np.linspace(0,400e-6,41); resistance=np.linspace(0,250,41)
    temp=np.empty((len(resistance),len(conductance)))
    for i,r in enumerate(resistance):
        for j,g in enumerate(conductance):
            result=solve(replace(p,interface_K_per_W=float(r),support_W_per_K=float(g)),c)
            temp[i,j]=result.get('detector_K',np.nan)
    fig,ax=plt.subplots(figsize=(7.5,4.7))
    mesh=ax.pcolormesh(conductance*1e6,resistance,temp,shading='auto',cmap='viridis')
    contour=ax.contour(conductance*1e6,resistance,temp,levels=[100],colors=['white'],linewidths=2)
    ax.clabel(contour,fmt='%g K',colors='white')
    ax.scatter([p.support_W_per_K*1e6],[p.interface_K_per_W],marker='*',s=110,color='#ffbf47',edgecolors='black',label='Baseline')
    fig.colorbar(mesh,ax=ax,label='Detector temperature (K)')
    ax.set(xlabel='Additional support conductance (µW/K)',ylabel='Additional interface resistance (K/W)',title='Packaging feasibility at 10 mW device dissipation')
    ax.legend(loc='upper left',fontsize=8)
    fig.text(.02,.015,'Illustrative package assumptions; 100 K contour is conditional on the reference capacity map.',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(out/'packaging_feasibility.png');plt.close(fig)

    rows=['# First simulation results','',
        'Status: preliminary package predictions using a published measured-performance map; not independent experimental validation.','',
        '| Scenario | Platform (K) | Detector (K) | Maximum device load for 100 K (mW) |',
        '|---|---:|---:|---:|']
    for name,r in results.items():
        limit=r['maximum_device_power_W']
        rows.append(f"| {name.replace('_',' ')} | {r.get('platform_K',float('nan')):.2f} | {r.get('detector_K',float('nan')):.2f} | {'infeasible even at zero load' if limit is None else f'{limit*1000:.2f}'} |")
    rows+=['','## Interpretation','',
        'Only added package loads are shown. The platform is the reference silicon chip, not the nitrogen evaporator. The detector sits across an additional interface.',
        'Changes to support conductance and emissivity are scenario assumptions, not demonstrated material substitutions.',
        'Maximum load is a steady-state target boundary; it does not guarantee cooldown with the device powered.',
        '', '## Capacity uncertainty scenario','',
        'Scaling all capacities by 0.9 and 1.1 is an engineering sensitivity bracket, not a measured confidence interval. It does not cover temperature-axis digitization error or model-form uncertainty.','']
    for scale,r in uncertainty.items():
        rows.append(f"- Capacity scale {scale}: detector {r['detector_K']:.2f} K; allowable device load {r['maximum_device_power_W']*1000:.2f} mW.")
    rows+=['','## Verification versus validation','',
        'Run `python -m unittest -v`. Tests check a closed-form two-node solution, energy conservation, zero-load behavior, monotonic design trends, overload handling, and domain restrictions.',
        'Agreement at supplied curve points is calibration/interpolation, not independent validation. Independent package validation is still outstanding.','']
    (out/'summary.md').write_text('\n'.join(rows),encoding='utf-8')
    print(json.dumps({'baseline':baseline,'maximum_device_power_mW':maximum_device_power(p,c)*1000,'output':str(out)},indent=2))

if __name__=='__main__':main()
