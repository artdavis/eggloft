#! /usr/bin/env python
"""
:mod:`eggcarrier_1` -- Hollow Egg Carrier CAD Model
===============================================================================

.. module:: eggcarrier_1
   :synopsis: Hollow Egg Carrier CAD Model
.. moduleauthor:: Arthur Davis <art.davie@gmail.com>

Copyright 2017 Arthur Davis (art.davis@gmail.com)
Licensed under the MIT License

2017-04-02 - File creation

"""
import os
import numpy as np

# Solidpython
import solid as sol
from solid import utils as solu

# Setup to use breakpt() for droppping into ipdb:
import IPython
breakpt = IPython.core.debugger.set_trace

CWD=os.path.dirname(os.path.abspath(__file__))
MODNAME = os.path.splitext(os.path.basename(__file__))[0]

PROF_INNER = os.path.join('data', 'egg-profile_inner.csv')
PROF_OUTER = os.path.join('data', 'egg-profile_outer.csv')
SEGMENTS = 48
WALL_TH = 2.0
LENGTH = 78.0 # Shell profile length

HEADER = '''
// Copyright 2017 Arthur Davis (thingiverse.com/artdavis)
// This file is licensed under a Creative Commons Attribution 4.0
// International License.
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
// DEALINGS IN THE SOFTWARE.

// Coupler Shoulder Length
coupler_shoulder_len = 6.0; // [1.0:1.0:25.0]
// Coupler Shoulder Diameter
coupler_shoulder_diam = 18.7; // [10.0:0.2:50.0]
// Fitting Shoulder Length
coupler_fitting_len = 12.0; // [5.0:1.0:25.0]
// Fitting Shoulder Diameter
coupler_fitting_diam = 17.9; // [10.0:0.2:50.0]

/* [Hidden] */
// Special variables for facets/arcs
$fn = {SEGMENTS};

// Incremental offset to make good overlap for CSG operations
delta = 0.1;

// Coupler extension to overlap with egg shell
coupler_extra = 50.0;

// Wall thickness of the fitting
wall_th = {WALL_TH};
'''.format(**locals())

# Get x, y tuples from the csv file
def read_csv(filename, cols=[0, 1]):
    '''
    Parameters
    ----------
    filename : str
        Filepath to the csv file to read
    cols : list-like, optional
        Which columns to use for the x and y values respectively
        (default: [0, 1])
    '''
    coords = []
    with open(filename, 'r') as fid:
        for fline in fid:
            try:
                pts = fline.split(',')
                coords.append([float(pts[cols[0]]), float(pts[cols[1]])])
            except ValueError:
                # Skip any lines that won't convert to floats (i.e. comments)
                pass
    return coords

def egg(length=LENGTH, nsteps=100, offset=0):
    '''
    Parameters
    ----------
    length : float
        The length of the egg shell. Typical outer shell length = 78.
    nsteps : int
        Number of points to sample over the profile
    offset : float
        How much to offset from the origin (set to the wall thickness)
    '''
    xpts = np.linspace(0, length, nsteps)
    term1 = (1 - xpts / length)**(2/3.)
    profile = 0.9 * length * term1 * np.sqrt(1 - term1)
    # For the profile to "stand up" swap the axes
    coords = list(zip(profile, xpts + offset))
    # Add origin point as the last point to close the profile
    coords.append((0., offset))
    return coords

# Read the outer profile for the shell
#shell = sol.polygon(read_csv(PROF_OUTER))
# Generate the outer profile for the shell
shell = sol.polygon(egg(LENGTH))
# Rotational extrusion to make the solid.
# rotate_extrude takes the profile on the XY plane and uses it as the
# profile in the XZ plane for revolution about the Z-axis
shell = sol.rotate_extrude(convexity=10)(shell)

# Variables...
# The following variables need to be defined in the HEADER string
# for OpenSCAD to have access to them in the generated program:
# coupler_shoulder_len, coupler_shoulder_diam, coupler_fitting_len
# coupler_fitting_diam, coupler_extra, delta, wall_th
OUTFILE = 'Customizable_hollow_egg_carrier.scad'
coupler_fitting_diam = 'coupler_fitting_diam'
coupler_shoulder_h = 'coupler_shoulder_len + coupler_extra'
coupler_shoulder_diam = 'coupler_shoulder_diam'
coupler_shoulder_shift = '-coupler_shoulder_len'
coupler_fitting_h = 'coupler_fitting_len + delta'
coupler_fitting_shift = '-(coupler_shoulder_len + coupler_fitting_len)'
hole_len = 'coupler_shoulder_len + coupler_extra + coupler_fitting_len'
hole_h = hole_len + ' + delta'
hole_diam = 'coupler_fitting_diam - 2 * wall_th'
hole_shift = '-(coupler_shoulder_len + coupler_fitting_len + delta/2.)'

# Make the coupler
coupler_shoulder = sol.cylinder(h=coupler_shoulder_h, d=coupler_shoulder_diam)
coupler_shoulder = sol.translate(
        v=(0, 0, coupler_shoulder_shift))(coupler_shoulder)

coupler_fitting = sol.cylinder(h=coupler_fitting_h, d=coupler_fitting_diam)
coupler_fitting = sol.translate(
        v=(0, 0, coupler_fitting_shift))(coupler_fitting)

coupler = coupler_shoulder + coupler_fitting

# Hollow out the coupler
c_hole = sol.cylinder(h=hole_h, d=hole_diam)
c_hole = sol.translate(v=(0, 0, hole_shift))(c_hole)
coupler -= c_hole # Make the hole

geom = shell + coupler

# Core out the inner cavity
#cav = sol.polygon(read_csv(PROF_INNER))
cav = sol.polygon(egg(length=LENGTH-2*WALL_TH, offset=WALL_TH))
cav = sol.rotate_extrude()(cav)

geom -= cav

# Chopping block
cs = 200 # chop size
chop = sol.translate(v=(0, -cs/2., -cs/2.))(sol.cube(size=cs))

geom -= chop

# Rotate for 3D printing (Z-direction normal to platen)
geom = sol.rotate(a=(0, 90., 0))(geom)

sol.scad_render_to_file(geom, filepath=OUTFILE,
        file_header=HEADER,
        include_orig_code=False)

# Post-Processor...
# The variables have been preserved but are surrounded by double-quotes (") in
# the OpenSCAD file. These need to be stripped out for the file to work.
filestring = ''
with open(OUTFILE, 'r') as fid:
    for fline in fid:
        if fline.startswith('//') or fline.startswith('/*'):
            # Leave comment lines as is
            filestring += fline
        else:
            # Strip all occurrences of double quotes in code context
            filestring += fline.replace('"', '')

# Overwrite OUTFILE with the post-processed code
with open (OUTFILE, 'w') as fid:
    fid.write(filestring)

