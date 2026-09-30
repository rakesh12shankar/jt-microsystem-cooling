import unittest
from copy import deepcopy
import numpy as np
from array_model import design,solve,max_power,die_heat,band_exitance,optical,interface_R
from array_optimization import peak_power
from array_transient import simulate
from package_fem import thermal,mechanical
from model import SIGMA

class ArrayStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=design()

    def test_active_area_fits_envelope(self):
        derived=np.array(self.p['pixels'])*self.p['pitch_m']
        np.testing.assert_allclose(derived,self.p['active_dimensions_m'])
        self.assertTrue(np.all(derived<np.array(self.p['die_dimensions_m'][:2])))

    def test_spectral_power_bound(self):
        p=self.p;b=band_exitance(295,[3,5])
        self.assertTrue(0<b<SIGMA*295**4)
        self.assertAlmostEqual(optical(p,295),0)
        area=np.prod(p['active_dimensions_m']);view=1/(1+4*p['f_number']**2)
        upper=area*view*p['detector_absorptance']*SIGMA*(295**4-100**4)
        self.assertTrue(0<optical(p,100)<upper)

    def test_array_target_boundary(self):
        limit=max_power(self.p);r=solve({**self.p,'device_power_W':limit})
        self.assertAlmostEqual(r['die_K'],100,places=6)
        self.assertLess(abs(r['energy_residual_W']),1e-9)

    def test_thermal_fem_analytical_layered_limit(self):
        r=thermal(self.p,2,total_W=.02,hotspot_W=0,base_K=90)
        self.assertAlmostEqual(r['max_die_K'],90+.02*interface_R(self.p),places=7)
        self.assertLess(r['die_nonuniformity_K'],1e-7)
        self.assertLess(abs(r['energy_residual_W']),1e-9)

    def test_thermal_fem_linearity_and_heat_balance(self):
        a=thermal(self.p,2,total_W=.01,hotspot_W=.005,base_K=0)
        b=thermal(self.p,2,total_W=.02,hotspot_W=.01,base_K=0)
        self.assertAlmostEqual(b['max_die_K'],2*a['max_die_K'],places=8)
        self.assertLess(abs(b['energy_residual_W']),1e-9)

    def test_matched_expansion_is_stress_free(self):
        r=mechanical(self.p,2,matched_alpha=True)
        self.assertLess(r['peak_von_mises_MPa'],1e-6)
        self.assertLess(r['warpage_um'],1e-6)

    def test_zero_cooldown_and_force_residual(self):
        r=mechanical(self.p,2,cold_K=295)
        self.assertLess(r['peak_von_mises_MPa'],1e-10)
        r=mechanical(self.p,2,cold_K=100)
        self.assertLess(r['free_residual_N'],1e-7)
        self.assertGreater(r['warpage_um'],0)

    def test_peak_limit_matches_fem(self):
        f=thermal(self.p,2,total_W=.01,hotspot_W=.005,base_K=0)
        beta=(f['max_die_K']-f['mean_die_K'])/.005
        limit=peak_power(self.p,beta);p={**self.p,'device_power_W':limit};r=solve(p)
        f=thermal(p,2,total_W=die_heat(r['loads_W']),hotspot_W=.5*limit,base_K=r['platform_K'])
        self.assertAlmostEqual(f['max_die_K'],100,places=6)
        self.assertLess(limit,max_power(self.p))

    def test_transient_equilibrium_and_energy(self):
        r=simulate(self.p,power_end=.01,duration=5)
        self.assertLess(np.ptp(r['die_K']),1e-7)
        r=simulate(self.p,power_end=.015,duration=5)
        self.assertLess(r['energy_residual_J'],1e-8)
        self.assertTrue(all(v<0 for v in r['local_eigenvalues_per_s']))
        self.assertGreater(r['die_K'][-1],r['die_K'][0])

if __name__=='__main__':unittest.main()
