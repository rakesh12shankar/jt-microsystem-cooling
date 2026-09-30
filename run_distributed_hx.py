"""Unfitted constitutive scenarios, mesh study and conditional package propagation."""
from dataclasses import replace
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from distributed_hx import HX,solve_hx
from model import ROOT
from array_model import max_power


def main():
    out=ROOT/'results/extensions';out.mkdir(exist_ok=True)
    (ROOT/'tmp').mkdir(exist_ok=True)
    points=json.loads((ROOT/'data/qi2023_validation.json').read_text(encoding='utf-8'))['points']
    eligible=[p for p in points if p['T_K']>=110]
    rows=[];profiles=[];base=HX(cells=128)
    for gas in [.3,1.,3.]:
        for coupling in [1e-4,.003,.1]:
            c=replace(base,gas_wall_W_K=gas,insulation_contact_W_K=coupling)
            for point in eligible:
                row=dict(gas_wall_W_K=gas,insulation_contact_W_K=coupling,**point)
                try:
                    r=solve_hx(point['T_K'],point['flow_mg_s']*1e-6,c)
                    row.update(status='converged_vapor',predicted_mW=1000*r['net_W'],error_mW=1000*r['net_W']-point['Q_mW'],
                               hx_radiation_mW=r['hx_radiation_W']*1000,cold_anchor_mW=r['cold_anchor_W']*1000,
                               energy_residual_W=r['energy_residual_W'],return_superheat_K=r['return_superheat_min_K'])
                    if point['T_K']==130:profiles.append(r)
                except (ValueError,RuntimeError) as e:row.update(status='rejected',reason=str(e))
                rows.append(row)
            print(f'Completed gas conductance {gas}, insulation coupling {coupling}',flush=True)
            (ROOT/'tmp/hx_sweep_checkpoint.json').write_text(json.dumps(dict(cases=rows,profiles=profiles),indent=2),encoding='utf-8')
    mesh=[]
    for n in [16,32,64,128,256]:
        r=solve_hx(130,6.93e-6,replace(base,cells=n))
        mesh.append({k:v for k,v in r.items() if k not in ['x','high_K','low_K','wall_K','insulation_K']})
        print(f'Mesh {n}: net {r["net_W"]*1000:.3f} mW',flush=True)
    contact=[]
    corner_mesh=[]
    for gas,coupling in [(.3,.1),(3.,1e-4),(3.,.1)]:
        for n in [128,256]:
            r=solve_hx(130,6.93e-6,replace(base,cells=n,gas_wall_W_K=gas,insulation_contact_W_K=coupling))
            corner_mesh.append(dict(cells=n,gas_wall_W_K=gas,insulation_contact_W_K=coupling,net_mW=r['net_W']*1000))
    print('Completed corner resolution checks',flush=True)
    for resistance in [0,50,100]:
        for temperature,flow in [(110,4.68e-6),(130,6.93e-6),(153,7.94e-6)]:
            try:
                r=solve_hx(temperature,flow,replace(base,fluid_platform_K_W=resistance))
                contact.append(dict(R_K_W=resistance,T_K=temperature,status='vapor_solution',net_mW=r['net_W']*1000,superheat_K=r['return_superheat_min_K']))
            except (ValueError,RuntimeError) as e:contact.append(dict(R_K_W=resistance,T_K=temperature,status='rejected',reason=str(e)))
    # Illustrative mean-temperature package target lies inside modeled range.
    # Never use this >=110 K extension to update the original 100 K rating.
    selected=json.loads((ROOT/'results/advanced/optimization_results.json').read_text(encoding='utf-8'))['selected_inputs']
    propagated=[]
    class Curve:
        minimum=110.;maximum=153.
        def __init__(self,subset):self.f=interp1d([r['T_K'] for r in subset],[r['predicted_mW']/1000 for r in subset],bounds_error=True)
        def __call__(self,t):return float(self.f(t))
    for gas in [.3,1.,3.]:
        for coupling in [1e-4,.003,.1]:
            sub=[r for r in rows if r['gas_wall_W_K']==gas and r['insulation_contact_W_K']==coupling]
            record=dict(gas_wall_W_K=gas,insulation_contact_W_K=coupling,target_mean_K=130.)
            if all(r['status']=='converged_vapor' for r in sub):
                try:
                    power=max_power({**selected,'target_K':130},Curve(sub))
                    record.update(status='boundary' if power is not None else 'no_zero_load_margin',power_mW=None if power is None else power*1000)
                except ValueError as e:record.update(status='outside_model_domain',reason=str(e))
            else:record['status']='incomplete_curve'
            propagated.append(record)
    result=dict(scope='Single-phase vapor return; prescribed measured flows and pressure drops; unfitted conductance scenarios. Not an independently validated cooler map.',
                cases=rows,mesh=mesh,corner_mesh=corner_mesh,finite_contact_screen=contact,package_130K_mean_screen=propagated,profiles_at130K=profiles)
    (out/'distributed_hx.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    fields=sorted(set().union(*(r.keys() for r in rows)))
    with (out/'distributed_hx.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
    fig,axs=plt.subplots(1,2,figsize=(11,4.5))
    for gas in [.3,1.,3.]:
        for coupling in [1e-4,.003,.1]:
            rs=[r for r in rows if r['gas_wall_W_K']==gas and r['insulation_contact_W_K']==coupling and r['status']=='converged_vapor']
            axs[0].plot([r['T_K'] for r in rs],[r['predicted_mW'] for r in rs],alpha=.55,label=f'Gg={gas:g}, Gi={coupling:g}')
    axs[0].plot([p['T_K'] for p in eligible],[p['Q_mW'] for p in eligible],'ko',label='Qi measurements')
    axs[0].set(xlabel='Platform temperature (K)',ylabel='Net external capacity (mW)',title='Unfitted conductance scenarios (128 cells)');axs[0].legend(fontsize=6,ncol=2)
    r=next(r for r in profiles if r['config']['gas_wall_W_K']==1 and r['config']['insulation_contact_W_K']==.003)
    x=np.asarray(r['x']);mid=(x[:-1]+x[1:])/2
    for key,label in [('high_K','High-pressure gas'),('low_K','Return gas'),('wall_K','Glass wall'),('insulation_K','Insulation')]:axs[1].plot(x if len(r[key])==len(x) else mid,r[key],label=label)
    axs[1].plot(x,295+(130-295)*x,'k--',label='Imposed linear reference')
    axs[1].set(xlabel='Axial position, warm → cold',ylabel='Temperature (K)',title='Solved temperatures: central scenario at 130 K');axs[1].legend(fontsize=8)
    for ax in axs:ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'distributed_hx.png',dpi=180);plt.close(fig)
    print('Saved distributed exchanger results.',flush=True)


if __name__=='__main__':main()
