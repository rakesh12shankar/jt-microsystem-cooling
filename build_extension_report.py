"""Assemble extension findings from saved numerical outputs, without refitting."""
import json,re
import numpy as np
from CoolProp.CoolProp import PropsSI
from model import ROOT


def main():
    out=ROOT/'results/extensions'
    h=json.loads((out/'distributed_hx.json').read_text(encoding='utf-8'))
    b=json.loads((out/'bond_defects.json').read_text(encoding='utf-8'))
    hr=[r for r in h['cases'] if r['T_K']==130 and r['status']=='converged_vapor']
    central=next(r for r in hr if r['gas_wall_W_K']==1 and r['insulation_contact_W_K']==.003)
    def label(s):return s.replace('square','patch').replace('_',' ')
    br=[r for r in b['scenarios'] if r['condition']=='adverse']
    intact=next(r for r in br if r['actual_fraction']==0)
    quarter=next(r for r in br if r['shape']=='center_square' and r['requested_fraction']==.25)
    edge=next(r for r in br if r['shape']=='edge_strip' and r['requested_fraction']==.5)
    mesh=h['mesh'];bm=b['mesh_25percent'];fine=mesh[-1]
    table='\n'.join(f"| {label(r['shape'])} | {100*r['actual_fraction']:.2f} | {r['power_limit_mW']:.2f} | {r['peak_at10mW_K']:.3f} | {r['nonuniformity_at10mW_K']:.3f} |" for r in br)
    htable='\n'.join(f"| {r['gas_wall_W_K']:g} | {r['insulation_contact_W_K']:g} | {r['predicted_mW']:.2f} | {r['hx_radiation_mW']:.2f} | {r['cold_anchor_mW']:.1f} |" for r in hr)
    mtable='\n'.join(f"| {r['config']['cells']} | {1000*r['net_W']:.3f} | {1000*r['hx_radiation_W']:.3f} | {1000*r['cold_anchor_W']:.2f} |" for r in mesh)
    btable='\n'.join(f"| {r['level']} | {r['nodes']} | {r['actual_fraction']*100:.2f} | {r['power_limit_mW']:.4f} | {r['peak_at10mW_K']:.4f} |" for r in bm)
    usable=[r['power_mW'] for r in h['package_130K_mean_screen'] if r.get('power_mW') is not None]
    corner=h['corner_mesh'];cornerdiff=max(abs(corner[i+1]['net_mW']-corner[i]['net_mW']) for i in range(0,len(corner),2))
    # Independent whole-device entropy screen of saved profiles; reservoir heat at Ta/Tc.
    entropy=[]
    for r in h['profiles_at130K']:
        c=r['config'];ta=c['ambient_K'];m=r['mass_flow_kg_s'];tc=r['platform_K']
        sin=PropsSI('Smass','T',ta,'P',c['high_Pa'],'Nitrogen')
        sout=PropsSI('Smass','T',r['low_K'][0],'P',c['low_out_Pa'],'Nitrogen')
        sg=m*(sout-sin)-r['net_W']/tc-(r['hx_radiation_W']+r['cold_radiation_W']+r['warm_anchor_W'])/ta
        entropy.append(sg)
    if min(entropy)<-1e-8:raise RuntimeError('Negative whole-device entropy generation')
    checks=dict(minimum_whole_device_entropy_generation_W_K=min(entropy),
                maximum_hx_global_energy_residual_W=max(abs(r['energy_residual_W']) for r in h['cases'] if r['status']=='converged_vapor'),
                maximum_bond_FE_energy_residual_per_W=max(r['FE_energy_residual_per_W'] for r in b['scenarios']),
                hx_central_128_to256_capacity_difference_mW=1000*abs(mesh[-1]['net_W']-mesh[-2]['net_W']),
                hx_corner_max_128_to256_difference_mW=cornerdiff,
                bond_level8_to12_power_difference_mW=abs(bm[-1]['power_limit_mW']-bm[-2]['power_limit_mW']))
    (out/'verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    text=f'''# Extension studies: exchanger physics and bond defects

## Main findings

1. **Bond quality can consume the remaining design margin.** For the selected
   package under the existing adverse assumptions, intact allowable power is
   **{intact['power_limit_mW']:.2f} mW**. A25% central degraded patch lowers it to
   **{quarter['power_limit_mW']:.2f} mW**; a50% edge strip lowers it to
   **{edge['power_limit_mW']:.2f} mW**, failing the10 mW requirement.
2. **Solving temperatures changes the exchanger loss estimate, but does not
   establish model adequacy.** At130 K, the central distributed scenario predicts
   **{central['predicted_mW']:.2f} mW** net capacity on128 cells, compared with121.9 mW
   in Qi's manually read measurement. Refining to256 cells gives
   **{fine['net_W']*1000:.2f} mW**. Its large computed wall heat into the cold platform
   is an unresolved internal-budget discrepancy, despite a close net result.
3. The exchanger extension is deliberately restricted to vapor return at
   platform temperatures110–153 K. It **does not update the original100 K rating**.
   All heat-transfer conductances are stated scenarios, not calibrated measurements.

Methods and source/assumption definitions: [extension methods](../../docs/extension_methods.md).

## A. Distributed exchanger and insulation

The model solves high-pressure gas, return gas, glass wall and insulation
temperatures, including wall conduction and explicit warm/cold wall anchors.
Unlike the original imposed linear radiation profile, insulation temperature is
found from radiation input and thermal coupling to the wall. Flow remains
prescribed from Qi at each temperature. There is no hydraulic closure or
two-phase exchanger correlation, and no new fitting to measured capacity.

### Constitutive screen at130 K

Gg is total conductance on each gas side; Gi is total wall-to-insulation conductance.

| Gg W/K | Gi W/K | Predicted net mW | Exchanger radiation mW | Wall → cold platform mW |
|---:|---:|---:|---:|---:|
{htable}

The scenario spread is **{min(r['predicted_mW'] for r in hr):.1f}–{max(r['predicted_mW'] for r in hr):.1f} mW**,
not a probability interval. The insulation radiation range is
**{min(r['hx_radiation_mW'] for r in hr):.1f}–{max(r['hx_radiation_mW'] for r in hr):.1f} mW**.
Comparison across all five eligible points is saved in `distributed_hx.csv`.
These are conditional comparisons using measured flow, not independent validation.

![Exchanger scenarios and solved temperature profiles](distributed_hx.png)

### Mesh resolution and physical adequacy

| Cells | Net mW | Exchanger radiation mW | Wall → cold platform mW |
|---:|---:|---:|---:|
{mtable}

The central128-to256-cell net change is **{checks['hx_central_128_to256_capacity_difference_mW']:.3f} mW**.
The largest change at the three additionally checked scenario corners is
**{cornerdiff:.3f} mW**. This is a numerical resolution check at130 K, not a uniform
error bound for all temperatures or conductances. Cold-anchor heat converges
more slowly and is reported rather than hidden by the net balance.

**Do not interpret the net agreement as a validated correction.** The assumed
continuous glass cross-section, shared wall, thermal anchors and film conductances
produce hundreds of milliwatts of wall heat entering the cold platform. That
behavior is in tension with the below2 mW axial-loss scale reported in Qi's
model diagnostics and used in Pei's supplementary accounting. The heat-flow
definitions and hardware boundaries need reconciliation before treating these
as directly identical quantities. It nevertheless prevents claiming that the
internal physics has been validated by a matching net capacity.

The model conserves energy, but large internal heat circulation can cancel in
the net result. All saved130 K profiles pass an independent whole-device entropy
screen (minimum **{min(entropy):.3g} W/K**). Conservation and a nonnegative entropy
balance are necessary checks, not proof that the assumed thermal paths represent
the real cooler. No scenario is promoted to a replacement reference curve.

The finite-contact screen reports successful vapor solutions and rejected
nonlinear cases separately. Rejection at110 K with nonzero contact resistance
is not proof of physical infeasibility; it may require a wet-return formulation
or a more robust solver. Extending below110 K by interpolation is disallowed.

### Propagation to an illustrative package target

Using the selected package at a separate **130 K mean-die** target produces
**{min(usable):.1f}–{max(usable):.1f} mW** useful power across these scenarios.
This demonstrates how unresolved cooler physics affects a package calculation.
It is not the100 K peak-temperature requirement, not a new infrared performance
specification, and not a validated rating. All interpolations stay within110–153 K.

## B. Bond-defect sensitivity of the selected package

The thermal bond contains an imposed low-conductivity region, set to10^-4 of
intact effective conductivity. It is a poor-contact surrogate, not a measured
vacuum void or a crack-growth model. Central/corner patches are rectangular,
with the same6:5 aspect ratio as the die. The actual meshed area is shown below.

Each defect geometry has separate uniform and localized1 W FE load bases. Their
full temperature fields and area means are recombined inside the nonlinear
package solve. The intact scalar interface resistance is not reused for a
defective bond, and separate maxima are not added together.

### Adverse-condition results at the original100 K peak limit

| Defect footprint | Actual area % | Allowable power mW | Peak at10 mW K | Peak-to-minimum at10 mW K |
|---|---:|---:|---:|---:|
{table}

![Bond defects and useful-power limits](bond_defect_limits.png)

![Die temperature fields at10 mW under adverse assumptions](bond_defect_fields.png)

Small central defects directly beneath the heat source are more harmful than
some equally sized edge defects, but the ordering changes for large regions.
A large edge strip forces substantial lateral spreading through the die and
can move the hottest point away from the imposed central source. Therefore,
defect area alone is not a sufficient thermal acceptance measure.

At25% area, all four tested shapes still meet10 mW, with reduced margin. At
approximately50%, all four fail under the adverse assumptions. This is a result
for sampled shapes and area fractions, not a precise allowable-void threshold.
Nominal results and all26 primary cases are saved in `bond_defects.csv`.

### Mesh and conductivity sensitivity

The convergence case has an exactly25% centered rectangle on each mesh:

| Mesh level | Nodes | Actual area % | Allowable power mW | Peak at10 mW K |
|---:|---:|---:|---:|---:|
{btable}

The level8-to12 power change is **{checks['bond_level8_to12_power_difference_mW']:.4f} mW**.
The intact FE solution and allowable-power calculation recover the earlier model;
a uniformly degraded whole bond recovers analytical layered resistance.
The maximum1 W basis energy residual across the primary cases is
**{checks['maximum_bond_FE_energy_residual_per_W']:.2g} W/W**.

For the25% central patch, changing the defect conductivity ratio from10^-4 to0.1
gives allowable power from **{b['severity_25percent'][0]['power_limit_mW']:.3f} to
{b['severity_25percent'][-1]['power_limit_mW']:.3f} mW**. All are assumptions about
thermal contact. Defect morphology, gap gas/radiation and interface measurements
would be needed to connect this screen to manufacturing acceptance criteria.
Bond stress redistribution and reliability are not established by this thermal study.

## What this adds to the project

The contribution is now stronger than an ideal-bond geometry search: it tests
whether the candidate survives spatial interface defects and shows why a good
net-capacity fit is insufficient evidence for a distributed cooler model.
The43-test suite covers both extensions alongside the original studies.
Remaining experimental gaps are explicit; neither extension is presented as
an independently validated manufactured design.

Reproduce using the commands in [extension methods](../../docs/extension_methods.md).
The original baseline configurations and results remain available for comparison.
'''
    text=re.sub(r'\b(a|A|at|the|all|above|below|from|to|of|with|than|exactly|on|and|for|about|level|levels|case|cells)(?=\d)',r'\1 ',text)
    text=re.sub(r'(?<=\d)(K|mW|W|mg|mm|cells|tests)\b',r' \1',text)
    (out/'report.md').write_text(text,encoding='utf-8')
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
