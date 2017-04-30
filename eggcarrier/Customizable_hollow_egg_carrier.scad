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

// Optimize view for Makerbot Customizer:
// preview[view:south east, tilt:bottom]

// Length of the Egg Casing Shell
case_length = 78; // [60:2:100]
// Coupler Shoulder Length
coupler_shoulder_len = 6.0; // [1.0:1.0:25.0]
// Coupler Shoulder Diameter
coupler_shoulder_diam = 18.7; // [10.0:0.2:50.0]
// Fitting Shoulder Length
coupler_fitting_len = 12.0; // [5.0:1.0:25.0]
// Fitting Shoulder Diameter
coupler_fitting_diam = 17.9; // [10.0:0.2:50.0]
// Wall thickness
wall_th = 2.0; // [1.0:0.2:4.0]

boss_diam = 5;
pin_diam = 2.2;
pin_depth= 3.6;

/* [Hidden] */
// Special variables for facets/arcs
$fn = 48;

// Incremental offset to make good overlap for CSG operations
delta = 0.1;

// Coupler extension to overlap with egg shell
coupler_extra = 50.0;

// Number of steps to sample the half profile of the shell
steps = 100;

// X-coordinates for the studs
stud_xpts = [0.2 * case_length, 0.8 * case_length];

// Egg profile computing function
function egg(x, l=case_length)= 0.9*l*pow(1-x/l, 2/3)*sqrt(1-pow(1-x/l, 2/3));

// Create egg profile
module egg_profile(length=case_length, offset=0, steps=steps) {
    ss = length / (steps-1); // step size
    v1 = [for (x=[0:ss:length]) [egg(x, length), x + offset]];
    // Make absolute sure the last point brings the profile
    // back to the axis
    v2 = concat(v1, [[0, length + offset]]);
    // Close the loop
    v3 = concat(v2, [[0, offset]]);
        polygon(points = v3);
}

// Create a solid egg part
module solid_egg(length=case_length, offset=0, steps=steps) {
    rotate_extrude(convexity = 10) {
        egg_profile(length=length, offset=offset, steps=steps);
    }
}

// Create exterior shell trimming volume
module egg_trim(length=case_length, offset=0, steps=steps){
    difference() {
        translate(v = [-delta, -length*1.05, -delta]) {
            cube(size=2.1*length);
        }
        rotate(a = [0, 90.0000000000, 0]) {
            solid_egg(length=length, offset=offset, steps=steps);
        }
    }
}

module main_body() {
    rotate(a = [0, 90.0000000000, 0])
    {
        difference() {
            difference() {
                union() {
                    solid_egg(length=case_length, offset=0, steps=steps);
                    difference() {
                        union() {
                            translate(v = [0, 0, -coupler_shoulder_len]) {
                                cylinder(d = coupler_shoulder_diam,
                                         h = coupler_shoulder_len + coupler_extra);
                            }
                            translate(v = [0, 0,
                                    -(coupler_shoulder_len+coupler_fitting_len)]) {
                                cylinder(d = coupler_fitting_diam,
                                         h = coupler_fitting_len + delta);
                            }
                        }
                        translate(v = [0, 0,
                        -(coupler_shoulder_len + coupler_fitting_len + delta/2.)]) {
                            cylinder(d = coupler_fitting_diam - 2 * wall_th,
                                     h = coupler_shoulder_len + coupler_extra + coupler_fitting_len + delta);
                        }
                    }
                }
                solid_egg(case_length - 2*wall_th, wall_th);
            }
            translate(v = [0, -100.0000000000, -100.0000000000]) {
                cube(size = 200);
            }
        }
    }
}

module stud(loc_diam, cyl_diam, ht, x) {
    translate(v = [x + loc_diam/2, egg(x, case_length - loc_diam), 0]) {
        cylinder(h=ht, d=cyl_diam);
    }
    translate(v = [x + loc_diam/2, -egg(x, case_length - loc_diam), 0]) {
        cylinder(h=ht, d=cyl_diam);
    }
}

// Create boss features for mating the shell haves
module egg_boss() {
    difference() {
      union() {
          for(x = stud_xpts)stud(boss_diam, boss_diam, case_length, x);
            }
        egg_trim();
        }
    }

difference() {
    union() {
        main_body();
        egg_boss(diam=boss_diam);
    }
    for(x = stud_xpts)stud(boss_diam, pin_diam, pin_depth, x);
}