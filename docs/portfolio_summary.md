# Portfolio presentation

## Project title

**Joule–Thomson Cooler Integration for Infrared Microsystems**

## Short description

Developed a reproducible Python study of how supports, wiring, insulation and
bond interfaces limit useful cryogenic cooling power. Coupled measured nitrogen
cooler capacity with thermal networks, thermal and thermoelastic finite elements,
constrained geometry search and local transient analysis. Audited recent journal
experiments and reproduced a published supplementary heat budget.

## Resume bullets

- Built thermal-network and finite-element models for a reference infrared-array
  package; evaluated 1,134 geometries against thermal, mechanical and electrical
  constraints, identifying seven feasible designs under a prescribed adverse scenario.
- Predicted 11.5 mW allowable device power at a 100 K peak-die limit for the selected
  adverse-case design; documented mesh convergence, uncertainty assumptions and
  limitations through 43 automated verification tests and reproducible reports.
- Reproduced a published cryogenic heat budget and gas-runtime calculation using
  CoolProp; distinguished measured evidence, fitted parameters and residual-based
  estimates to avoid unsupported validation claims.

Use the first two bullets if space is limited. These describe simulations and
literature reproduction; they do not imply fabricated hardware or a journal publication.

## Repository description

Python models of JT cooler packaging: thermal networks, finite elements,
constrained design search, local transients and literature heat-budget reproduction.

## Suggested topics

`cryogenics`, `joule-thomson`, `thermal-analysis`, `finite-element-method`,
`microsystems`, `infrared-detectors`, `coolprop`, `python`

## Interview explanation

The main challenge was that useful detector cooling depends on its entire package.
Reducing thermal conduction by thinning supports or wires competes with stiffness
and electrical resistance. I used measured cooler capacity because the separate
real-fluid baseline had substantial prediction errors. I then tested package
tradeoffs and documented why reproducing a paper's energy-balance residual is
not independent experimental validation. The next step toward hardware would be
an actual detector specification and measured interface and insulation properties.

## Additional research contribution

- Extended the package model to spatial bond defects, showing that a 50% degraded
  edge region reduces the selected adverse-case power limit from 11.46 to 8.43 mW;
  implemented a distributed exchanger model with conservation checks and explicit
  single-phase scope to investigate uncertainty in internal heat losses.

Use this as an alternative technical bullet; do not describe the exchanger as
experimentally validated or the defect fractions as manufacturing acceptance limits.
