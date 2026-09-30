"""Two-node incremental package model, SI units throughout.

The measured Qi silicon chip is the reference platform. A new detector connects
through an ADDITIONAL interface. Only extra package heat paths are modeled.
This is a measured-performance model, not a first-principles JT cycle solver.
"""
from dataclasses import dataclass, fields, replace
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parent
SIGMA = 5.670374419e-8

@dataclass(frozen=True)
class Package:
    ambient_K: float = 295
    target_K: float = 100
    device_power_W: float = .01
    interface_K_per_W: float = 50
    support_W_per_K: float = 50e-6
    lead_W_per_K: float = 20e-6
    stage_area_m2: float = 1e-4
    stage_emissivity: float = .05
    device_area_m2: float = 9e-6
    device_emissivity: float = .2
    gas_W_per_K: float = 0
    optical_W: float = 0

    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            if not np.isfinite(v) or v < 0:
                raise ValueError(f"Invalid {f.name}: {v}")
        if not 0 < self.target_K < self.ambient_K:
            raise ValueError("Require 0 < target < ambient")
        if max(self.stage_emissivity, self.device_emissivity) > 1:
            raise ValueError("Emissivity must not exceed one")

    @classmethod
    def load(cls, path=ROOT / 'config/baseline.json'):
        data = json.loads(Path(path).read_text())
        return cls(**{f.name:data[f.name] for f in fields(cls) if f.name in data})

class Capacity:
    def __init__(self, path=ROOT / 'data/qi2023_capacity.json', scale=1.):
        self.source = json.loads(Path(path).read_text())
        self.T = np.array([p['T_K'] for p in self.source['points']])
        self.Q = np.array([p['Q_mW'] for p in self.source['points']]) * .001
        if not np.isfinite(scale) or scale <= 0:
            raise ValueError('Capacity scale must be positive')
        self.scale = scale
        self.minimum, self.maximum = float(self.T[0]), float(self.T[-1])

    def __call__(self, t):
        if np.any(np.asarray(t) < self.minimum) or np.any(np.asarray(t) > self.maximum):
            raise ValueError('Temperature outside measured branch; extrapolation forbidden')
        return np.interp(t, self.T, self.Q) * self.scale

def radiation(area, emissivity, hot, cold):
    return SIGMA * area * emissivity * (hot**4 - cold**4)

def loads(tc, td, p):
    """Extra heat loads; existing experimental losses are NOT repeated."""
    return {
        'device': p.device_power_W,
        'leads_to_device': p.lead_W_per_K * (p.ambient_K - td),
        'radiation_to_device': radiation(p.device_area_m2,p.device_emissivity,p.ambient_K,td),
        'optical_to_device': p.optical_W,
        'supports_to_platform': p.support_W_per_K * (p.ambient_K - tc),
        'radiation_to_platform': radiation(p.stage_area_m2,p.stage_emissivity,p.ambient_K,tc),
        'residual_gas_to_platform': p.gas_W_per_K * (p.ambient_K - tc)
    }

def device_heat(td, p):
    return (p.device_power_W + p.optical_W + p.lead_W_per_K*(p.ambient_K-td)
            + radiation(p.device_area_m2,p.device_emissivity,p.ambient_K,td))

def detector_temperature(tc, p):
    if p.interface_K_per_W == 0:
        return tc
    def residual(td):
        return td-tc-p.interface_K_per_W*device_heat(td,p)
    upper = p.ambient_K+p.interface_K_per_W*(p.device_power_W+p.optical_W)+1
    return brentq(residual,tc,upper,xtol=1e-11)

def solve(p, capacity=None):
    c = capacity or Capacity()
    if p.ambient_K != 295:
        raise ValueError('Measured capacity only applies at ambient 295 K')
    def residual(tc):
        td=detector_temperature(tc,p)
        return float(c(tc))-sum(loads(tc,td,p).values())
    lo,hi=c.minimum,c.maximum
    if residual(lo)>1e-10 or residual(hi)<-1e-10:
        return {'status':'no_equilibrium_in_modeled_branch','meets_target':False}
    tc=brentq(residual,lo,hi,xtol=1e-10)
    td=detector_temperature(tc,p)
    heat=loads(tc,td,p)
    return {'status':'equilibrium','platform_K':tc,'detector_K':td,
            'capacity_W':float(c(tc)),'loads_W':heat,
            'energy_residual_W':residual(tc),
            'interface_residual_K':td-tc-p.interface_K_per_W*device_heat(td,p),
            'meets_target':bool(td<=p.target_K)}

def maximum_device_power(p, capacity=None):
    """Maximum device dissipation satisfying target on this monotone branch."""
    c=capacity or Capacity()
    base=solve(replace(p,device_power_W=0),c)
    if not base['meets_target']:
        return None  # even zero device dissipation cannot meet target
    def feasible(power):
        r=solve(replace(p,device_power_W=power),c)
        return r.get('detector_K',p.target_K+100)-p.target_K
    return brentq(feasible,0,float(c(c.maximum)),xtol=1e-10)
