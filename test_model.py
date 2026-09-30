import unittest
from dataclasses import replace
from model import Package,Capacity,solve,maximum_device_power,radiation

class LinearCapacity:
    minimum=80.; maximum=153.
    def __call__(self,t): return .005*(t-80)

class ModelTests(unittest.TestCase):
    def test_closed_form_two_node_solution(self):
        # Exact solution with linear capacity, support and lead conduction.
        p=Package(stage_area_m2=0,device_area_m2=0)
        a=.005; g=p.lead_W_per_K; s=p.support_W_per_K; R=p.interface_K_per_W
        # Device heat = (P + g*(Ta-Tc))/(1+gR).
        tc=(a*80+(p.device_power_W+g*p.ambient_K)/(1+g*R)+s*p.ambient_K)/(a+g/(1+g*R)+s)
        td=tc+R*(p.device_power_W+g*(p.ambient_K-tc))/(1+g*R)
        out=solve(p,LinearCapacity())
        self.assertAlmostEqual(out['platform_K'],tc,places=8)
        self.assertAlmostEqual(out['detector_K'],td,places=8)

    def test_zero_load_limit(self):
        p=Package(device_power_W=0,support_W_per_K=0,lead_W_per_K=0,stage_area_m2=0,device_area_m2=0)
        self.assertAlmostEqual(solve(p)['detector_K'],88.5)

    def test_energy_and_interface_balance(self):
        for R in [0,50,200]:
            out=solve(replace(Package(),interface_K_per_W=R))
            self.assertLess(abs(out['energy_residual_W']),1e-9)
            self.assertLess(abs(out['interface_residual_K']),1e-8)

    def test_overload_does_not_extrapolate(self):
        self.assertEqual(solve(replace(Package(),device_power_W=1))['status'],'no_equilibrium_in_modeled_branch')
        with self.assertRaises(ValueError): Capacity()(80)
        with self.assertRaises(ValueError): solve(replace(Package(),ambient_K=300))

    def test_design_trends(self):
        p=Package(); t=solve(p)['detector_K']
        self.assertGreater(solve(replace(p,support_W_per_K=200e-6))['detector_K'],t)
        self.assertGreater(solve(replace(p,interface_K_per_W=200))['detector_K'],t)

    def test_maximum_power_boundary(self):
        p=Package(); power=maximum_device_power(p)
        self.assertAlmostEqual(solve(replace(p,device_power_W=power))['detector_K'],100,places=6)
        self.assertFalse(solve(replace(p,device_power_W=power+1e-5))['meets_target'])

    def test_infeasible_zero_power(self):
        self.assertIsNone(maximum_device_power(replace(Package(),support_W_per_K=.001)))

    def test_radiation_equilibrium_and_sign(self):
        self.assertEqual(radiation(1,.5,100,100),0)
        self.assertAlmostEqual(radiation(1,.5,295,100),-radiation(1,.5,100,295))

if __name__=='__main__': unittest.main()
