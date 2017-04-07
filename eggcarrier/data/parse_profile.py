#! /usr/bin/env python
"""
:mod:`parse_profile` -- Convert unstructured profile data to xy coords
===============================================================================

.. module:: parse_profile
   :synopsis: Convert unstructured profile data to xy coords
.. moduleauthor:: Arthur Davis <art.davis@gmail.com>

Copyright 2017 Arthur Davis (art.davis@gmail.com)
Licensed under the MIT License

2017-04-02 - File creation
"""
import os
import numpy as np
import pandas as pd

# Setup to use breakpt() for droppping into ipdb:
import IPython
breakpt = IPython.core.debugger.set_trace

CWD=os.path.dirname(os.path.abspath(__file__))
MODNAME = os.path.splitext(os.path.basename(__file__))[0]

with open('egg-profile_data.csv', 'r') as fid:
    raw = fid.read().strip()

i = iter(raw.split(','))

x = []
y = []
try:
    while True:
        x.append(float(next(i)))
        y.append(float(next(i)))
except StopIteration:
    pass

xpts = np.array(x)
ypts = -np.array(y)

# Set zero origin
xpts = xpts - np.min(xpts)
ypts = ypts - np.min(ypts)

df = pd.DataFrame({'x': xpts, 'y': ypts})

df.to_csv('egg-profile_xy.csv', index=False)
