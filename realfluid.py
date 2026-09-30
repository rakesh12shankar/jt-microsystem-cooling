"""Steady real-fluid nitrogen JT cycle and package coupling (milestone 3).

Enthalpy-based recuperator with sampled internal pinch checks; ideal isenthalpic
valve; prescribed mass flow and pressure drops. Cold-return enthalpy is the
unknown, allowing a wet return at saturation rather than forcing a vapor state.
No measured cooling-capacity values are used by this model.
"""
from dataclasses import dataclass,fields
import json
import numpy as np
from CoolProp.CoolProp import PropsSI
from scipy.integrate import quad
from scipy.optimize import brentq
from model import ROOT,SIGMA,Package,detector_temperature,loads

@dataclass(frozen=True)
class Cycle:
    fluid: str = 'Nitrogen'
    ambient_K: float = 295
    high_pressure_Pa: float = 11.1e6
    outlet_pressure_Pa: float = .24e6
    high_drop_Pa: float = 50e3
    low_drop_Pa: float = 45e3
    mass_flow_kg_s: float = 4.2e-6
    effectiveness: float = .995
    hx_radiation_area_m2: float = 2*.042*.0095
    reference_cold_area_m2: float = 2*.0095**2
    reference_emissivity: float = .15
    reference_axial_W_K: float = 5e-6
    fluid_to_platform_K_W: float = 100
    pinch_nodes: int = 81

    def __post_init__(self):
        if self.fluid != 'Nitrogen': raise ValueError('Only nitrogen supported by this case study')
        vals=[getattr(self,f.name) for f in fields(self) if f.name!='fluid']
        if any(not np.isfinite(v) or v<0 for v in vals): raise ValueError('Inputs must be finite and nonnegative')
        if self.mass_flow_kg_s<=0 or self.outlet_pressure_Pa<=0: raise ValueError('Flow and outlet pressure must be positive')
        if self.high_pressure_Pa-self.high_drop_Pa<=self.evaporator_Pa: raise ValueError('No pressure head left for restriction')
        if not 0<=self.effectiveness<=1 or not 0<=self.reference_emissivity<=1: raise ValueError('Effectiveness and emissivity must lie in [0,1]')
        if self.pinch_nodes<5 or not isinstance(self.pinch_nodes,int): raise ValueError('At least 5 integer pinch nodes required')
        # Ensure a subcritical low-pressure two-phase domain exists.
        if self.evaporator_Pa>=PropsSI('pcrit',self.fluid): raise ValueError('Evaporator must be subcritical')
        if self.ambient_K<=self.saturation_K: raise ValueError('Ambient must exceed evaporator saturation temperature')

    @property
    def evaporator_Pa(self):return self.outlet_pressure_Pa+self.low_drop_Pa
    @property
    def saturation_K(self):return float(PropsSI('T','P',self.evaporator_Pa,'Q',0,self.fluid))

    @classmethod
    def load(cls,path=ROOT/'config/realfluid.json'):
        d=json.loads(path.read_text());return cls(**{f.name:d[f.name] for f in fields(cls) if f.name in d})

def state(p,h,c):
    return {'pressure_Pa':float(p),'enthalpy_J_kg':float(h),
        'temperature_K':float(PropsSI('T','P',p,'Hmass',h,c.fluid)),
        'quality':float(PropsSI('Q','P',p,'Hmass',h,c.fluid))}

def hx_radiation(tc,c):
    # Linear assumed wall profile between fluid cold end and ambient.
    # Integral_0^1 T(x)^4 dx = (Ta^4+Ta^3Tc+...+Tc^4)/5.
    ta=c.ambient_K
    mean_t4=sum(ta**(4-i)*tc**i for i in range(5))/5
    return SIGMA*c.reference_emissivity*c.hx_radiation_area_m2*(ta**4-mean_t4)

def evaluate(hreturn,c=Cycle()):
    """Return state and energy records at a given evaporator outlet enthalpy."""
    m=c.mass_flow_kg_s; pe=c.evaporator_Pa; phc=c.high_pressure_Pa-c.high_drop_Pa
    cold=state(pe,hreturn,c);tc=cold['temperature_K']
    if tc>c.ambient_K:raise ValueError('Cold return is warmer than ambient')
    h1=float(PropsSI('Hmass','P',c.high_pressure_Pa,'T',c.ambient_K,c.fluid))
    qr=hx_radiation(tc,c)
    # Endpoint bounds on heat transferred from high-pressure to low-pressure stream.
    h_h_cold=float(PropsSI('Hmass','P',phc,'T',tc,c.fluid))
    h_l_warm=float(PropsSI('Hmass','P',c.outlet_pressure_Pa,'T',c.ambient_K,c.fluid))
    upper=min(m*(h1-h_h_cold),m*(h_l_warm-hreturn)-qr)
    if upper<0:raise ValueError('Radiation alone exceeds available return-stream heat uptake')
    x=np.linspace(0,1,c.pinch_nodes)
    ph=c.high_pressure_Pa-c.high_drop_Pa*x
    pl=c.outlet_pressure_Pa+c.low_drop_Pa*x
    def profile(q):
        hh=h1-q*x/m
        hl=hreturn+(q+qr)*(1-x)/m
        th=np.asarray(PropsSI('T','P',ph,'Hmass',hh,c.fluid))
        tl=np.asarray(PropsSI('T','P',pl,'Hmass',hl,c.fluid))
        return th,tl,hh,hl
    def pinch(q):
        th,tl,_,_=profile(q);return float(np.min(th-tl))
    if pinch(0)<-1e-7:raise ValueError('No feasible recuperator state at zero transfer')
    if pinch(upper)>=-1e-7:qmax=upper
    else:qmax=brentq(pinch,0,upper,xtol=1e-12)
    q=c.effectiveness*qmax
    th,tl,hh,hl=profile(q)
    h2=h1-q/m;h3=h2;h5=hreturn+(q+qr)/m
    gross=m*(hreturn-h3)
    platform=tc+c.fluid_to_platform_K_W*gross
    reference_radiation=SIGMA*c.reference_emissivity*c.reference_cold_area_m2*(c.ambient_K**4-platform**4)
    axial=c.reference_axial_W_K*(c.ambient_K-platform)
    net=gross-reference_radiation-axial
    return {'states':{'1_warm_high_in':state(c.high_pressure_Pa,h1,c),
        '2_cold_high_before_valve':state(phc,h2,c),
        '3_after_valve':state(pe,h3,c),'4_evaporator_return':cold,
        '5_warm_low_out':state(c.outlet_pressure_Pa,h5,c)},
        'platform_K':float(platform),'gross_cold_W':float(gross),'net_external_W':float(net),
        'recuperator_transfer_W':float(q),'maximum_transfer_W':float(qmax),
        'hx_radiation_W':float(qr),'cold_reference_radiation_W':float(reference_radiation),
        'reference_axial_W':float(axial),'pinch_K':float(np.min(th-tl)),
        'hx_energy_residual_W':float(m*(h5-hreturn)-m*(h1-h2)-qr),
        'cycle_energy_residual_W':float(m*(h5-h1)-gross-qr),
        'valve_enthalpy_residual_J_kg':float(h3-h2),
        'valve_entropy_generation_W_K':float(m*(PropsSI('Smass','P',pe,'Hmass',h3,c.fluid)-PropsSI('Smass','P',phc,'Hmass',h2,c.fluid))),
        'profile':{'x_warm_to_cold':x.tolist(),'high_K':th.tolist(),'low_K':tl.tolist()}}

def solve_package(p=None,c=None):
    p=p or Package.load();c=c or Cycle.load()
    if abs(p.ambient_K-c.ambient_K)>1e-9:raise ValueError('Package and cycle ambient temperatures differ')
    hl=float(PropsSI('Hmass','P',c.evaporator_Pa,'Q',0,c.fluid))
    hv=float(PropsSI('Hmass','P',c.evaporator_Pa,'Q',1,c.fluid))
    # Covers wet return through single-phase return up to 160 K.
    high=float(PropsSI('Hmass','P',c.evaporator_Pa,'T',min(160,c.ambient_K-1),c.fluid))
    def residual(h):
        r=evaluate(h,c);tp=r['platform_K'];td=detector_temperature(tp,p)
        return r['net_external_W']-sum(loads(tp,td,p).values())
    # State may become infeasible near ambient; never silently bridge an invalid interval.
    grid=np.unique(np.r_[np.linspace(hl,hv,17),np.linspace(hv,high,17)])
    roots=[];prev=None
    for h in grid:
        try:f=residual(h)
        except ValueError:prev=None;continue
        if abs(f)<1e-10:roots.append(float(h))
        elif prev is not None and f*prev[1]<0:
            roots.append(float(brentq(residual,prev[0],h,xtol=1e-6)))
        prev=(h,f)
    if not roots:return {'status':'no_equilibrium_in_search_domain','meets_target':False}
    h=min(roots);r=evaluate(h,c)
    td=detector_temperature(r['platform_K'],p);qload=loads(r['platform_K'],td,p)
    r.update({'status':'equilibrium','detector_K':float(td),'package_loads_W':qload,
        'package_energy_residual_W':float(r['net_external_W']-sum(qload.values())),
        'meets_target':bool(td<=p.target_K),'roots_found':len(roots),
        'selection':'lowest return-enthalpy equilibrium; dynamic stability not established'})
    if r['gross_cold_W']<0 or r['pinch_K']<-1e-6:raise RuntimeError('Nonphysical equilibrium')
    return r

def slit_flow_diagnostic(temperature_K,c=None):
    """Qi Eq. A1, 14 slits, isothermal equilibrium phases; not a choked-flow model.

    This diagnostic does not set the cycle flow. Density/viscosity jump at
    saturation is integrated piecewise; no two-phase viscosity is invented.
    """
    c=c or Cycle.load();lo=c.evaporator_Pa;hi=c.high_pressure_Pa-c.high_drop_Pa
    edges=[lo,hi]
    if PropsSI('Ttriple',c.fluid)<temperature_K<PropsSI('Tcrit',c.fluid):
        ps=float(PropsSI('P','T',temperature_K,'Q',0,c.fluid))
        if lo<ps<hi:edges.insert(1,ps)
    def integrand(p):return PropsSI('Dmass','P',p,'T',temperature_K,c.fluid)/PropsSI('V','P',p,'T',temperature_K,c.fluid)
    integral=sum(quad(integrand,a,b,epsrel=1e-6)[0] for a,b in zip(edges[:-1],edges[1:]))
    return 14*140e-6*(.7e-6)**3/(12*1e-3)*integral
