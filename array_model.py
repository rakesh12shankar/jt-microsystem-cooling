"""Revised array package: grouped wiring and band-integrated optical loading."""
import json
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
from model import ROOT,SIGMA
from packaging_model import conduct,ScreenCapacity

def design():return json.loads((ROOT/'config/array_design.json').read_text(encoding='utf-8'))

def interface_R(p):
    area=np.prod(p['die_dimensions_m'][:2])
    return (p['bond_thickness_m']/p['bond_conductivity_W_mK']+p['contact_resistivity_m2K_W']+p['die_dimensions_m'][2]/p['die_conductivity_W_mK']+p['adapter_dimensions_m'][2]/p['adapter_conductivity_W_mK'])/area

def band_exitance(t,band):
    # hemispherical Planck exitance integrated over wavelength [m].
    h=6.62607015e-34;c=299792458.;kb=1.380649e-23
    return quad(lambda lam:2*np.pi*h*c*c/(lam**5*np.expm1(h*c/(lam*kb*t))),band[0]*1e-6,band[1]*1e-6,epsabs=1e-10)[0]

def optical(p,td):
    area=np.prod(p['active_dimensions_m']);view=1/(1+4*p['f_number']**2)
    band=band_exitance(p['ambient_K'],p['optical_band_um'])-band_exitance(td,p['optical_band_um'])
    allwave=SIGMA*(p['ambient_K']**4-td**4)
    return float(area*view*p['detector_absorptance']*(p['in_band_transmission']*band+p['out_band_transmission']*(allwave-band)))

def wire_resistance(p,g):return p['lead_resistivity_ohm_m']*p['lead_length_m']/(np.pi*g['diameter_m']**2/4)

def loads(tc,td,p):
    ta=p['ambient_K'];lead=joule=0
    for g in p['lead_groups']:
        area=np.pi*g['diameter_m']**2/4
        lead+=conduct(p['lead_material'],td,ta,area,p['lead_length_m'],g['count'],p.get('lead_k_scale',1))
        joule+=g['count']*g['current_A']**2*wire_resistance(p,g)
    return {'device':p['device_power_W'],
        'leads':lead,'wire_joule':joule,
        'supports':conduct(p['support_material'],tc,ta,p['support_width_m']*p['support_thickness_m'],p['support_length_m'],p['support_count'],p.get('support_k_scale',1)),
        'die_radiation':SIGMA*p['die_emissivity']*(np.prod(p['die_dimensions_m'][:2])-np.prod(p['active_dimensions_m']))*(ta**4-td**4),
        'stage_radiation':SIGMA*p['stage_emissivity']*p['stage_area_m2']*(ta**4-tc**4),
        'optical':optical(p,td),'gas':p['gas_conductance_W_K']*(ta-tc)}

def die_heat(q):return sum(q[k] for k in ['device','leads','wire_joule','die_radiation','optical'])

def solve(p,c=None):
    c=c or ScreenCapacity();r=interface_R(p)
    def die_t(tc):return brentq(lambda td:td-tc-r*die_heat(loads(tc,td,p)),tc,299)
    def fun(tc):return c(tc)-sum(loads(tc,die_t(tc),p).values())
    if fun(c.minimum)>0:return {'status':'below_measured_branch'}
    if fun(c.maximum)<0:return {'status':'above_measured_branch'}
    tc=brentq(fun,c.minimum,c.maximum);td=die_t(tc)
    return {'status':'equilibrium','platform_K':tc,'die_K':td,'interface_K_W':r,'loads_W':loads(tc,td,p),'energy_residual_W':fun(tc)}

def max_power(p,c=None):
    c=c or ScreenCapacity();td=p['target_K'];r=interface_R(p);zero={**p,'device_power_W':0}
    parasitic=die_heat(loads(td,td,zero));upper=td-r*parasitic
    if upper<c.minimum:return None
    def power(tc):return (td-tc)/r-parasitic
    def fun(tc):return c(tc)-sum(loads(tc,td,{**p,'device_power_W':power(tc)}).values())
    if fun(upper)<0:return None
    if fun(c.minimum)>0:raise ValueError('Target boundary below measured domain')
    return float(power(brentq(fun,c.minimum,upper)))

def screens(p):
    l=p['support_length_m'];t=p['support_thickness_m'];w=p['support_width_m'];n=p['support_count']
    force=p['payload_mass_kg']*p['acceleration_m_s2']
    stiff=n*p['young_modulus_Pa']*w*t**3/(4*l**3)
    deflection=force/stiff;stress=6*force*l/(n*w*t*t)
    res={g['name']:wire_resistance(p,g) for g in p['lead_groups']}
    return {'deflection_um':deflection*1e6,'stress_MPa':stress/1e6,'wire_resistance_ohm':res,
        'pass':bool(deflection<=p['max_deflection_m'] and stress<=p['screen_stress_limit_Pa'] and all(res[g['name']]<=g['max_resistance_ohm'] for g in p['lead_groups'])),
        'cold_support_envelope_mm':float((max(p['reference_platform_dimensions_m'][:2])+2*l)*1000)}
