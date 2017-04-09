#! /usr/bin/env python
"""
:mod:`egg_profile` -- Analytic equation for egg profile points
===============================================================================

.. module:: egg_profile
   :synopsis: Analytic equation for egg profile points
.. moduleauthor:: Arthur Davis <art.davie@gmail.com>

Copyright 2017 Arthur Davis (art.davis@gmail.com)
Licensed under the MIT License

2017-04-02 - File creation

Contains function for calculating egg profile and plots a comparison against
the sampled profile coordinates.
"""
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# Setup to use breakpt() for droppping into ipdb:
import IPython
breakpt = IPython.core.debugger.set_trace

CWD=os.path.dirname(os.path.abspath(__file__))
MODNAME = os.path.splitext(os.path.basename(__file__))[0]

# Analytic egg profile equation
def egg(x, l=78.):
    '''
    Generates any size egg profile of length specified in the 'l' parameter.

    Parameters
    ----------
    x : list-like
        Coordinate points for which to calculate egg shell profile
    l : float
        Length of the shell profile (default: 78.)
    '''
    term1 = (1 - x / l)**(2/3.)
    return 0.9 * l * term1 * np.sqrt(1 - term1)

# Get the coordinate points for the sampled egg shell
df = pd.read_csv('egg-profile_outer.csv')
# Drop the last data point which returns the profile to the origin
df = df.drop(df.index[-1])
# Swap x and y axes to make profile differentiable
df.set_index('y', inplace=True)
df.index.name='x'
df.columns = ['data']
# Add column with analytic calculation of the profile
df['equation'] = egg(df.index)

df.plot()
plt.show()

