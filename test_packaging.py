import json,unittest
from scipy.integrate import quad
from model import ROOT
from packaging_model import conduct,conductivity,constraints,equilibrium,max_power,ScreenCapacity

class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg=json.loads((ROOT/'config/packaging.json').read_text(encoding='utf-8'))
        cls.p={**cfg['common'],**cfg['architectures'][1]}

    def test_property_integration_against_adaptive_quadrature(self):
        for mat in ['ss304','g10_warp']:
            expected=quad(lambda t:float(conductivity(mat,t)),90,295,epsabs=1e-9)[0]
            self.assertAlmostEqual(conduct(mat,90,295,1,1),expected,delta=expected*1e-8)
            self.assertEqual(conduct(mat,100,100,1,1),0)
        with self.assertRaises(ValueError):conductivity('g10_warp',310)

    def test_equilibrium_and_target_boundary(self):
        for kind in ['nominal','lower','upper']:
            c=ScreenCapacity(kind);limit=max_power(self.p,c)
            r=equilibrium({**self.p,'device_power_W':limit},c)
            self.assertAlmostEqual(r['detector_K'],100,places=6)
            self.assertLess(abs(r['energy_residual_W']),1e-9)
            self.assertLess(abs(r['interface_residual_K']),1e-8)

    def test_capacity_order_and_domain(self):
        limits=[max_power(self.p,ScreenCapacity(k)) for k in ['lower','nominal','upper']]
        self.assertTrue(limits[0]<limits[1]<limits[2])
        with self.assertRaises(ValueError):ScreenCapacity('lower')(88.5)

    def test_cantilever_closed_form_and_scaling(self):
        p=self.p;c=constraints(p)
        # 4 beams, E=20 GPa, w=0.3mm, t=0.1mm, L=2mm: 750 N/m total.
        self.assertAlmostEqual(c['stiffness_N_m'],750,places=8)
        long=constraints({**p,'support_length_m':2*p['support_length_m']})
        self.assertAlmostEqual(long['deflection_um']/c['deflection_um'],8)
        self.assertAlmostEqual(long['stress_MPa']/c['stress_MPa'],2)

    def test_electrothermal_wire_tradeoff(self):
        p=self.p;long={**p,'lead_length_m':2*p['lead_length_m']}
        self.assertAlmostEqual(constraints(long)['lead_resistance_ohm']/constraints(p)['lead_resistance_ohm'],2)
        self.assertGreater(max_power(long),max_power(p))
        self.assertFalse(constraints(long)['electrical_pass'])

    def test_steel_support_thermal_overload(self):
        self.assertIsNone(max_power({**self.p,'support_material':'ss304'}))

if __name__=='__main__':unittest.main()
