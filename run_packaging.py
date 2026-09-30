"""Reproduce milestone 5: package architectures and constraint-aware tradeoffs."""
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import ROOT
from packaging_model import ScreenCapacity,equilibrium,max_power,constraints,conductivity


def main():
    cfg=json.loads((ROOT/'config/packaging.json').read_text(encoding='utf-8'));common=cfg['common']
    out=ROOT/'results/packaging';out.mkdir(parents=True,exist_ok=True)
    records=[]
    for arch in cfg['architectures']:
        p={**common,**arch};nom=equilibrium(p);limits={k:max_power(p,ScreenCapacity(k)) for k in ['lower','nominal','upper']}
        adverse={**p,'support_k_scale':1.2,'lead_k_scale':1.1,'interface_K_W':2*p['interface_K_W'],
            'stage_emissivity':.1,'die_emissivity':.4,'gas_conductance_W_K':10e-6,'optical_gray_factor':1,
            'lead_resistivity_ohm_m':1.2*p['lead_resistivity_ohm_m']}
        stress=constraints({**adverse,'young_modulus_Pa':.7*p['young_modulus_Pa']})
        records.append({'name':arch['name'],'inputs':p,'at_10mW':nom,'constraints':constraints(p),
            'max_device_power_W':limits,'adverse_max_device_power_W':max_power(adverse,ScreenCapacity('lower')),
            'adverse_constraints':stress})
    # One-at-a-time effects relative to compact G10 architecture B.
    p=records[1]['inputs'];sens=[]
    for label,changes in [
        ('B baseline',{}),('interface 20 K/W',{'interface_K_W':20}),('interface 100 K/W',{'interface_K_W':100}),
        ('16 leads',{'lead_count':16}),('50 um leads',{'lead_diameter_m':50e-6}),
        ('stage emissivity 0.2',{'stage_emissivity':.2}),('gas G = 20 uW/K',{'gas_conductance_W_K':20e-6}),
        ('aperture diameter 2 mm',{'aperture_diameter_m':.002}),('lead current 10 mA',{'lead_current_A':.01})]:
        pp={**p,**changes};sens.append({'scenario':label,'max_power_W':max_power(pp),'constraints':constraints(pp)})
    record={'status':'Conditional package tradeoff study completed; no integrated-package experimental validation.',
        'capacity':'Qi experimental net capacity, original increasing 88.5–153 K map; fixed pressure/ambient/reference package.',
        'architectures':records,'sensitivity':sens,'assumptions':cfg['assumptions'],
        'uncertainty':'Capacity-only lower/upper: shift chip temperature by ±1.2 K and power by ±3.12 mW, inside common interpolation domain. Adverse case additionally combines support k +20%, lead k +10%, interface R x2, stage/die emissivity x2, gas G=10 uW/K, optical factor=1, resistivity +20%, modulus -30%. These are engineering scenarios, not confidence bounds or manufacturing tolerance guarantees.',
        'property_samples_W_mK':{mat:{str(t):float(conductivity(mat,t)) for t in [90,100,200,295]} for mat in ['ss304','g10_warp']}}
    (out/'results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    with (out/'comparison.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['architecture','detector_K_at_10mW','Pmax_nominal_mW','Pmax_lower_capacity_mW','Pmax_upper_capacity_mW','Pmax_adverse_mW','deflection_um','lead_ohm','screens_pass'])
        for r in records:
            writer.writerow([r['name'],r['at_10mW'].get('detector_K'),*[None if r['max_device_power_W'][k] is None else r['max_device_power_W'][k]*1000 for k in ['nominal','lower','upper']],None if r['adverse_max_device_power_W'] is None else r['adverse_max_device_power_W']*1000,r['constraints']['deflection_um'],r['constraints']['lead_resistance_ohm'],r['constraints']['combined_pass']])
    plt.rcParams.update({'font.size':10,'figure.dpi':140,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(9,4.8))
    for i,r in enumerate(records):
        power=r['max_device_power_W']['nominal'];con=r['constraints']['combined_pass']
        if power is None:ax.text(i,1,'No 100 K solution\neven at zero power',ha='center',fontsize=8)
        else:
            values=r['max_device_power_W'];lo=values['lower'];hi=values['upper']
            ax.bar(i,power*1000,color='#176b87' if con else '#c98a48',hatch=None if con else '//')
            ax.errorbar(i,power*1000,yerr=[[1000*(power-lo)],[1000*(hi-power)]],color='black',capsize=5)
            ax.scatter(i,r['adverse_max_device_power_W']*1000 if r['adverse_max_device_power_W'] is not None else 0,marker='D',color='#a6293d',zorder=5)
    ax.set_xlim(-.65,3.65)
    ax.set_xticks(range(4),['A: steel','B: compact G10','C: long thin G10','D: reinforced G10'])
    ax.set(ylabel='Maximum device dissipation at 100 K (mW)',title='Package thermal capacity and preliminary design screens')
    ax.axhline(10,color='#777',ls=':',label='10 mW project load');ax.grid(axis='y',alpha=.2)
    fig.text(.02,.015,'Whiskers: capacity-reading scenarios. Diamonds: combined adverse case. Hatching: constraint failure.',fontsize=8)
    fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(out/'architecture_comparison.png');plt.close(fig)
    # Length/thickness study fixes all other B inputs. Shared geometry affects both heat and stiffness.
    lengths=np.linspace(1,4,25)*1e-3;thickness=np.linspace(50,200,25)*1e-6
    powers=np.zeros((25,25));deform=np.zeros_like(powers);safe=np.zeros_like(powers,dtype=bool)
    for i,t in enumerate(thickness):
        for j,l in enumerate(lengths):
            pp={**p,'support_thickness_m':float(t),'support_length_m':float(l)}
            limit=max_power(pp);powers[i,j]=np.nan if limit is None else limit*1000
            con=constraints(pp);deform[i,j]=con['deflection_um'];safe[i,j]=con['combined_pass'] and limit is not None and limit>=.01
    fig,ax=plt.subplots(figsize=(8,4.8))
    mesh=ax.pcolormesh(lengths*1e3,thickness*1e6,powers,shading='auto',cmap='viridis')
    cs=ax.contour(lengths*1e3,thickness*1e6,deform,levels=[10],colors='white',linewidths=2)
    ax.clabel(cs,fmt='10 um deflection',fontsize=8)
    ax.contourf(lengths*1e3,thickness*1e6,deform,levels=[10,1e6],colors='none',hatches=['////'])
    ax.scatter([2],[100],marker='*',s=120,color='#efb44b',edgecolor='black')
    ax.set(xlabel='Support length (mm)',ylabel='Support thickness (um)',title='G10 geometry: thermal benefit versus bending compliance')
    fig.colorbar(mesh,ax=ax,label='Nominal maximum device power at 100 K (mW)')
    fig.text(.02,.015,'Hatched region fails assumed 10 um deflection limit at 5 mg payload and 10 g. Star: architecture B.',fontsize=8)
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(out/'support_tradeoff.png');plt.close(fig)
    report=['# Milestone 5 — packaging tradeoffs','',record['status'],'',
        '## Question and architecture','',
        'How much useful detector dissipation can an added package support at 100 K while limiting support deflection and lead resistance? The reference Qi chip remains the cold platform. A separate 3 × 3 mm die connects across an added interface. Four supports connect the platform to the warm enclosure; eight wires connect the die to warm feedthroughs. A gray optical aperture, exposed opaque surfaces and residual gas add heat.','',
        'The 10 mW device load and 100 K target are project assumptions, not requirements supplied by a detector manufacturer. The study is steady-state; startup, reliability and integrated-package performance are unvalidated.','',
        '## Results','',
        '| Architecture | Die K at 10 mW | Max device power mW | Capacity-only range mW | Combined adverse mW | Mechanical/electrical screen |',
        '|---|---:|---:|---:|---:|---|']
    def fmt(x):return 'infeasible' if x is None else f'{1000*x:.1f}'
    for r in records:
        c=r['constraints'];limits=r['max_device_power_W'];temp=r['at_10mW'].get('detector_K')
        report.append(f"| {r['name']} | {f'{temp:.1f}' if temp else r['at_10mW']['status'].replace('_',' ')} | {fmt(limits['nominal'])} | {fmt(limits['lower'])}–{fmt(limits['upper'])} | {fmt(r['adverse_max_device_power_W'])} | {'pass' if c['mechanical_pass'] else 'fail'} / {'pass' if c['electrical_pass'] else 'fail'} |")
    report+=['','Ranges cover only capacity-reading scenarios. Combined adverse values vary multiple package assumptions together. Neither is a statistical confidence interval. “Infeasible” means even zero device dissipation cannot meet 100 K in this branch. A thermal limit remains listed for C to show why thermal ranking alone is insufficient.','',
        '## Geometry and preliminary constraints','',
        'All supports: four tabs, width 0.30 mm. Leads: eight 304 stainless wires, diameter 25 um. The material choice is a low-current thermal candidate with assumed electrical resistivity; it is not a qualified detector interconnect.','',
        '| Architecture | Support L / thickness mm | Wire L mm | Interface K/W | Deflection um | Lead resistance ohm |',
        '|---|---:|---:|---:|---:|---:|']
    for r in records:
        pp=r['inputs'];c=r['constraints']
        report.append(f"| {r['name']} | {pp['support_length_m']*1e3:.1f} / {pp['support_thickness_m']*1e3:.2f} | {pp['lead_length_m']*1e3:.0f} | {pp['interface_K_W']:.0f} | {c['deflection_um']:.2f} | {c['lead_resistance_ohm']:.1f} |")
    report+=['','Mechanical screen: equal-load cantilever bending under a 5 mg payload at 10 g; deflection ≤10 um and stress ≤50 MPa. Electrical screen: ≤20 ohm per lead at 100 uA assumed current. Moduli and resistance limits are design assumptions. This is not a structural or electrical qualification.','',
        '## Interpretation','',
        '- The steel-support case demonstrates how a warm-to-cold mechanical path can consume the cooling budget. A working cooler alone does not establish package feasibility.',
        '- Architecture C reduces support/wire heat leakage and passes the nominal bending screen; it fails the lead-resistance limit.',
        '- B and D are candidates for further study. D changes both support geometry and interface resistance. The one-at-a-time interface sweep isolates the thermal advantage; reinforcement itself is not claimed to improve cooling.',
        '- B and D have equal support thickness/length ratios, so this beam model gives equal support heat leakage and stiffness. Longer supports offer no free thermal gain when thickness is raised proportionally to preserve stiffness.',
        '- No design is selected for fabrication. Required next evidence includes cryogenic joints, actual detector pin count/current, G10 directional stiffness, optical spectral response, and vacuum-compatible assembly.',
        '', '## One-at-a-time changes from B','', '| Change | Max device power at 100 K, mW |','|---|---:|']
    for s in sens:report.append(f"| {s['scenario']} | {fmt(s['max_power_W'])} |")
    report+=['','These comparisons hold all other inputs fixed. The 10 mA case includes conservative deposition of all wire Joule heat at the die. The model does not assess voltage drop, bandwidth or noise beyond the resistance screen.','',
        '## Added heat budget at 10 mW','', '| Path | B heat, mW | D heat, mW |','|---|---:|---:|']
    for key in records[1]['at_10mW']['loads_W']:
        report.append(f"| {key.replace('_',' ')} | {records[1]['at_10mW']['loads_W'][key]*1000:.3f} | {records[3]['at_10mW']['loads_W'][key]*1000:.3f} |")
    report+=['','Only added loads appear here. Reference-cooler heat leaks are already embedded in Qi’s measured net capacity and are not subtracted a second time.','',
        '## Uncertainty and limitations','',record['uncertainty'],'',*['- '+a for a in cfg['assumptions']],
        '', '## Sources and reproducibility','',
        '- Cooler reference: Qi et al. (2023), Applied Thermal Engineering, https://doi.org/10.1016/j.applthermaleng.2023.120361.',
        '- Packaging context: Tong et al. (2024), Cryogenics, https://doi.org/10.1016/j.cryogenics.2024.103929. Its proposed package is not treated as an integrated detector validation dataset.',
        '- Conductivity: NIST cryogenic materials fits, linked with coefficients and ranges in `../../data/packaging_materials.json`. These are legacy property references supporting the recent journal case studies.',
        '- Inputs: `../../config/packaging.json`; equations: `../../docs/packaging_model.md`; numerical records: `results.json`; table: `comparison.csv`.',
        '- Reproduce: `python run_packaging.py`; verify: `python -m unittest -v`. No proprietary solver or network access required.',
        '', 'Milestone 5 is complete as a conditional design study. Milestone 6 will consolidate the term paper, repository documentation and a defensible project/resume summary.','']
    (out/'summary.md').write_text('\n'.join(report),encoding='utf-8')
    print(json.dumps([{'name':r['name'],'maximum_W':r['max_device_power_W'],'constraints':r['constraints'],'adverse_W':r['adverse_max_device_power_W']} for r in records],indent=2))

if __name__=='__main__':main()

