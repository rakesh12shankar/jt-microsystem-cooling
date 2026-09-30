"""Priorities 1 and 2: specification figure, thermal/thermoelastic FE study."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from model import ROOT
from array_model import design,solve,die_heat,max_power,screens
from package_fem import thermal,mechanical

def compact(d):return {k:v for k,v in d.items() if not isinstance(v,np.ndarray)}

def main():
    out=ROOT/'results/advanced';out.mkdir(parents=True,exist_ok=True)
    p=design();baseline=solve(p)
    plt.rcParams.update({'font.size':10,'figure.dpi':140,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(9,4.8))
    for xy,w,h,color,label in [((-4.75,0),9.5,.5,'#558899','Reference silicon platform (9.5 mm)'),((-3,.5),6,.5,'#91b2ba','Added Si adapter'),((-3,1),6,.15,'#d79454','Adhesive + contact'),((-3,1.15),6,.3,'#3d6379','6 x 5 mm hybrid die')]:
        ax.add_patch(Rectangle(xy,w,h,facecolor=color,edgecolor='black'));ax.text(7.2,xy[1]+h/2,label,va='center',fontsize=9)
    ax.plot([-2.4,2.4],[1.5,1.5],color='#a52943',lw=4);ax.text(0,1.75,'Active array: 4.80 x 3.84 mm',ha='center')
    ax.add_patch(Rectangle((-3.2,2.7),6.4,.12,facecolor='#94c9dc',edgecolor='black'))
    ax.text(0,3.05,'Warm optical window and f/1.2 cone',ha='center')
    ax.plot([-2.4,-3.0],[1.5,2.7],'--',color='#888');ax.plot([2.4,3.0],[1.5,2.7],'--',color='#888')
    ax.plot([-6.75,-4.75],[.25,.25],lw=5,color='#75a966');ax.plot([4.75,6.75],[.25,.25],lw=5,color='#75a966')
    ax.text(-5.8,-.35,'G10 supports',ha='center',fontsize=9)
    ax.set(xlim=(-8,18),ylim=(-.65,3.5),title='Reference array package: schematic cross-section')
    ax.axis('off');fig.text(.02,.02,'Vertical dimensions exaggerated. Candidate layout; seals, feedthroughs and fabrication tolerances are not detailed.',fontsize=8)
    fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(out/'package_section.png');plt.close(fig)
    thermal_rows=[];mechanical_rows=[]
    q=die_heat(baseline['loads_W'])
    for level in [2,4,8]:
        f=thermal(p,level,total_W=q,hotspot_W=.005,base_K=baseline['platform_K'])
        m=mechanical(p,level,cold_K=100)
        thermal_rows.append({'level':level,**compact(f)});mechanical_rows.append({'level':level,**compact(m)})
        print('mesh',level,'thermal nodes',f['nodes'],'max K',f['max_die_K'],'warpage um',m['warpage_um'],flush=True)
    for level in [16,32]:
        m=mechanical(p,level,cold_K=100)
        mechanical_rows.append({'level':level,**compact(m)})
        print('mechanical mesh',level,'nodes',m['nodes'],'warpage um',m['warpage_um'],flush=True)
    # Last mesh retained for figures. Map global node IDs into surface-only IDs.
    top=f['top_ids'];mapping=np.full(len(f['points']),-1,int);mapping[top]=np.arange(len(top))
    fig,ax=plt.subplots(figsize=(7.3,4.8))
    surf=f['points'][top];mesh=ax.tripcolor(surf[:,0]*1e3,surf[:,1]*1e3,mapping[f['top_triangles']],f['temperature_K'][top],shading='gouraud',cmap='inferno')
    ax.set(xlabel='x (mm)',ylabel='y (mm)',title='Die temperature: 10 mW device, 50% central hot spot',aspect='equal')
    fig.colorbar(mesh,ax=ax,label='Temperature (K)');fig.tight_layout();fig.savefig(out/'thermal_fem.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,3.9));pts=m['points'];u=m['displacement_m'];scale=30
    im=ax.tripcolor((pts[:,0]+scale*u[:,0])*1e3,(pts[:,1]+scale*u[:,1])*1e3,m['triangles'],facecolors=m['von_mises_Pa']/1e6,shading='flat',cmap='viridis')
    ax.set(xlabel='x (mm)',ylabel='z (mm)',title='Bonded cross-section: 295 to 100 K, deformation x30')
    fig.colorbar(im,ax=ax,label='Equivalent stress (MPa)')
    fig.text(.02,.01,'Plane-stress screening with assumed effective properties; free-edge peak stress is not a failure criterion.',fontsize=8)
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(out/'cooldown_mechanical_fem.png');plt.close(fig)
    # Property sensitivity keeps material uncertainties visible.
    sensitivities=[]
    for name,changes in [('nominal',{}),('contact resistivity x0.5',{'contact_resistivity_m2K_W':p['contact_resistivity_m2K_W']/2}),('contact resistivity x2',{'contact_resistivity_m2K_W':p['contact_resistivity_m2K_W']*2}),('die k x0.5',{'die_conductivity_W_mK':10}),('die k x2',{'die_conductivity_W_mK':40})]:
        pp={**p,**changes};r=solve(pp);case=thermal(pp,4,total_W=die_heat(r['loads_W']),hotspot_W=.005,base_K=r['platform_K'])
        sensitivities.append({'scenario':name,'max_die_K':case['max_die_K'],'range_K':case['die_nonuniformity_K']})
    record={'baseline':baseline,'max_power_W':max_power(p),'screens':screens(p),
        'thermal_mesh':thermal_rows,'mechanical_mesh':mechanical_rows,'property_sensitivity':sensitivities,
        'thermal_scope':'3D tetrahedral stack, constant effective k, full-area bond/contact, isothermal bottom and adiabatic sides. Network supplies bottom temperature and heat budget; mean is identical to 1D stack in this geometry. Local top source is 5 mW Gaussian sigma 0.35 mm plus uniform remainder.',
        'mechanical_scope':'2D plane-stress tri-elements, constant effective E/nu/CTE, perfect bonded interfaces, left pin/right roller, uniform cooldown. No adhesive plasticity, creep, debonding or package restraint. Central die stress excludes outer 1 mm on both ends.'}
    (out/'fem_results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    rows=['# Priority 2: thermal and mechanical finite-element study','',record['thermal_scope'],'',record['mechanical_scope'],'',
        f"Revised array network: platform {baseline['platform_K']:.3f} K; mean die {baseline['die_K']:.3f} K at 10 mW. Nominal mean-temperature device-power limit: {max_power(p)*1000:.2f} mW.",'',
        '| Level | Thermal nodes | Maximum die K | Die range K | Energy residual W |','|---:|---:|---:|---:|---:|']
    for d in thermal_rows:rows.append(f"| {d['level']} | {d['nodes']} | {d['max_die_K']:.5f} | {d['die_nonuniformity_K']:.5f} | {d['energy_residual_W']:.2e} |")
    rows+=['','| Level | Mechanical nodes | Warpage um | Central die stress MPa | Edge-inclusive peak MPa |','|---:|---:|---:|---:|---:|']
    for d in mechanical_rows:rows.append(f"| {d['level']} | {d['nodes']} | {d['warpage_um']:.4f} | {d['central_die_von_mises_MPa']:.4f} | {d['peak_von_mises_MPa']:.4f} |")
    rows+=['','The highest-mesh change is reported rather than claiming universal mesh independence. Free-edge stress may be singular; use the interior stress and warpage for screening. Neither proves adhesive reliability. The thermal mean agrees with the analytical layered resistance because the bottom is isothermal and the sides are insulated; this is verification, not experimental validation.','',
        '## Property sensitivity','', '| Assumption | Maximum die K | Die range K |','|---|---:|---:|']
    for d in sensitivities:rows.append(f"| {d['scenario']} | {d['max_die_K']:.3f} | {d['range_K']:.3f} |")
    rows+=['','## Interpretation','',
        '- The corrected payload and wiring materially reduce the earlier exploratory power budget.',
        '- A finite bond and a localized readout heat source create a die hot spot; optimization must constrain peak temperature rather than the mean alone.',
        '- Cooldown mismatch produces curvature and interior stress even without mechanical acceleration. Linear effective CTE/modulus assumptions dominate the physical interpretation.',
        '- Supports, wires, seals, glass pressure channels and optical window are not meshed here. Supports/wires remain network and beam-screen elements. A full enclosure FEA requires qualified material, joint and mounting details.',
        '', 'Run `python run_array_fem.py`. The source model is `package_fem.py`; geometry and property assumptions are in `config/array_design.json`.','']
    (out/'02_fem_report.md').write_text('\n'.join(rows),encoding='utf-8')

if __name__=='__main__':main()
