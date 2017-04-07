#! /usr/bin/env python
"""
:mod:`fit_profile` -- Fit egg profile points to analytic equation
===============================================================================

.. module:: eggcarrier_1
   :synopsis: Fit egg profile points to analytic equation
.. moduleauthor:: Arthur Davis <art.davie@gmail.com>

Copyright 2017 Arthur Davis (art.davis@gmail.com)
Licensed under the MIT License

2017-04-02 - File creation

"""
import os
import numpy as np
import pandas as pd
from scipy import optimize
from matplotlib import pyplot as plt

# Setup to use breakpt() for droppping into ipdb:
import IPython
breakpt = IPython.core.debugger.set_trace

CWD=os.path.dirname(os.path.abspath(__file__))
MODNAME = os.path.splitext(os.path.basename(__file__))[0]

def asphere(coef, x):
    '''
    A simple asphere equation assuming kappa=01 and ad2=0:
    cvt * x**2 / 2. + ad4 * x**4 + ad6 * x**6 + ad8 * x**8

    Parameters
    ----------
    coef : list-like
        [cvt, ad4, ad6, ad8]
    x : float or numpy.ndarray
        X-coordinate point to apply function to
    '''
    return(coef[0] * x**2 / 2.0
             + coef[1] * x**4
             + coef[2] * x**6
             + coef[3] * x**8)

def asphere_jacobian(x):
    # Derivatives wrt the coefficients (set of partials at x for each
    # coeff). Note since coeffs are all linear there is no dependence
    # on them in the Jacobian.
    return([x**2 / 2.0, x**4, x**6, x**8])

# Get the coordinate points that define the fit
df = pd.read_csv('egg-profile_outer.csv')
# Drop the last data point which returns the profile to the origin
df = df.drop(df.index[-1])

# Make some lambda functions for the leastsq fitter
errfunc = lambda p, x, y: asphere(p, x) - y
jacobian = lambda p, x, y: asphere_jacobian(x)
# Initial guess for the coefficients:
coeffs0 = [ .01, 0, 0, 0 ]
# Do the fit:
csolve, success = optimize.leastsq(
        errfunc, coeffs0,
        args=(df['x'].values, df['y'].values),
        Dfun=jacobian, col_deriv=True)

# Use the solved equation to calculate a profile
df['y2'] = asphere(csolve, df['x'])
# Make the x column the index
#df.set_index('x', inplace=True)

# Plot
df.plot.scatter(x=['x', 'x'], y=['y', 'y2'])
plt.show()
