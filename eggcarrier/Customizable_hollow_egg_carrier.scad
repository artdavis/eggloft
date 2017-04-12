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
// Coupler Fraction
coupler_fract = 0.4; // [0.0:0.05:1.0]
// Coupler Thickness
coupler_th = 2.0; // [0.0:0.2:4.0]

/* [Hidden] */
// Special variables for facets/arcs
$fn = 48;

// Incremental offset to make good overlap for CSG operations
delta = 0.1;

// Coupler extension to overlap with egg shell
coupler_extra = 50.0;

// Number of steps to sample the half profile of the shell
steps = 100;


// Egg profile computing function
function egg(x, l=case_length)= 0.9*l*pow(1-x/l, 2/3)*sqrt(1-pow(1-x/l, 2/3));

// Create egg profile
module egg_profile(length=case_length, offset=0, steps=steps) {
    ss = length / (steps-1); // step size
    v1 = [for (x=[0:ss:length]) [egg(x, length), x + offset]];
    // Make absolute sure the last point bring the profile
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

// Create shell coupling feature
// thick: Thickness of the coupling feature
// fract: Fraction of shell to cover with coupling feature (between 0 and 1)
module shell_coupler(length=case_length, offset=0,
                     thick=coupler_th, fract=coupler_fract, steps=steps) {
    rotate(a=[90,0,-90]){
        difference() {
            union() {
                linear_extrude(height=thick, convexity=10) {
                    egg_profile(length=length, offset=offset, steps=steps);}
                mirror(v=[1, 0, 0]) {
                    linear_extrude(height=thick, convexity=10) {
                        egg_profile(length=length, offset=offset, steps=steps);}
                }
            }
        cube(size=[200, 2*(1-fract)*length, 200], center=true);
        }
    }
}

rotate(a = [0, 90.0000000000, 0])
{
	difference() {
		difference() {
			union() {
                shell_coupler(length=case_length + 2*coupler_th,
                              offset=-coupler_th, fract=coupler_fract);
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
