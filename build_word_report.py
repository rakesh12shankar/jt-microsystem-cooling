"""Assemble the complete technical Word report from reviewed project evidence."""
from pathlib import Path
import re,json
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
doc=Document();sec=doc.sections[0]
sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
sec.top_margin=Inches(.8);sec.bottom_margin=Inches(.75)
sec.left_margin=sec.right_margin=Inches(.8)
sec.footer_distance=Inches(.35)
WIDTH=6.67
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
    st=doc.styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
    st.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Calibri')
normal=doc.styles['Normal'];normal.font.size=Pt(10.5)
normal.paragraph_format.space_after=Pt(6);normal.paragraph_format.line_spacing=1.12
for name,size in [('Title',26),('Subtitle',14),('Heading 1',16),('Heading 2',13),('Heading 3',11.5)]:
    st=doc.styles[name];st.font.size=Pt(size);st.font.bold=name not in ['Subtitle']
    st.paragraph_format.space_before=Pt(14 if name.startswith('Heading') else 0)
    st.paragraph_format.space_after=Pt(7);st.paragraph_format.keep_with_next=True
doc.styles['Caption'].font.size=Pt(9);doc.styles['Caption'].font.italic=True
doc.styles['Caption'].paragraph_format.space_after=Pt(9)
doc.core_properties.title='Joule Thomson Cooling for Infrared Microsystems'
doc.core_properties.subject='Complete technical report on cooler integration and package design'
doc.core_properties.author='';doc.core_properties.keywords='cryogenics, Joule Thomson, microsystems, packaging, finite elements'


def clean(s):
    s=s.replace('→','→').replace('\u0000','').replace('**','').replace('`','')
    s=re.sub(r'\b(a|A|at|At|the|The|all|above|below|from|to|of|with|than|exactly|on|and|for|about|level|levels|case|cells|approximately|Approximately|maximum|minimum|central|separate|original|nominally|is|localized|are|least|drop|emissivity|section|two|five|within|Additional|additional|each)(?=\d)',r'\1 ',s)
    s=re.sub(r'(?<=\d)(K|mW|W|mg|mm|cells|tests)\b',r' \1',s)
    s=re.sub(r',(?=\d{1,2}\b)',', ',s).replace('×','× ')
    s=s.replace('10^-4','10⁻⁴').replace('10^-7','10⁻⁷')
    return s


def inline(p,s):
    # Preserve visible source labels; local project links become ordinary document prose.
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:m.group(1),s)
    for part in re.split(r'(\*\*.*?\*\*|`[^`]+`)',s):
        r=p.add_run(clean(part));r.bold=part.startswith('**')
        if part.startswith('`'):r.font.name='Consolas';r.font.size=Pt(9)


def para(s,style=None):
    p=doc.add_paragraph(style=style);inline(p,s)
    p.paragraph_format.widow_control=True
    return p


def heading(s,level=1):
    s=re.sub(r'[^\w\s]',' ',clean(s));s=re.sub(r'\s+',' ',s).strip()
    return doc.add_heading(s,level)


def table(headers,rows,widths=None):
    if not widths:
        widths=[.37]+[(.63)/(len(headers)-1)]*(len(headers)-1) if len(headers)>1 else [1]
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    for col,w in zip(t.columns,widths):col.width=Inches(WIDTH*w)
    for j,h in enumerate(headers):t.rows[0].cells[j].text=clean(str(h))
    for row in rows:
        c=t.add_row().cells
        for j,val in enumerate(row):c[j].text=clean(str(val))
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
    t._tbl.tblPr.append(borders)
    for i,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr();no=OxmlElement('w:cantSplit');pr.append(no)
        if i==0:
            repeat=OxmlElement('w:tblHeader');pr.append(repeat)
        for j,cell in enumerate(row.cells):
            cell.width=Inches(WIDTH*widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tc=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'343D46' if i==0 else ('F3F5F6' if i%2==0 else 'FFFFFF'));tc.append(shade)
            margins=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');margins.append(e)
            tc.append(margins)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2);p.paragraph_format.line_spacing=1.04
                p.paragraph_format.keep_with_next=(i < len(t.rows)-1) if len(t.rows)<=6 else (i<2)
                p.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 else WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.size=Pt(9);r.font.bold=i==0;r.font.color.rgb=RGBColor(255,255,255) if i==0 else RGBColor(0,0,0)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return t


def equation(s):
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after=Pt(5)
    om=OxmlElement('m:oMathPara');m=OxmlElement('m:oMath')
    subs={'Td':('T','d'),'Tc':('T','c'),'Hd':('H','d'),'Hc':('H','c'),'Cd':('C','d'),'Cp':('C','p'),'Rinterface':('R','int'),'Qreference':('Q','ref'),'Tpeak':('T','peak'),'Tmean':('T','mean'),'Pdevice':('P','dev'),'Qgross':('Q','gross'),'Qnet':('Q','net'),'Qcold-radiation':('Q','cold rad'),'Qwall-to-platform':('Q','wall to platform'),'Tplatform':('T','p'),'Treturn,cold':('T','r,c'),'Rfluid-platform':('R','fp'),'Tinsulation':('T','s'),'Twall':('T','w'),'Tambient':('T','a'),'hh':('h','h'),'hl':('h','l'),'hreturn,cold':('h','r,c'),'hhigh,cold':('h','h,c'),'qh':('q','h'),'ql':('q','l'),'qi':('q','i'),'qr':('q','r'),'qax,in':('q','ax,in'),'qax,out':('q','ax,out'),'epsilon_thermal':('ε','th'),'fthermal':('f','th'),'Ke':('K','e'),'Qdie':('Q','d'),'basis_uniform':('b','u'),'basis_hotspot':('b','h')}
    def run(text):
        r=OxmlElement('m:r');txt=OxmlElement('m:t');txt.text=text;r.append(txt);return r
    pattern='('+ '|'.join(re.escape(k) for k in sorted(subs,key=len,reverse=True))+')'
    for part in re.split(pattern,s):
        if part in subs:
            sub=OxmlElement('m:sSub');base=OxmlElement('m:e');base.append(run(subs[part][0]));index=OxmlElement('m:sub');index.append(run(subs[part][1]));sub.extend([base,index]);m.append(sub)
        elif part:
            for old,new in [('integral','∫'),('grad','∇'),('alpha','α'),('beta','β'),('sigma','σ'),('epsilon','ε'),('dT','ΔT'),('^T','ᵀ'),('^4','⁴'),('*','·'),('rise_vector','θ')]:part=part.replace(old,new)
            m.append(run(part))
    om.append(m);p._p.append(om)


def figure(path,caption=None):
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
    shape=p.add_run().add_picture(str(path),width=Inches(WIDTH))
    shape._inline.docPr.set('descr',caption or path.stem.replace('_',' '))
    return p


def markdown(text,base,heading_offset=0,skip_title=False):
    lines=text.splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'))
            if not(skip_title and level==1):heading(line.lstrip('# ').strip(),min(3,max(1,level-1+heading_offset)))
            i+=1;continue
        if line.startswith('```'):
            lang=line[3:];code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            if lang in ['sh','bash']:
                for c in code:
                    p=para(c);p.paragraph_format.space_after=Pt(1)
                    for r in p.runs:r.font.name='Consolas';r.font.size=Pt(9)
            else:
                for c in code:
                    if c.strip():equation(c)
            i+=1;continue
        if line.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                vals=[v.strip() for v in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+',v) for v in vals):block.append(vals)
                i+=1
            table(block[0],block[1:]);continue
        if line.startswith('!['):
            match=re.match(r'!\[([^]]*)\]\(([^)]+)\)',line)
            figure((base/match[2]).resolve(),match[1]);i+=1;continue
        # Assemble wrapped markdown paragraphs and list items.
        buf=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||!\[|```|[-*] |\d+\. )',lines[i].strip()):buf.append(lines[i].strip());i+=1
        s=' '.join(buf)
        if s.startswith('*Figure '):
            p=para(s.strip('*'),'Caption');p.paragraph_format.keep_with_next=False
        elif s.startswith('- '):para(s[2:],'List Bullet')
        else:para(s)


def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))


# Cover with a direct purpose statement and principal conclusions.
doc.add_paragraph('Joule Thomson Cooling for Infrared Microsystems',style='Title')
doc.add_paragraph('Complete Technical Report',style='Subtitle')
para('30 September 2026')
para('This report evaluates how a miniature nitrogen Joule–Thomson cooler can be integrated with a reference infrared-array package. It brings together the literature evidence, thermal and mechanical models, design search, transient analysis, supplementary-data audit, distributed exchanger model and spatial bond-defect study.')
para('The main engineering conclusion is that package heat leaks and interface quality can determine feasibility even when the cooler alone has sufficient measured capacity. The selected intact package meets the provisional requirement under the prescribed adverse assumptions, but sufficiently large poorly conducting bond regions remove that margin.')
table(['Result','Value','Interpretation'],[
    ['Reference device requirement','10 mW at 100 K peak','Assumed project requirement'],
    ['Selected intact package','28.5 mW nominal\n11.5 mW adverse','Conditional simulated limits'],
    ['50 percent edge bond defect','8.43 mW adverse','Fails the 10 mW requirement'],
    ['Verification suite','43 passing tests','Numerical verification, not hardware qualification']],[.37,.25,.38])
para('Scope: computational reference design and literature reproduction. No manufactured detector package, pressure enclosure, cryogenic joint reliability or imaging performance has been qualified. The distributed exchanger extension remains limited to single-phase vapor return and does not replace the measured capacity map at 100 K.')
doc.add_page_break()
doc.add_paragraph('Contents',style='Title')
p=doc.add_paragraph();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'TOC \\o "1-2" \\h \\z \\u');p._p.append(fld)
doc.add_page_break()
foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
foot.add_run('Page ')
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
for r in foot.runs:r.font.size=Pt(9)

main=(ROOT/'docs/term_paper.md').read_text(encoding='utf-8')
main=main[main.index('## Abstract'):main.index('## References')]
# Avoid filesystem directions in the narrative; the appendix supplies reproduction details.
main=main.replace('and `config/array_design.json`.','and the parameter ledger in Appendix B.')
markdown(main,ROOT/'docs')

doc.add_page_break();heading('Appendix A Detailed model formulation')
para('This appendix records the implementation assumptions needed to reproduce and assess the models. The original network and finite-element methods support the design search; the distributed exchanger and defective-interface formulations are separate extensions with narrower physical claims.')
methods=(ROOT/'docs/advanced_methods.md').read_text(encoding='utf-8')
methods=methods[methods.index('## 2. Finite elements'):methods.index('## Reproduction order')]
methods=re.sub(r'## ([2-5])\.',lambda m:'## A'+str(int(m[1])-1),methods)
methods=re.sub(r'The independent legacy Derking result.*?curve\.',"No test data from other coolers are spliced into Qi's capacity curve.",methods,flags=re.S)
markdown(methods,ROOT/'docs',heading_offset=1)
ext=(ROOT/'docs/extension_methods.md').read_text(encoding='utf-8')
ext=ext[ext.index('## 1. Distributed exchanger'):ext.index('## Reproduce')]
ext=re.sub(r'## ([12])\.',lambda m:'## A'+str(int(m[1])+4),ext)
markdown(ext,ROOT/'docs',heading_offset=1)

doc.add_page_break();heading('Appendix B Input parameters and evidence status')
para('Source-based dimensions and measured boundary conditions are kept separate from surrogate material properties and design requirements. Values in this appendix are the simulation inputs, not procurement specifications.')
p=load('config/array_design.json');o=load('results/advanced/optimization_results.json')
table(['Parameter','Value','Evidence status'],[
 ['Active format','320 × 256 at 15 µm','Tong 2024'],['Active dimensions','4.80 × 3.84 mm','Derived from format'],
 ['Die envelope','6 × 5 × 0.30 mm','Assumed homogenized hybrid'],['Added adapter','6 × 5 × 0.50 mm','Assumed'],
 ['Baseline bond thickness','50 µm','Assumed'],['Selected bond thickness','25 µm','Selected grid value'],
 ['Adapter conductivity','150 W/(m K)','Assumed constant'],['Die conductivity','20 W/(m K)','Assumed effective constant'],
 ['Bond conductivity','0.2 W/(m K)','Assumed'],['Contact resistivity','5 × 10⁻⁴ m² K/W','Assumed nominal'],
 ['Support modulus','20 GPa','Assumed'],['Cold payload','450 mg','Density-based allowance'],
 ['Acceleration','98.0665 m/s²','Assumed 10 g screen'],['Support deflection limit','10 µm','Assumed screen'],
 ['Support stress limit','50 MPa','Assumed screen'],['Lead resistivity','0.72 µΩ m','Assumed'],
 ['Signal wires','12 × 25 µm diameter','Assumed pin budget'],['Power and return wires','4 × 75 µm diameter','Assumed pin budget'],
 ['Signal and power currents','0.1 and 1 mA','Assumed per wire'],['Resistance limits','20 and 2 Ω','Assumed per wire'],
 ['Optical band and cone','3–5 µm and f/1.2','Band assumed; cone from Tong'],['Transmission in and out of band','0.70 and 0.01','Assumed spectral scenario'],
 ['Detector absorptance','0.8','Assumed'],['Additional stage area','200 mm²','Assumed effective exposure'],
 ['Stage and die emissivity','0.05 and 0.20','Assumed'],['Residual gas conductance','0.5 µW/K','Assumed nominal'],
 ['Die and platform capacitance','0.008 and 0.10 J/K','Assumed local values near 100 K'],
 ['Enclosure allocation','70 × 25 × 15 mm','Clearance envelope only']],[.37,.29,.34])
heading('B1 Thermoelastic material surrogates',2)
table(['Layer','Thickness µm','E GPa','Poisson ratio','Expansion 10⁻⁶ per K'],[[x['name'],f"{x['thickness_m']*1e6:.0f}",f"{x['E_Pa']/1e9:g}",x['nu'],f"{x['alpha_per_K']*1e6:g}"] for x in p['mechanical_layers']],[.33,.17,.14,.16,.20])
para('These constant properties are screening assumptions. The selected geometry uses a 25 µm bond in its mechanical recheck. Temperature-dependent modulus, expansion, plasticity, creep and measured joint strength are not available.')
heading('B2 Prescribed adverse scenario',2)
table(['Input','Change from nominal'],[['Capacity curve','Lower reading and instrument allowance scenario'],['Support conductivity','Increase by 20 percent'],['Wire conductivity','Increase by 10 percent'],['Contact resistivity','Multiply by 2'],['Opaque emissivities','Multiply by 2'],['Residual gas conductance','10 µW/K'],['Out of band transmission','0.03'],['Wire resistivity','Increase by 20 percent'],['Support modulus','Decrease by 30 percent']],[.42,.58])
para('The adverse scenario is a deterministic combination of selected assumptions. It is neither a statistical confidence interval nor a demonstrated worst case. Mechanical failure criteria for the adhesive are absent.')

doc.add_page_break();heading('Appendix C Numerical results and convergence records')
f=load('results/advanced/fem_results.json');v=load('results/advanced/calibration_audit.json');b=load('results/extensions/bond_defects.json');h=load('results/extensions/distributed_hx.json')
heading('C1 Baseline thermal and mechanical mesh studies',2)
md=(ROOT/'results/advanced/02_fem_report.md').read_text(encoding='utf-8');start=md.index('| Level | Thermal');end=md.index('## Interpretation');markdown(md[start:end],ROOT/'results/advanced',heading_offset=1)
figure(ROOT/'results/advanced/cooldown_mechanical_fem.png','Baseline bonded cross-section displacement and stress')
para('Figure 8. Baseline bonded cross-section cooldown response. Central stress and warpage support numerical screening; edge-inclusive stress does not qualify adhesive reliability.','Caption')
heading('C2 Calibration and held out temperatures',2)
table(['Platform K','Split','Measured mW','Baseline mW','Corrected mW','Error mW'],[[r['T_K'],r['split'],f"{r['Q_mW']:.1f}",f"{r['baseline_mW']:.1f}",f"{r['corrected_mW']:.1f}",f"{r['corrected_error_mW']:+.1f}"] for r in v['comparisons']],[.16,.15,.18,.17,.18,.16])
para(f"The single fitted radiation-area multiplier is {v['fitted_area_multiplier']:.4f}. Training RMSE is {v['metrics']['train']['RMSE_mW']:.2f} mW and held-out RMSE is {v['metrics']['holdout']['RMSE_mW']:.2f} mW. All points belong to the same experiment. The correction is not used for the package ratings.")
heading('C3 Complete primary bond defect cases',2)
para('The following table retains both nominal and adverse results. Rectangular footprints preserve the die aspect ratio. A conductivity ratio of 10⁻⁴ defines the main poor-contact scenario; actual meshed fractions differ slightly from requested fractions.')
table(['Condition and shape','Area percent','Limit mW','Peak at 10 mW K','Range at 10 mW K'],[[r['condition']+' '+r['shape'].replace('square','patch').replace('_',' '),f"{r['actual_fraction']*100:.2f}",f"{r['power_limit_mW']:.3f}",f"{r['peak_at10mW_K']:.3f}",f"{r['nonuniformity_at10mW_K']:.3f}"] for r in b['scenarios']],[.34,.15,.15,.18,.18])
heading('C4 Bond mesh and defect conductivity checks',2)
table(['Mesh level','Nodes','Area percent','Limit mW','Peak at 10 mW K'],[[r['level'],r['nodes'],f"{r['actual_fraction']*100:.2f}",f"{r['power_limit_mW']:.4f}",f"{r['peak_at10mW_K']:.4f}"] for r in b['mesh_25percent']],[.18,.18,.18,.20,.26])
table(['Conductivity ratio','Allowable power mW','Peak at 10 mW K'],[[r['conductivity_ratio'],f"{r['power_limit_mW']:.4f}",f"{r['peak_at10mW_K']:.4f}"] for r in b['severity_25percent']],[.34,.33,.33])
heading('C5 Distributed exchanger scenario matrix',2)
para('Each entry below is predicted net external capacity in mW. The gas and insulation conductances are total conductances in W/K; gas conductance applies separately to each stream. The 128-cell sweep prescribes measured mass flow at each temperature and assumes ideal fluid-to-platform contact. No coefficients are fitted to this table.')
rows=[]
for g in [.3,1.,3.]:
 for k in [1e-4,.003,.1]:
  rs=[r for r in h['cases'] if r['gas_wall_W_K']==g and r['insulation_contact_W_K']==k]
  rows.append([f'{g:g}',f'{k:g}']+[f"{r['predicted_mW']:.2f}" for r in rs])
table(['Gas G','Insulation G','110 K','120 K','130 K','140 K','153 K'],rows,[.14,.17,.138,.138,.138,.138,.138])
para('Measured Qi marker values for these temperatures are 69.8, 97.0, 121.9, 142.7 and 146.9 mW. The associated prescribed flows are 4.68, 5.81, 6.93, 7.84 and 7.94 mg/s. These manually read data carry measurement and graph-reading allowances; the scenario spread is not a probabilistic interval.')
heading('C6 Exchanger mesh and internal heat flows at 130 K',2)
table(['Cells','Net mW','Radiation mW','Wall to platform mW'],[[r['config']['cells'],f"{r['net_W']*1000:.3f}",f"{r['hx_radiation_W']*1000:.3f}",f"{r['cold_anchor_W']*1000:.2f}"] for r in h['mesh']],[.17,.25,.25,.33])
para('The large wall-to-platform term is an unresolved adequacy issue. It circulates through the evaporator and can cancel in the net balance. Its relation to the much smaller axial-loss estimate in the reference paper requires reconciliation of geometry and boundary definitions.')
heading('C7 Illustrative propagation at a different package target',2)
table(['Gas G W per K','Insulation G W per K','Device limit mW at 130 K mean'],[[f"{r['gas_wall_W_K']:g}",f"{r['insulation_contact_W_K']:g}",f"{r['power_mW']:.2f}"] for r in h['package_130K_mean_screen']],[.3,.3,.4])
para('This is an illustrative mean-temperature target within the modeled vapor branch, not the original 100 K peak-temperature specification. It must not be used to revise the original detector rating.')
heading('C8 Verification summary',2)
checks=load('results/extensions/verification.json')
table(['Check','Observed result'],[['Automated test suite','43 tests passed'],['Exchanger global energy residual',f"Maximum {checks['maximum_hx_global_energy_residual_W']:.2e} W"],['Exchanger entropy screen',f"Minimum {checks['minimum_whole_device_entropy_generation_W_K']:.3g} W/K"],['Bond FE load basis energy residual',f"Maximum {checks['maximum_bond_FE_energy_residual_per_W']:.2e} W/W"],['Central exchanger 128 to 256 cells',f"{checks['hx_central_128_to256_capacity_difference_mW']:.3f} mW net change"],['Checked exchanger corners 128 to 256 cells',f"Maximum {checks['hx_corner_max_128_to256_difference_mW']:.3f} mW net change"],['Bond mesh level 8 to 12',f"{checks['bond_level8_to12_power_difference_mW']:.4f} mW limit change"]],[.57,.43])

heading('Appendix D Experimental source audit')
para('Four recent journal articles provide the main evidence. This appendix identifies what each can support, emphasizing differences in chip, geometry, load definition, operating point and temperature measurement location.')
heading('D1 Qi 2023 reference cooler',2)
para('The 60 × 9.5 × 1.3 mm glass nitrogen cooler has a 42 mm exchanger. The experiment uses 11.1 MPa inlet pressure, 0.24 MPa room-temperature outlet pressure and 295 K surroundings in vacuum below 10⁻⁴ Pa. The 45 kPa return-channel drop is modeled, not directly measured. Net cooling is averaged steady heater power measured at the silicon platform. Instrument errors include ±0.0605 MPa high pressure, ±0.0155 MPa low pressure, ±0.12 mW power, ±0.2 K temperature and ±0.2 mg/s flow [1].')
para('The no-load endpoint is 88.5 K and peak heater capacity is 146.9 mW near 153 K. Intermediate points are manually read, not author raw data. The paper acknowledges difficulty with liquid return below about 100 K. Its modeled radiation and exhaust temperatures are diagnostic outputs rather than independent validation measurements.')
heading('D2 Tong 2024 integration context',2)
para('Tong provides the reference array format and an integrated detector architecture, including window, filter, shield, supports and seals [2]. The proposed 26 mm axial detector package is not transferred to the 60 mm Qi cooler. The metal cooler performance, material changes and gas-specific cooldown results concern different hardware. The stated 38 s cooldown is an argon result; it must not be attributed to the nitrogen reference model. The present package is a literature-format surrogate, not a reproduction of a tested complete commercial array assembly.')
heading('D3 Pei 2024 controlled sample stage',2)
para('The 2024 study uses a 10 × 8 mm quantum-dot-coated SiO₂/Si sample, a silicon holder and silver adhesive, with nitrogen at 7.5 MPa inlet and about 100 kPa outlet and vacuum below 0.1 Pa [3]. It uses active PID heater control. The 5 mW laser value is incident optical power; absorbed power, detailed bond properties and numerical control settings are not provided. Its controlled temperature excursions cannot validate a passive electrical power step.')
table(['Stage temperature K','Net heater capacity mW'],[[120,32.9],[130,36.5],[140,37.9],[150,35.9],[160,29.7]],[.5,.5])
para('Values are printed figure labels with camera illumination present. The 170 K plateau is excluded because clogging prevents steady operation. The camera adds approximately 0.5 mW by heater substitution. Suggested adhesive gaps provide qualitative motivation for the defect study, not measured void geometry. The vibration measurement was performed at room temperature and 2 MPa, rather than cryogenic nominal-pressure operation.')
heading('D4 Pei 2026 and supplementary information',2)
para('The gas-supply tests and single-point HgTe detector demonstration use different chips [4]. Their results cannot be combined into a single measured array assembly. The gas system occupies about 8.91 L and weighs 8.5 kg; the dewar adds 1.1 kg. This illustrates the difference between cold-package size and total installation size. Cold shielding remains future work in that demonstration.')
para('Supplement S3 specifies measured flow of 16.5 mg/s at 130 K, 295 K environment and 7.0/0.285 MPa dewar inlet/outlet pressures. The outlet pressure is adopted from previous work with an identical exhaust line; atmospheric vent pressure is a separate boundary. The reproduced gross refrigeration is 234.05 mW, cold-head radiation 57.61 mW, exchanger radiation 65.07 mW and six-trace conduction 35.90 mW. Axial conduction is bounded below 2 mW.')
para('The approximately 68 mW exhaust loss is inferred using measured 5.3 mW net power. Its associated effectiveness is a residual-based definition, not automatically the earlier model’s pinch-based effectiveness. Eight traces would give approximately 47.9 mW conduction before any shielding contribution. An alternative insulation-temperature assumption gives about 25 mW radiation instead of 65 mW, exposing substantial model dependence.')
heading('D5 Gas inventory and startup arithmetic',2)
extgas=load('results/advanced/external_comparison.json')
table(['Assumed cylinder K','Usable main mass g','Replacement interval min','Buffer duration s'],[[r['assumed_gas_temperature_K'],f"{r['usable_main_g']:.2f}",f"{r['main_runtime_min']:.2f}",f"{r['buffer_runtime_s']:.1f}"] for r in extgas['temperature_scenarios']],[.25,.25,.27,.23])
para('The main volume is 0.5 L with pressure falling from 29.5 to 9 MPa at 21 mg/s; the buffer is 0.1 L from 9 to 7 MPa and screened at 25 mg/s. The 300 K result of 75.5 min is close to the reported approximately 75 min replacement interval. Cylinder temperature is assumed, and purge/cooldown consumption is excluded. The 295 K chamber temperature in S3 does not establish every cylinder temperature.')
para('S1 reports approximately 23 g for replacement purge, 41 g after prolonged air exposure and 35 g after installation. Duration × mean-flow calculations reproduce these values using the 47 min figure caption for the replacement case. However, after subtracting 41 g from 95 g, the remaining 54 g lasts 75 min total at 12 mg/s. A 30 min cooldown leaves 45 min, not the stated 60 min. Variable flow might reconcile the statement, but a supporting flow history is unavailable. S2 gives the controller circuit and dual-mode PID logic but not the numerical gains or timing needed to reproduce closed-loop transients.')

doc.add_page_break();heading('Appendix E Reproducibility and research deliverables')
repro=(ROOT/'docs/reproducibility.md').read_text(encoding='utf-8')
repro=repro[:repro.index('## Sharing contents')]+repro[repro.index('## Physical extensions'):]
repro_count=iter(range(1,10))
repro=re.sub(r'^## ',lambda m:'## E'+str(next(repro_count))+' ',repro,flags=re.M)
markdown(repro,ROOT/'docs',heading_offset=1,skip_title=True)
heading('E6 Research priorities after this report',2)
para('The highest-value next evidence is a specified detector stack and pinout, measured bond contact/defect properties, independently measured exhaust conditions and experimentally supported exchanger wall/film conductances. A compatible integrated-package experiment should withhold its performance results from fitting if it is to serve as independent validation. Pressure containment, sealing, vacuum retention and joint reliability require separate qualification.')

doc.add_page_break();heading('References')
refs=[
'[1] L. Qi, D. Liu, X. Liu, H. Pei, D. Zhao, H. Cao and M. Qiu. Cooling characteristics of a nitrogen micromachined Joule-Thomson cooler operating from 88.5 K to 295 K. Applied Thermal Engineering 227 (2023), 120361. https://doi.org/10.1016/j.applthermaleng.2023.120361',
'[2] X. Tong, J. Qiu, J. Li, K. Xie, J. Chen, Y. Huai, S. Li, Y. Huang and W. Dong. Experimental study and infrared detector application research of micro miniature refrigerators. Cryogenics 143 (2024), 103929. https://doi.org/10.1016/j.cryogenics.2024.103929',
'[3] H. Pei, L. Qi, Y. Lu, D. Liu, J. Zhu, D. Zhao and M. Qiu. Micromachined Joule–Thomson cooling for long-time and precise thermal management. Review of Scientific Instruments 95 (2024), 085118. https://doi.org/10.1063/5.0214551',
'[4] H. Pei, M. Chen, X. Xue, L. Qi, J. Wang, D. Liu, D. Zhao and M. Qiu. A miniaturized low-vibration cryogenic cooling system enabling continuous operation via in-situ gas cylinder replacement. Cryogenics 161 (2026), 104445. Main article and supplementary information S1–S3. https://doi.org/10.1016/j.cryogenics.2026.104445',
'[5] NIST Cryogenic Material Properties. G-10 CR fiberglass epoxy. Temperature-dependent conductivity fits used as property data. https://trc.nist.gov/cryogenics/materials/G-10%20CR%20Fiberglass%20Epoxy/G10CRFiberglassEpoxy_rev.htm',
'[6] NIST Cryogenic Material Properties. 304 stainless steel. Temperature-dependent conductivity fits used as property data. https://trc.nist.gov/cryogenics/materials/304Stainless/304Stainless_rev.htm']
for r in refs:para(r)
para('Software: Python 3.12.14, NumPy 2.3.5, SciPy 1.18.1, Matplotlib 3.11.2 and CoolProp 8.0.0 in the recorded analysis environment. Project source files, inputs and provenance hashes accompany the report in the local repository.')
settings=doc.settings.element;upd=OxmlElement('w:updateFields');upd.set(qn('w:val'),'true');settings.append(upd)
for root in [doc.styles.element,doc.element]:
    for border in list(root.iter(qn('w:pBdr'))):border.getparent().remove(border)
path=OUT/'JT_Microsystems_Complete_Technical_Report.docx';doc.save(path)
print(path)
print('Paragraphs',len(doc.paragraphs),'Tables',len(doc.tables),'Figures',len(doc.inline_shapes))
