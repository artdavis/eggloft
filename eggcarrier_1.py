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

Set FILEMODE to either 'direct' or 'customizer'.
'direct' makes an OpenSCAD file without any variable names.
'customizer' preserves variable names and creates an OpenSCAD file that will
             work with the Thingiverse Customizer.
"""
import os
import pandas as pd

# Solidpython
import solid as sol
from solid import utils as solu

# Setup to use breakpt() for droppping into ipdb:
import IPython
breakpt = IPython.core.debugger.set_trace

CWD=os.path.dirname(os.path.abspath(__file__))
MODNAME = os.path.splitext(os.path.basename(__file__))[0]

PROF_INNER = 'egg-profile_inner.csv'
PROF_OUTER = 'egg-profile_outer.csv'
SEGMENTS = 48

FILEMODE = 'customizer'

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
$fn = {};

// Incremental offset to make good overlap for CSG operations
delta = 0.1;

// Coupler extension to overlap with egg shell
coupler_extra = 50.0;

// Wall thickness of the fitting
wall_th = 2.0;
'''.format(SEGMENTS)

# Read the outer profile for the shell
shell_df = pd.read_csv(PROF_OUTER)
shell = sol.polygon(list(zip(shell_df['x'], shell_df['y'])))
# Rotational extrusion to make the solid.
# rotate_extrude takes the profile on the XY plane and uses it as the
# profile in the XZ plane for revolution about the Z-axis
shell = sol.rotate_extrude(convexity=10)(shell)

# Make the coupler
def make_direct():
    # For making scad file directly for OpenSCAD
    global delta, coupler_shoulder_len, coupler_shoulder_diam
    global coupler_fitting_len, coupler_fitting_diam, coupler_extra
    global coupler_shoulder_h, coupler_shoulder_shift
    global coupler_fitting_h, coupler_fitting_shift
    global wall_th, hole_len, hole_h, hole_diam, hole_shift
    global OUTFILE
    OUTFILE = 'hollow_egg_carrier.scad'
    # Incremental offset to make good overlap for CSG operations
    delta = 0.1
    coupler_shoulder_len = 6.
    coupler_shoulder_diam = 18.7
    coupler_fitting_len = 12.
    coupler_fitting_diam = 17.9
    coupler_extra = 50.

    coupler_shoulder_h = coupler_shoulder_len + coupler_extra
    coupler_shoulder_shift = -coupler_shoulder_len

    coupler_fitting_h = coupler_fitting_len + delta
    coupler_fitting_shift = -(coupler_shoulder_len + coupler_fitting_len)

    wall_th = 2.0
    hole_len = coupler_shoulder_len + coupler_extra + coupler_fitting_len
    hole_h = hole_len + delta
    hole_diam = coupler_fitting_diam - 2 * wall_th
    hole_shift = -(coupler_shoulder_len + coupler_fitting_len + delta/2.)

def make_customizer():
    # For making scad file for use with Thingiverse Customizer
    global coupler_shoulder_diam
    global coupler_fitting_diam
    global coupler_shoulder_h, coupler_shoulder_shift
    global coupler_fitting_h, coupler_fitting_shift
    global hole_len, hole_h, hole_diam, hole_shift
    global OUTFILE
    OUTFILE = 'Customizable_hollow_egg_carrier_tmp.scad'
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

if 'direct' == FILEMODE.lower():
    make_direct()
elif 'customizer' == FILEMODE.lower():
    make_customizer()
else:
    raise ValueError("Unknown FILEMODE: {}".format(FILEMODE))

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
cav_df = pd.read_csv(PROF_INNER)
cav = sol.polygon(list(zip(cav_df['x'], cav_df['y'])))
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
# If we made a 'customizer' type of file, the variables have been preserved
# but are surrounded by double-quotes (") in the OpenSCAD file. These need
# to be stripped out for the file to work.
filestring = ''
if 'customizer' == FILEMODE.lower():
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

