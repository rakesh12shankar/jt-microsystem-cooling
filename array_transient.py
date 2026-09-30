"""Local two-node passive response; cooler capacity is quasi-steady.

Not a cooldown, gas-dynamics or controlled-stage model. Heat capacities are
effective assumptions near the cold operating state, not room-temperature data.
"""
import numpy as np
from scipy.integrate import solve_ivp
from array_model import loads,die_heat,interface_R,solve
from packaging_model import ScreenCapacity

def simulate(p,power_start=.01,power_end=.015,duration=180,capacity_scale=1,rtol=1e-8):
    c=ScreenCapacity();r=interface_R(p)
    cp=p['thermal_capacitance_platform_J_K']*capacity_scale
    cd=p['thermal_capacitance_die_J_K']*capacity_scale
    if min(cp,cd)<=0:raise ValueError('Heat capacities must be positive')
    initial=solve({**p,'device_power_W':power_start});final=solve({**p,'device_power_W':power_end})
    if initial['status']!='equilibrium' or final['status']!='equilibrium':raise ValueError('Step endpoints outside measured branch')
    pp={**p,'device_power_W':power_end}
    def rhs(t,y):
        tc,td=y[:2];q=loads(tc,td,pp);qd=die_heat(q);qs=sum(q.values())-qd;qi=(td-tc)/r
        dc=(qs+qi-c(tc))/cp;dd=(qd-qi)/cd
        return [dc,dd,sum(q.values())-c(tc)]
    times=np.linspace(0,duration,int(duration*20)+1)
    y0=[initial['platform_K'],initial['die_K'],0]
    solution=solve_ivp(rhs,[0,duration],y0,method='Radau',t_eval=times,rtol=rtol,atol=rtol*.01,max_step=1)
    if not solution.success:raise RuntimeError(solution.message)
    delta=abs(final['die_K']-initial['die_K']);band=max(1e-7,.02*delta)
    outside=np.flatnonzero(np.abs(solution.y[1]-final['die_K'])>band)
    settling=None if len(outside) and outside[-1]==len(times)-1 else (float(times[outside[-1]+1]) if len(outside) else 0.)
    energy=cp*(solution.y[0]-y0[0])+cd*(solution.y[1]-y0[1])-solution.y[2]
    equilibrium_state=np.array([final['platform_K'],final['die_K'],0])
    jac=np.zeros((2,2));step=1e-4
    for j in range(2):
        e=np.zeros(3);e[j]=step
        jac[:,j]=(np.array(rhs(0,equilibrium_state+e))[:2]-np.array(rhs(0,equilibrium_state-e))[:2])/(2*step)
    eigen=np.linalg.eigvals(jac)
    return {'time_s':solution.t,'platform_K':solution.y[0],'die_K':solution.y[1],
        'initial':initial,'final':final,'settling_2percent_s':settling,
        'max_mean_die_K':float(max(solution.y[1])),'overshoot_above_final_K':float(max(0,max(solution.y[1])-final['die_K'])),
        'energy_residual_J':float(max(abs(energy))),'local_eigenvalues_per_s':eigen.tolist(),
        'time_constants_s':sorted((-1/eigen).tolist()),'capacity_scale':capacity_scale}
