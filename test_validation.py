"""Independent accounting identities for the validation diagnostics."""
import unittest
from dataclasses import replace
from CoolProp.CoolProp import PropsSI
from realfluid import Cycle
from run_realfluid import at_platform_temperature
from run_validation import budget


class ValidationTests(unittest.TestCase):
    def test_ideal_isothermal_warm_boundary(self):
        # With no losses and perfect recuperation, a warm-end-limited cycle
        # must recover the analytical enthalpy-difference capacity.
        c=replace(Cycle(),reference_emissivity=0,reference_axial_W_K=0,
            fluid_to_platform_K_W=0,effectiveness=1,mass_flow_kg_s=7.94e-6)
        r=at_platform_temperature(153,c)
        exact=c.mass_flow_kg_s*(PropsSI('Hmass','P',c.outlet_pressure_Pa,'T',295,c.fluid)-
            PropsSI('Hmass','P',c.high_pressure_Pa,'T',295,c.fluid))
        self.assertAlmostEqual(r['net_external_W'],exact,places=9)

    def test_decomposition_and_boundary_temperature(self):
        for t,m in [(90,4.18e-6),(100,4.41e-6),(153,7.94e-6)]:
            c=replace(Cycle(),mass_flow_kg_s=m)
            r=at_platform_temperature(t,c);b=budget(r,c)
            self.assertAlmostEqual(r['platform_K'],t,places=6)
            self.assertLess(abs(b['closure_residual_mW']),1e-6)
            self.assertGreaterEqual(b['warm_outlet_deficit_mW'],-1e-6)

    def test_whole_cooler_second_law(self):
        # Steady control volume includes recuperator, valve and cold region.
        # Boundary heat enters at the cold platform and 295 K enclosure.
        for t,m in [(90,4.18e-6),(100,4.41e-6),(153,7.94e-6)]:
            c=replace(Cycle(),mass_flow_kg_s=m)
            r=at_platform_temperature(t,c);s=r['states']
            ds=PropsSI('Smass','P',c.outlet_pressure_Pa,'Hmass',s['5_warm_low_out']['enthalpy_J_kg'],c.fluid)-PropsSI('Smass','P',c.high_pressure_Pa,'Hmass',s['1_warm_high_in']['enthalpy_J_kg'],c.fluid)
            qambient=r['hx_radiation_W']+r['cold_reference_radiation_W']+r['reference_axial_W']
            entropy_generation=c.mass_flow_kg_s*ds-r['net_external_W']/t-qambient/c.ambient_K
            self.assertGreaterEqual(entropy_generation,-1e-10)


if __name__=='__main__':unittest.main()
