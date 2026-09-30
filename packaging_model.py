"""Geometry-based incremental package: temperature-dependent conduction."""
import json
import numpy as np
from scipy.optimize import brentq
from model import ROOT,Capacity,SIGMA

MATERIALS=json.loads((ROOT/'data/packaging_materials.json').read_text(encoding='utf-8'))['materials']
GX,GW=np.polynomial.legendre.leggauss(32)

def conductivity(material,t):
    m=MATERIALS[material];t=np.asarray(t)
    if np.any(t<m['range_K'][0]) or np.any(t>m['range_K'][1]):
        raise ValueError('Temperature outside conductivity fit range')
    return 10**np.polynomial.polynomial.polyval(np.log10(t),m['coefficients'])

def conduct(material,cold,hot,area,length,count=1,scale=1):
    if length<=0 or area<0 or count<0 or scale<=0:raise ValueError('Invalid conduction geometry')
    mid=(hot+cold)/2;half=(hot-cold)/2
    return float(count*area/length*scale*half*np.dot(GW,conductivity(material,mid+half*GX)))

class ScreenCapacity:
    """Conservative reading-error scenarios inside the common interpolation domain."""
    def __init__(self,kind='nominal'):
        if kind not in ['nominal','lower','upper']:raise ValueError('Unknown capacity scenario')
        self.c=Capacity();self.kind=kind
        # Use original map's larger ±1 K / ±3 mW manual allowance plus instrument errors.
        self.dt=1.2;self.dq=.00312
        self.minimum=self.c.minimum+(self.dt if kind!='nominal' else 0)
        self.maximum=self.c.maximum-(self.dt if kind!='nominal' else 0)
    def __call__(self,t):
        if t<self.minimum-1e-9 or t>self.maximum+1e-9:raise ValueError('Outside capacity scenario domain')
        sign={'nominal':0,'lower':-1,'upper':1}[self.kind]
        return max(0,float(self.c(np.clip(t+sign*self.dt,self.c.minimum,self.c.maximum)))+sign*self.dq)

def heat_loads(tc,td,p):
    ta=p['ambient_K'];aw=np.pi*p['lead_diameter_m']**2/4
    aperture=np.pi*p['aperture_diameter_m']**2/4
    if aperture>p['die_area_m2']:raise ValueError('Aperture exceeds die area')
    rr=p['lead_resistivity_ohm_m']*p['lead_length_m']/aw
    return {
        'device':p['device_power_W'],
        'supports':conduct(p['support_material'],tc,ta,p['support_width_m']*p['support_thickness_m'],p['support_length_m'],p['support_count'],p.get('support_k_scale',1)),
        'leads':conduct(p['lead_material'],td,ta,aw,p['lead_length_m'],p['lead_count'],p.get('lead_k_scale',1)),
        'lead_joule':p['lead_count']*p['lead_current_A']**2*rr,
        'stage_radiation':SIGMA*p['stage_area_m2']*p['stage_emissivity']*(ta**4-tc**4),
        'die_radiation':SIGMA*(p['die_area_m2']-aperture)*p['die_emissivity']*(ta**4-td**4),
        'optical':SIGMA*aperture*p['optical_gray_factor']*(ta**4-td**4),
        'gas':p['gas_conductance_W_K']*(ta-tc)
    }

def die_heat(q):return sum(q[k] for k in ['device','leads','lead_joule','die_radiation','optical'])

def detector(tc,p):
    if p['interface_K_W']==0:return tc
    return brentq(lambda td:td-tc-p['interface_K_W']*die_heat(heat_loads(tc,td,p)),tc,299.9)

def equilibrium(p,c=None):
    c=c or ScreenCapacity()
    if p['ambient_K']!=295:raise ValueError('Capacity experiment requires 295 K ambient')
    def residual(tc):return c(tc)-sum(heat_loads(tc,detector(tc,p),p).values())
    if residual(c.minimum)>0:return {'status':'below_measured_branch'}
    if residual(c.maximum)<0:return {'status':'above_measured_branch'}
    tc=brentq(residual,c.minimum,c.maximum,xtol=1e-10);td=detector(tc,p)
    q=heat_loads(tc,td,p)
    return {'status':'equilibrium','platform_K':tc,'detector_K':td,'loads_W':q,
        'energy_residual_W':residual(tc),'interface_residual_K':td-tc-p['interface_K_W']*die_heat(q),
        'meets_target':td<=p['target_K']}

def max_power(p,c=None):
    """Solve the target boundary directly, without nested power/temperature solves."""
    c=c or ScreenCapacity();td=p['target_K'];r=p['interface_K_W']
    zero={**p,'device_power_W':0}
    if not c.minimum<=td<=c.maximum:raise ValueError('Target outside measured domain')
    if r==0:return max(0,c(td)-sum(heat_loads(td,td,zero).values())) if c(td)>=sum(heat_loads(td,td,zero).values()) else None
    # At a fixed Td, all die-side parasitic loads are independent of Tc.
    parasitic=die_heat(heat_loads(td,td,zero))
    def power(tc):return (td-tc)/r-parasitic
    def residual(tc):return c(tc)-sum(heat_loads(tc,td,{**p,'device_power_W':power(tc)}).values())
    upper=td-r*parasitic  # zero device power
    if upper<c.minimum:return None
    if residual(upper)<0:return None
    if residual(c.minimum)>0:raise ValueError('Target boundary below measured branch')
    tc=brentq(residual,c.minimum,upper,xtol=1e-10)
    return max(0,power(tc))

def constraints(p):
    n=p['support_count'];w=p['support_width_m'];t=p['support_thickness_m'];l=p['support_length_m']
    force=p['payload_mass_kg']*p['acceleration_m_s2'];moment=w*t**3/12
    stiffness=n*3*p['young_modulus_Pa']*moment/l**3
    deflection=force/stiffness;stress=6*(force/n)*l/(w*t*t)
    resistance=p['lead_resistivity_ohm_m']*p['lead_length_m']/(np.pi*p['lead_diameter_m']**2/4)
    return {'deflection_um':deflection*1e6,'stress_MPa':stress/1e6,'lead_resistance_ohm':resistance,
        'stiffness_N_m':stiffness,'mechanical_pass':deflection<=p['max_deflection_m'] and stress<=p['screen_stress_limit_Pa'],
        'electrical_pass':resistance<=p['max_lead_resistance_ohm'],
        'combined_pass':deflection<=p['max_deflection_m'] and stress<=p['screen_stress_limit_Pa'] and resistance<=p['max_lead_resistance_ohm']}
