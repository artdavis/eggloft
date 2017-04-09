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

class Asphere(object):
    def __init__(self):
        pass

    def eq(self, params, x):
        '''
        A simple asphere equation assuming kappa=01 and ad2=0:
        cvt * x**2 / 2. + ad4 * x**4 + ad6 * x**6 + ad8 * x**8

        Parameters
        ----------
        params : list-like
            [cvt, ad4, ad6, ad8]
        x : float or numpy.ndarray
            X-coordinate point to apply function to
        '''
        return(params[0] * x**2 / 2.0
                 + params[1] * x**4
                 + params[2] * x**6
                 + params[3] * x**8)

    def jacobian(self, params, x):
        # Derivatives wrt the coefficients (set of partials at x for each
        # coeff). Note since coeffs are all linear there is no dependence
        # on them in the Jacobian.
        return([x**2 / 2.0, x**4, x**6, x**8])

class SinCos(object):
    def __init__(self, scalar = np.pi / 78.0):
        # Scalar to put in range from 0 to pi
        self.scalar = scalar

    def eq(self, params, x):
        # TODO: try some polar form (The Folium: cos^3).
        # Ref: http://www.mathematische-basteleien.de/eggcurves.htm
        # Ref: http://www.geocities.jp/nyjp07/index_egg_E.html
        # y = sqrt((a-b)-2x+sqrt(4bx+(a-b)^2))*sqrt(x)/sqrt(2)
        a, b, c = params
        return (a * np.sin(b * x * self.scalar)
                  * np.cos(c * x * self.scalar))
    def jacobian(self, params, x):
        a, b, c = params
        return([np.sin(b * x * self.scalar) * np.cos(c * x * self.scalar),
                a * np.cos(b * x * self.scalar) * np.cos(c * x * self.scalar),
                -a * np.sin(b * x * self.scalar) * np.sin(c * x * self.scalar)])

class ThirdDegree(object):
    def __init(self):
        pass

    def eq(self, params, x):
        a, b, c, d = params
        return np.sqrt(a*(x-b)*(x-c)*(x-d))

    def jacobian(self, params, x):
        a, b, c, d = params
        denom = 2 * np.sqrt(a*(x-b)*(x-c)*(x-d))
        dyda = (x-b)*(x-c)*(x-d) / denom
        dydb = -a*(x-c)*(x-d) / denom
        dydc = -a*(x-b)*(x-d) / denom
        dydd = -a*(x-b)*(x-c) / denom
        return [dyda, dydb, dydc, dydd]

# Initial guess for the coefficients:
coeffs0 = [ .01, .01, .01, .01 ]
egg = Asphere()
#egg = ThirdDegree()
#coeffs0 = [1, 1, 1]
#egg = SinCos()

# Get the coordinate points that define the fit
df = pd.read_csv('egg-profile_outer.csv')
# Drop the last data point which returns the profile to the origin
df = df.drop(df.index[-1])

# Make index of dataframe the abscissa
dfx = df.copy()
dfx.set_index('x', drop=False, inplace=True)
dfx['r'] = np.sqrt(dfx['x']**2 + dfx['y']**2)
dfx['theta'] = np.arccos(dfx['x'] / dfx['r'])
# Zero out NaNs
dfx['theta'][dfx['theta'].isnull()] = 0
dfx['theta_deg'] = np.degrees(dfx['theta'])
dfx['cos'] = np.cos(dfx['theta'])
dfx['sin'] = np.sin(dfx['theta'])
rmax = dfx['r'].max()
dfx['r2'] = (np.cos(dfx['theta']))**2 * rmax
dfx['x2'] = dfx['r2'] * dfx['cos']
dfx['y2'] = dfx['r2'] * dfx['sin'] * 0.9
# Juggle coordinates to stand up the egg profile
#dfx['x2'] = np.abs(dfx['x2'] - dfx['x2'].max())
#tmpx = dfx['x2'].copy()
#dfx['x2'] = dfx['y2']
#dfx['y2'] = tmpx
rat1 = dfx['x']**2 / dfx['r']**2
dfx['y3'] = 0.9 * rmax * rat1 * np.sqrt(1 - rat1)

df3 = dfx.loc[:, :'sin'].copy()
df3['x2'] = rmax * df3['cos']**3
df3['y2'] = 0.9 * rmax * df3['cos']**2 * df3['sin']
df3['x3'] = df3['x2'].copy()
rat2 = (df3['x3'] / rmax) ** (2./3.)
df3['y3'] = 0.9 * rmax * rat2 * np.sqrt(1 - rat2)

#dfx.plot.scatter(['x', 'x2'], ['y', 'y2'])
#df3.plot.scatter(['x', 'x2', 'x', ], ['y', 'y2', 'y3'])
df3.plot.scatter(['x', 'x3'], ['y', 'y3'])
#dfx.plot.scatter(['x', 'x'], ['y', 'y3'])
plt.show()


# Make a dataframe that swaps x and y axes to make profile differentiable
dfy = df.copy()
dfy.set_index('y', inplace=True)
dfy.index.name='x'
dfy.columns = ['y']

'''

# Make some lambda functions for the leastsq fitter
errfunc = lambda p, x, y: egg.eq(p, x) - y
jacobian = lambda p, x, y: egg.jacobian(p, x)

# Which dataframe to use for interpolation
#dfi = dfx
dfi = dfy

# Do the fit:
csolve, success = optimize.leastsq(
        errfunc, coeffs0,
        args=(dfi.index.values, dfi['y'].values),
        Dfun=jacobian, col_deriv=True)

# Use the solved equation to calculate a profile
#df['y2'] = asphere(csolve, dfi.index)
dfi['y2'] = egg.eq(csolve, dfi.index)
# Make the x column the index
#df.set_index('x', inplace=True)

# Plot
#df.plot.scatter(x=['x', 'x'], y=['y', 'y2'])
df.plot()
plt.show()
'''
