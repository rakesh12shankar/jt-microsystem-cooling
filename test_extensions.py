import unittest
import numpy as np
from distributed_hx import HX,solve_hx
from bond_defects import basis,equilibrium,allowable_power
from package_fem import thermal
from array_model import design,interface_R
from array_optimization import peak_power


class DistributedTests(unittest.TestCase):
    def test_cell_and_global_energy(self):
        r=solve_hx(130,6.93e-6,HX(cells=12))
        self.assertLess(abs(r['energy_residual_W']),1e-7)
        self.assertLess(r['max_cell_residual_W'],1e-7)
        self.assertGreater(r['return_superheat_min_K'],0)

    def test_insulated_zero_axial_limit(self):
        r=solve_hx(130,6.93e-6,HX(cells=12,emissivity=0,cold_emissivity=0,axial_W_K=0,gas_wall_W_K=.1))
        self.assertAlmostEqual(r['hx_radiation_W'],0)
        self.assertAlmostEqual(r['net_W'],r['gross_cold_W'])
        np.testing.assert_allclose(r['wall_K'],r['insulation_K'],atol=1e-7)

    def test_excludes_wet_branch(self):
        with self.assertRaises(ValueError):solve_hx(100,4.4e-6)


class BondTests(unittest.TestCase):
    def test_intact_recovers_existing_solver(self):
        p=design();b=basis(p,2);r=thermal(p,2,total_W=.02,hotspot_W=.005,base_K=0)
        t=b['top_basis']@np.array([.015,.005])
        np.testing.assert_allclose(t,r['temperature_K'][r['top_ids']],atol=1e-9)

    def test_uniform_full_degradation_analytic(self):
        p=design();b=basis(p,2,1.,ratio=.1)
        area=np.prod(p['die_dimensions_m'][:2])
        bond=(p['bond_thickness_m']/p['bond_conductivity_W_mK']+p['contact_resistivity_m2K_W'])/area
        expected=interface_R(p)+9*bond
        self.assertAlmostEqual(b['mean_basis'][0],expected,places=6)

    def test_load_basis_conservation(self):
        b=basis(design(),4,.25)
        np.testing.assert_allclose(b['energy_residual_per_W'],0,atol=1e-9)
        self.assertAlmostEqual(b['actual_fraction'],.25,places=8)

    def test_central_defect_raises_hotspot(self):
        p=design();intact=basis(p,2);bad=basis(p,2,.25)
        force=np.array([.015,.005])
        self.assertGreater((bad['top_basis']@force).max(),(intact['top_basis']@force).max())

    def test_intact_power_boundary_matches_old_method(self):
        p=design();b=basis(p,2)
        r=thermal(p,2,total_W=.01,hotspot_W=.005,base_K=0)
        beta=(r['max_die_K']-r['mean_die_K'])/.005
        power=allowable_power(p,b)
        self.assertAlmostEqual(power,peak_power(p,beta),places=8)
        self.assertAlmostEqual(equilibrium(p,b,power)['peak_K'],100,places=6)


if __name__=='__main__':unittest.main()
