"""Conservative 1D nitrogen exchanger, wall and insulation screening model.

Cell-centred wall/insulation, nodal streams, exponential local heat exchange.
Only single-phase low-pressure return is supported; prescribed pressure/flow.
Conductances are scenario inputs, not fitted microchannel correlations.
"""
from dataclasses import dataclass, asdict, replace
import numpy as np
from scipy.optimize import root
from CoolProp.CoolProp import PropsSI


@dataclass(frozen=True)
class HX:
    cells: int = 32
    ambient_K: float = 295.
    high_Pa: float = 11.1e6
    high_drop_Pa: float = 50e3
    low_out_Pa: float = .24e6
    low_drop_Pa: float = 45e3
    gas_wall_W_K: float = 1.0  # total conductance on EACH gas side, assumed
    insulation_contact_W_K: float = .003  # integrated wall-to-MLI coupling, assumed
    axial_W_K: float = (0.0095*.0013-2*.00813*40e-6)/.042  # assumed glass k=1
    radiation_area_m2: float = 2*.042*.0095
    emissivity: float = .15
    cold_area_m2: float = 2*.0095**2
    cold_emissivity: float = .15
    fluid_platform_K_W: float = 0.  # ideal contact baseline; finite-contact sensitivity separate


def solve_hx(platform_K, mass_flow_kg_s, c=HX()):
    n=c.cells; ta=c.ambient_K; tc=platform_K; m=mass_flow_kg_s
    if n<4 or n!=int(n) or m<=0 or not 0<tc<ta:
        raise ValueError('Invalid mesh, mass flow or temperatures')
    if min(c.gas_wall_W_K,c.insulation_contact_W_K)<=0 or c.axial_W_K<0:
        raise ValueError('Positive coupling and nonnegative axial conductance required')
    x=np.linspace(0,1,n+1)
    ph=c.high_Pa-c.high_drop_Pa*x; pl=c.low_out_Pa+c.low_drop_Pa*x
    if ph.min()<=pl.max():raise ValueError('No pressure head')
    sat=np.asarray(PropsSI('T','P',pl,'Q',1,'Nitrogen'))
    lower=float(sat.max()+.05)
    if tc<110:raise ValueError('Declared validation scope is platform >=110 K; wet-return branch excluded')
    sigma=5.670374419e-8; g=c.gas_wall_W_K/n; gi=c.insulation_contact_W_K/n
    ka=c.axial_W_K*n
    def evaluate(z,record=False):
        th=np.r_[ta,z[:n]];tl=z[n:2*n+1]
        tw=z[2*n+1:3*n+1];ts=z[3*n+1:4*n+1]
        # Reject phase-ambiguous property calls during nonlinear iterations.
        if min(tl)<lower-20 or min(th)<65 or max(th)>500 or max(tl)>500:
            raise ValueError('Nonlinear iterate outside property bounds')
        hh=np.asarray(PropsSI('Hmass','P',ph,'T',th,'Nitrogen'))
        hl=np.asarray(PropsSI('Hmass','P',pl,'T',tl,'Nitrogen'))
        # Exact for a constant-cp fluid exchanging with an isothermal cell wall;
        # use local mean cp for real fluid, while enthalpy balances stay exact.
        cph=np.asarray(PropsSI('Cpmass','P',(ph[:-1]+ph[1:])/2,'T',(th[:-1]+th[1:])/2,'Nitrogen'))
        cpl=np.asarray(PropsSI('Cpmass','P',(pl[:-1]+pl[1:])/2,'T',(tl[:-1]+tl[1:])/2,'Nitrogen'))
        qh=m*cph*(th[:-1]-tw)*(-np.expm1(-g/(m*cph)))
        ql=m*cpl*(tw-tl[1:])*(-np.expm1(-g/(m*cpl)))
        qi=gi*(ts-tw)
        qr=c.emissivity*sigma*c.radiation_area_m2/n*(ta**4-ts**4)
        # Positive end fluxes: warm reservoir -> wall, wall -> cold platform.
        warm=2*ka*(ta-tw[0]);cold=2*ka*(tw[-1]-tc)
        edge=ka*(tw[:-1]-tw[1:])
        axial=np.r_[warm,edge]-np.r_[edge,cold]
        gross=m*(hl[-1]-hh[-1])
        residual=np.r_[m*(hh[:-1]-hh[1:])-qh,
                       m*(hl[:-1]-hl[1:])-ql,
                       qh-ql+qi+axial,qr-qi,
                       .01*(tc-tl[-1]-c.fluid_platform_K_W*gross)]
        if not record:return residual
        cold_rad=c.cold_emissivity*sigma*c.cold_area_m2*(ta**4-tc**4)
        net=gross-cold_rad-cold
        return dict(config=asdict(c),platform_K=tc,mass_flow_kg_s=m,
                    net_W=float(net),gross_cold_W=float(gross),cold_radiation_W=cold_rad,
                    hx_radiation_W=float(qr.sum()),warm_anchor_W=float(warm),cold_anchor_W=float(cold),
                    energy_residual_W=float(m*(hl[0]-hh[0])-net-cold_rad-qr.sum()-warm),
                    max_cell_residual_W=float(np.max(np.abs(residual[:-1]))),
                    interface_residual_K=float(residual[-1]/.01),
                    return_superheat_min_K=float(np.min(tl-sat)),
                    minimum_high_minus_low_K=float(np.min(th-tl)),
                    after_valve_quality=float(PropsSI('Q','P',pl[-1],'Hmass',hh[-1],'Nitrogen')),
                    x=x.tolist(),high_K=th.tolist(),low_K=tl.tolist(),wall_K=tw.tolist(),insulation_K=ts.tolist())
    th=np.linspace(ta,tc+2,n+1);tl=np.linspace(ta-2,tc-5,n+1)
    tw=(th[:-1]+th[1:]+tl[:-1]+tl[1:])/4
    initial=np.r_[th[1:],tl,tw,(tw+ta)/2]
    try:
        ans=root(evaluate,initial,method='hybr',options={'xtol':1e-8})
    except ValueError:
        ans=None
    # A resolved lower-mesh solution is a continuation initial guess, not data fitting.
    if (ans is None or not ans.success) and n>=16:
        coarse=solve_hx(tc,m,replace(c,cells=n//2))
        xc=np.asarray(coarse['x']);mc=(xc[:-1]+xc[1:])/2;mid=(x[:-1]+x[1:])/2
        guess=np.r_[np.interp(x[1:],xc,coarse['high_K']),np.interp(x,xc,coarse['low_K']),
                    np.interp(mid,mc,coarse['wall_K']),np.interp(mid,mc,coarse['insulation_K'])]
        ans=root(evaluate,guess,method='hybr',options={'xtol':1e-8})
    if ans is None:raise ValueError('Nonlinear solve left allowed property domain')
    r=evaluate(ans.x,True)
    if not ans.success or r['max_cell_residual_W']>1e-7 or abs(r['interface_residual_K'])>1e-5:
        raise RuntimeError(f'Exchanger did not converge: {ans.message}; residual {r["max_cell_residual_W"]}')
    if r['return_superheat_min_K']<=.05:
        raise ValueError('Return leaves the declared single-phase vapor domain')
    if min(r['high_K']+r['low_K']+r['wall_K']+r['insulation_K'])<lower or max(r['high_K']+r['low_K']+r['wall_K']+r['insulation_K'])>ta+1e-5:
        raise ValueError('Temperature bounds violated')
    r['success']=True
    return r
