"""Peak-temperature target and deterministic adverse-case definitions."""
from copy import deepcopy
from scipy.optimize import brentq
from array_model import loads,die_heat,interface_R
from packaging_model import ScreenCapacity

def adverse(p):
    q=deepcopy(p)
    q.update({'support_k_scale':1.2,'lead_k_scale':1.1,'contact_resistivity_m2K_W':2*p['contact_resistivity_m2K_W'],
        'stage_emissivity':2*p['stage_emissivity'],'die_emissivity':2*p['die_emissivity'],
        'gas_conductance_W_K':10e-6,'out_band_transmission':.03,
        'lead_resistivity_ohm_m':1.2*p['lead_resistivity_ohm_m'],'young_modulus_Pa':.7*p['young_modulus_Pa']})
    return q

def peak_power(p,beta,c=None):
    """beta [K/W] = FE peak-minus-area-mean per watt of localized heat.

    The assumed localized portion is 0.5*device power. Uniform parasitics do
    not contribute to the peak-minus-mean in this constant-property stack.
    """
    c=c or ScreenCapacity();r=interface_R(p);target=p['target_K']
    def state(power):
        td=target-beta*.5*power
        # Die-side loads independent of platform temperature.
        pp={**p,'device_power_W':power};tc=td-r*die_heat(loads(td,td,pp))
        return tc,td,pp
    tc0,td0,pp0=state(0)
    if tc0<c.minimum or c(tc0)<sum(loads(tc0,td0,pp0).values()):return None
    upper=brentq(lambda power:state(power)[0]-c.minimum,0,1)
    def fun(power):
        tc,td,pp=state(power)
        return c(max(c.minimum,tc))-sum(loads(tc,td,pp).values())
    if fun(upper)>0:raise ValueError('Peak boundary lies below capacity domain')
    return float(brentq(fun,0,upper,xtol=1e-11))
