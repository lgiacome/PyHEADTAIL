'''
@date:   15/04/2015
@author: Stefan Hegglin
'''
from __future__ import division

import sys, os
BIN = os.path.dirname(__file__) # ./PyHEADTAIL/testing/unittests/
BIN = os.path.abspath( BIN ) # absolute path to unittests
BIN = os.path.dirname( BIN ) # ../ -->  ./PyHEADTAIL/testing/
BIN = os.path.dirname( BIN ) # ../ -->  ./PyHEADTAIL/
BIN = os.path.dirname( BIN ) # ../ -->  ./
sys.path.append(BIN)

import unittest

import numpy as np
from scipy.constants import c, e, m_p

from PyHEADTAIL.particles.particles import Particles
from PyHEADTAIL.particles.generators import Gaussian6DTwiss
from PyHEADTAIL.general.printers import AccumulatorPrinter
import PyHEADTAIL.cobra_functions.stats as cf
from PyHEADTAIL.trackers.simple_long_tracking import LinearMap



class TestCobra(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.tolerance = 6
        self.n_samples = 1000000
        self.data1_var = 0.001
        #some random data to use for cov/eps/... computations
        self.data1 = np.random.normal(0, np.sqrt(self.data1_var), self.n_samples)
        self.data2 = np.random.normal(5., 0.1, self.n_samples)
        self.data3 = np.random.laplace(loc=-2., scale=0.5, size=self.n_samples)

    def tearDown(self):
        pass
    def test_covariance_for_variance(self):
        """ Test whether the cov_onepass, std, cov return the correct variance
        for a simulated data set
        """
        v1 = cf.cov(self.data1, self.data1)
        v2 = cf.cov_onepass(self.data1, self.data1)
        v3 = cf.std(self.data1)
        self.assertAlmostEqual(v1, self.data1_var, places=self.tolerance,
                               msg='stats.cov() is wrong when computing' +
                               'the variance of a dataset')
        self.assertAlmostEqual(v2, self.data1_var, places=self.tolerance,
                               msg='stats.cov_onepass is wrong when computing' +
                               'the variance of a dataset')

    def test_consistency_covariance(self):
        """ Test whether cov_onepass, cov return the same covariance for a
        simulated data set
        """
        v1 = cf.cov(self.data1, self.data2)
        v2 = cf.cov_onepass(self.data1, self.data2)
        self.assertAlmostEquals(v1, v2, places=self.tolerance,
                                msg='cov, cov_onepass results differ')

    def test_consistency_effective_emittance(self):
        """ Test whether effective_emittance and emittance_old return the
        same values """
        #eps1 = cf.effective_emittance(self.data1, self.data3)
        eps1 = cf.emittance(self.data2, self.data3, None)
        eps2 = cf.emittance_old(self.data2, self.data3)
        self.assertAlmostEquals(eps1, eps2, places=self.tolerance,
                                msg='the new effective emittance computation' +
                                'yields different results than the old one')

    def test_eta_prime_is_zero(self):
        """ Test whether computing eta_prime of a beam generated using
        Gaussian6dTwiss is 0 """
        bunch = self.generate_gaussian6dBunch(1000, 1, 1, 2, 1, 5, 100)
        eta_prime_x = cf.dispersion(bunch.xp, bunch.dp)
        self.assertAlmostEquals(eta_prime_x, 0., places=self.tolerance,
                                msg='eta_prime_x is not zero but ' + str(eta_prime_x))
        eta_prime_y = cf.dispersion(bunch.yp, bunch.dp)
        self.assertAlmostEquals(eta_prime_y, 0., places=self.tolerance,
                                msg='eta_prime_y is not zero but ' + str(eta_prime_y))




    def generate_gaussian6dBunch(self,n_macroparticles, alpha_x, alpha_y, beta_x,
                                  beta_y, dispx, dispy,
                                  gamma = 3730.27):
        Q_s = 0.0020443
        C = 26658.883
        alpha_0 = [0.0003225]
        linear_map = LinearMap(alpha_0, C, Q_s)

        intensity = 1.05e11
        sigma_z = 0.0059958
        gamma_t = 1. / np.sqrt(alpha_0)
        p0 = np.sqrt(gamma**2 - 1) * m_p * c
        beta_z = (linear_map.eta(dp=0, gamma=gamma) * linear_map.circumference /
              (2 * np.pi * linear_map.Qs))
        epsn_x = 3.75e-6 # [m rad]
        epsn_y = 3.75e-6 # [m rad]
        epsn_z = 4 * np.pi * sigma_z**2 * p0 / (beta_z * e)
        bunch = Gaussian6DTwiss(
            macroparticlenumber=n_macroparticles, intensity=intensity, charge=e,
            gamma_reference=gamma, mass=m_p, circumference=C,
            alpha_x=0., beta_x=1., epsn_x=epsn_x,
            alpha_y=0., beta_y=1., epsn_y=epsn_y,
            beta_z=beta_z, epsn_z=epsn_z).generate()
        # Scale to correct beta and alpha
        bunch.x *= np.sqrt(beta_x)
        bunch.xp = -alpha_x/np.sqrt(beta_x) * bunch.x + 1./np.sqrt(beta_x) * bunch.xp
        bunch.y = np.sqrt(beta_y)*bunch.y
        bunch.yp = -alpha_y/np.sqrt(beta_y) * bunch.y + 1./np.sqrt(beta_y) * bunch.yp
        bunch.x += dispx * bunch.dp
        bunch.y += dispy * bunch.dp
        return bunch

if __name__ == '__main__':
    unittest.main()

