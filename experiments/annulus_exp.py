# horizon test with rotation

import holocube.hc5 as hc5
from numpy import *
from holocube.tools import mseq

# horizon test
expi = 1

# how long for the exp?
numframes = 1023

# how fast is forward velocity?
fwd_v = 0.00

# in which theta range should lateral wn be active?
theta_range = [pi-arcsin(1),pi-arcsin(.97),pi-arcsin(.87),pi-arcsin(.66), pi- arcsin(0)]

def calc_theta(x,y,z):
    '''from cartesian coords return spherical coords theta'''
    r = sqrt(x**2 + y**2 + z**2)
    theta = arccos(z/r)
    return theta
    
# a set of points
pts = hc5.stim.Points(hc5.window, 5000, dims=[[-2,2],[-2,2],[-30,5]], color=.5, pt_size=3)

# simulation to calculate frames within thetas
coords_over_t = zeros([numframes, 4, pts.num]) 

## add fwd_v position to each z coordinate
coords_over_t[0] = [pts.coords[0] , pts.coords[1], pts.coords[2], [0]*pts.num]
for frame in arange(1, numframes):
    coords_over_t[frame] = array([pts.coords[0], pts.coords[1], coords_over_t[frame-1][2] + fwd_v, [0]*pts.num])

## check if coords in range of thetas
for frame in coords_over_t:
    for point in arange(pts.num):
        if theta_range[0] <= calc_theta(frame[0][point], frame[1][point], frame[2][point]) <= theta_range[1]:
            frame[3][point] = 1

act_inds = array([frame[3] for frame in coords_over_t], dtype='bool') ## frame and point indexes for which wn should be active           
        
# the wn motion
# wn1 = cumsum(mseq(2,10,0,1))
wn1 = mseq(2,9,0,1)
wn1_dir = array(sign(ediff1d(wn1,None, 0)), dtype='int')

lights1 = mod(cumsum(wn1_dir),3)
lights1 = array([[0,e*127,0] for e in lights1])
lights1[-1] = 0

tampl = .05
rampl = 1
hc5.scheduler.add_exp()

## experiments
expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds, wn1*tampl],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, lights1]]

ends =    [[pts.on,            0],
           [hc5.window.reset_pos, 1],
           [pts.shuffle,       1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)

# add the rest
num_frames = 300
rbar = hc5.stim.cbarr_class(hc5.window, dist=1)

starts =  [[hc5.window.set_far,         2],
           [hc5.window.set_bg,          [0.0,0.0,0.0,1.0]],
           [hc5.arduino.set_lmr_scale,  -.1],
           [rbar.set_ry,               0],
           [rbar.switch,               True] ]
middles = [[rbar.inc_ry,               hc5.arduino.lmr]]
ends =    [[rbar.switch,               False],
           [hc5.window.set_far,         2]]
 
hc5.scheduler.add_rest(num_frames, starts, middles, ends)

