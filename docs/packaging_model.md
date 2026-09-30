# Geometry-based package model — milestone 5

## Boundary and architecture

Qi's existing silicon chip is the platform Tc. An additional detector at Td
is attached through interface resistance R. The surrounding enclosure and warm
wire ends are at 295 K. Only added loads are modeled. The reference gas lines,
insulation, original chip, thermometer, glue and heat losses remain embedded
in the measured cooling-capacity curve. The cycle assumptions that failed
milestone 4 are not used to predict these package capacities.

All dimensions in `config/packaging.json` are candidate dimensions chosen for
this study, not copied prototype dimensions. A packaging drawing and assembly
clearance study are still required. The 3 mm support option extends outside the
3 mm detector footprint and requires space on/around the reference platform.
The prescribed contact resistance includes bonding and spreading effects as a
lumped parameter; material-specific interface resistance has not been measured.

## Governing equations

For n uniform support tabs or wires, without intermediate thermal intercepts:

```
Qcond = n A/L * integral[Tcold..295] k(T) dT
Qrad = sigma * epsilon * A * (295^4 - Tnode^4)
Qopt = sigma * Aaperture * fgray * (295^4 - Td^4)
Qgas = Ggas * (295 - Tc)
Rwire = rho * Lwire / Awire
QJoule,die = nwire * I^2 * Rwire
Td - Tc = Rinterface * (Pdevice + Qleads + QJoule + Qrad,die + Qopt)
Qmeasured(Tc) = sum(all added loads)
```

The gray aperture uses the full blackbody spectrum; it is a bounded engineering
scenario, not a prediction for a particular infrared detector band. The optical
factor combines effective transmission, absorptance and view factor. Aperture
area is removed from the opaque die area in its separate radiation term.
Surface and aperture exposure are idealized effective areas; optical baffles
and spectral filters require a more detailed model. Warm optical radiation is
not separately added again as an arbitrary device power.

The gas parameter does not map to pressure without species, gap, surface
accommodation and flow-regime information. A finite residual-gas load is
included without claiming a required vacuum pressure.

Conductivity is integrated by 32-point Gauss–Legendre quadrature. An independent
adaptive quadrature test checks the integral over the operating span. NIST
log-polynomial fits and applicability ranges are preserved in the material
data file; extrapolation is rejected. G10 warp-direction conductivity is used
along each tab. Specific laminate layup and cryogenic joints remain unspecified.

The leads are an exploratory 304 stainless low-current candidate. Their thermal
conductivity is sourced; their constant electrical resistivity is an explicit
assumption. All wire Joule heating is conservatively placed at the detector.
This neglects distributed wire heating and partition, so high-current cases
are screening cases rather than coupled electrothermal solutions.

## Mechanical/electrical screens

For equal-load cantilevers in out-of-plane bending:

```
Ibeam = width * thickness^3 / 12
Ktotal = n * 3 * E * Ibeam / length^3
deflection = payload_mass * acceleration / Ktotal
root_stress = 6 * (payload_mass * acceleration/n) * length / (width*thickness^2)
```

The assumed payload is 5 mg at 10 g; maximum deflection is 10 um and the
screening stress limit is 50 MPa. The payload must include all added supported
hardware in a real design. The existing cooler's own support is not modeled.
Assumed moduli are 20 GPa for G10 and 190 GPa for steel, with a -30% modulus
case included. These assumptions are not a source-backed laminate strength
allowable or a thermoelastic finite-element analysis. Load sharing, bonding,
resonance, shock pulse, buckling and cooldown contraction are unresolved.

The resistance screen is 20 ohm per lead, for eight wires at 100 uA per wire.
These are assumed signal requirements. Actual current, wire count, voltage
drop, noise and readout bandwidth must come from the detector electronics.

## Uncertainty and interpretation

Nominal interpolation retains the original increasing 88.5–153 K curve.
The lower capacity scenario is max(0, Q(T-1.2 K)-3.12 mW); the upper is
Q(T+1.2 K)+3.12 mW. Both are restricted to the common domain 89.7–151.8 K.
This uses the original map's conservative ±1 K/±3 mW reading allowances plus
the paper's ±0.2 K/±0.12 mW instrument errors. It does not silently replace the
original map with the separate milestone-4 subset.

These coherent shifts screen reading errors on a monotone curve. They do not
include all experimental uncertainty, interpolation bias, thermal-history
effects, or modifications to the reference cooler during assembly. No confidence
level is assigned. The additional adverse scenario combines selected uncertain
inputs; it is not an exhaustive tolerance analysis. Nominal equilibrium below
or above the measured branch is reported explicitly without extrapolation.

Maximum device power is solved at Td=100 K by finding the corresponding platform
temperature and enforcing the total heat balance. A direct target-boundary
solution is checked against the complete equilibrium solver. An infeasible
case is distinguished from a valid maximum of zero power.

## Sources

- Qi et al., Applied Thermal Engineering (2023):
  https://doi.org/10.1016/j.applthermaleng.2023.120361.
- Tong et al., Cryogenics (2024):
  https://doi.org/10.1016/j.cryogenics.2024.103929.
- NIST 304 conductivity:
  https://trc.nist.gov/cryogenics/materials/304Stainless/304Stainless_rev.htm.
- NIST G10 conductivity:
  https://trc.nist.gov/cryogenics/materials/G-10%20CR%20Fiberglass%20Epoxy/G10CRFiberglassEpoxy_rev.htm.

The journal evidence remains focused on the recent supplied papers. NIST is a
primary legacy property-data source, not additional recent journal evidence.
