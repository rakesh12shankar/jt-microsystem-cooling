"""Bond defect geometry, location, severity and mesh screens for selected package."""
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import ROOT
from array_optimization import adverse
from packaging_model import ScreenCapacity
from bond_defects import basis,equilibrium,allowable_power


def main():
    out=ROOT/'results/extensions';out.mkdir(exist_ok=True)
    p=json.loads((ROOT/'results/advanced/optimization_results.json').read_text(encoding='utf-8'))['selected_inputs']
    rows=[];fields=[]
    def case(condition,shape,fraction,level=8,ratio=1e-4,field=False):
        pp=p if condition=='nominal' else adverse(p)
        c=ScreenCapacity() if condition=='nominal' else ScreenCapacity('lower')
        b=basis(pp,level,fraction,shape,ratio)
        r=equilibrium(pp,b,.01,c);power=allowable_power(pp,b,c)
        limit=None if power is None else equilibrium(pp,b,power,c)
        result=dict(condition=condition,shape=shape,requested_fraction=fraction,
                    actual_fraction=b['actual_fraction'],level=level,conductivity_ratio=ratio,nodes=b['nodes'],
                    power_limit_mW=None if power is None else power*1000,
                    peak_at10mW_K=r['peak_K'],mean_at10mW_K=r['mean_K'],
                    nonuniformity_at10mW_K=r['nonuniformity_K'],
                    passes10mW=bool(r['peak_K']<=100),
                    target_recovery_K=None if limit is None else limit['peak_K'],
                    FE_energy_residual_per_W=float(np.max(np.abs(b['energy_residual_per_W']))),
                    network_energy_residual_W=r['energy_residual_W'])
        if field:fields.append((result,b['points'][b['top_ids'],:2],r['top_temperature_K']))
        return result
    for condition in ['nominal','adverse']:
        rows.append(case(condition,'center_square',0,field=condition=='adverse'))
        for shape in ['center_square','center_circle','edge_strip','corner_square']:
            for f in [.1,.25,.5]:
                rows.append(case(condition,shape,f,field=condition=='adverse' and f==.5 and shape in ['center_square','edge_strip']))
            print(f'Completed {condition} {shape}',flush=True)
    # Exact 25% aligned rectangular footprint for convergence, avoiding changing area.
    mesh=[case('adverse','center_square',.25,level=l) for l in [4,8,12]]
    severity=[case('adverse','center_square',.25,ratio=r) for r in [1e-4,1e-3,.01,.1]]
    result=dict(scope='Thermal-only conductivity defects; assumed geometry and gas/radiation-free gap representation; no crack initiation or reliability claim.',
                scenarios=rows,mesh_25percent=mesh,severity_25percent=severity)
    (out/'bond_defects.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (out/'bond_defects.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    plot_results(rows,fields,out)
    print('Saved bond defect results.',flush=True)


def plot_results(rows,fields,out):
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.2))
    for shape in ['center_square','center_circle','edge_strip','corner_square']:
        rs=[r for r in rows if r['condition']=='adverse' and r['shape']==shape]
        if shape!='center_square':rs=[rows[13]]+rs
        axs[0].plot([100*r['actual_fraction'] for r in rs],[r['power_limit_mW'] for r in rs],'o-',label=shape.replace('square','patch').replace('_',' '))
        axs[1].plot([100*r['actual_fraction'] for r in rs],[r['nonuniformity_at10mW_K'] for r in rs],'o-')
    axs[0].axhline(10,color='black',ls='--',label='10 mW requirement')
    axs[0].set(xlabel='Actual meshed defect area (%)',ylabel='Allowable power at 100 K peak (mW)',title='Selected package, adverse assumptions');axs[0].legend(fontsize=7)
    axs[1].set(xlabel='Actual meshed defect area (%)',ylabel='Peak-to-minimum temperature at 10 mW (K)',title='Temperature nonuniformity')
    for ax in axs:ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'bond_defect_limits.png',dpi=180);plt.close(fig)
    fig,axs=plt.subplots(1,len(fields),figsize=(12,3.8),constrained_layout=True)
    vmin=min(t.min() for _,_,t in fields);vmax=max(t.max() for _,_,t in fields)
    for ax,(r,xy,t) in zip(axs,fields):
        sc=ax.tricontourf(xy[:,0]*1000,xy[:,1]*1000,t,levels=np.linspace(vmin,vmax,17),cmap='inferno')
        ax.set(title=f"{r['shape'].replace('square','patch').replace('_',' ')}\n{r['actual_fraction']*100:.1f}% area; peak {r['peak_at10mW_K']:.2f} K",xlabel='x (mm)',ylabel='y (mm)',aspect='equal')
    fig.colorbar(sc,ax=axs,label='Die surface temperature (K)');fig.savefig(out/'bond_defect_fields.png',dpi=180);plt.close(fig)


if __name__=='__main__':main()
