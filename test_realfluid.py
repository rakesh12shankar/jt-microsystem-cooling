import unittest
from dataclasses import replace
from CoolProp.CoolProp import PropsSI
from realfluid import Cycle,evaluate,solve_package,slit_flow_diagnostic
from model import Package

class RealFluidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=Cycle();cls.r=solve_package(Package(),cls.c)

    def test_saturation_benchmark(self):
        self.assertAlmostEqual(self.c.saturation_K,87.3,delta=.1)

    def test_pressure_accounting(self):
        s=self.r['states'];c=self.c
        self.assertEqual(s['2_cold_high_before_valve']['pressure_Pa'],c.high_pressure_Pa-c.high_drop_Pa)
        self.assertEqual(s['3_after_valve']['pressure_Pa'],285000)
        self.assertEqual(s['5_warm_low_out']['pressure_Pa'],240000)

    def test_valve_first_and_second_laws(self):
        r=self.r
        self.assertLess(abs(r['valve_enthalpy_residual_J_kg']),1e-8)
        self.assertGreaterEqual(r['valve_entropy_generation_W_K'],-1e-10)
        self.assertGreater(r['states']['2_cold_high_before_valve']['temperature_K'],r['states']['3_after_valve']['temperature_K'])

    def test_energy_closure_at_each_boundary(self):
        for key in ['hx_energy_residual_W','cycle_energy_residual_W','package_energy_residual_W']:
            self.assertLess(abs(self.r[key]),1e-8)
        # Entire assembly: enthalpy rise = package load + all reference heat leaks.
        r=self.r;s=r['states'];m=self.c.mass_flow_kg_s
        supplied=sum(r['package_loads_W'].values())+r['hx_radiation_W']+r['cold_reference_radiation_W']+r['reference_axial_W']
        self.assertAlmostEqual(m*(s['5_warm_low_out']['enthalpy_J_kg']-s['1_warm_high_in']['enthalpy_J_kg']),supplied,places=8)

    def test_two_phase_return_and_pinch(self):
        s=self.r['states'];q3=s['3_after_valve']['quality'];q4=s['4_evaporator_return']['quality']
        self.assertTrue(0<=q3<q4<=1)
        self.assertGreaterEqual(self.r['pinch_K'],-1e-7)

    def test_no_recuperation_cannot_meet_baseline(self):
        r=solve_package(Package(),replace(self.c,effectiveness=0))
        self.assertEqual(r['status'],'no_equilibrium_in_search_domain')

    def test_ideal_warm_end_capacity_bound(self):
        c=replace(self.c,reference_emissivity=0,reference_axial_W_K=0,effectiveness=1,fluid_to_platform_K_W=0)
        h=PropsSI('Hmass','P',c.evaporator_Pa,'Q',1,c.fluid)
        r=evaluate(h,c)
        bound=c.mass_flow_kg_s*(PropsSI('Hmass','T',c.ambient_K,'P',c.outlet_pressure_Pa,c.fluid)-PropsSI('Hmass','T',c.ambient_K,'P',c.high_pressure_Pa,c.fluid))
        self.assertLessEqual(r['gross_cold_W'],bound+1e-9)

    def test_invalid_inputs(self):
        for args in [{'effectiveness':1.1},{'mass_flow_kg_s':0},{'high_drop_Pa':12e6},{'low_drop_Pa':-1}]:
            with self.assertRaises(ValueError):Cycle(**args)
        with self.assertRaises(ValueError):solve_package(replace(Package(),ambient_K=300),self.c)

    def test_restriction_diagnostic(self):
        flow=slit_flow_diagnostic(self.r['platform_K'],self.c)
        self.assertTrue(1e-6<flow<10e-6)

if __name__=='__main__':unittest.main()
