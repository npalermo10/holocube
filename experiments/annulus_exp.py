# horizon test with rotation

import holocube.hc5 as hc5
from numpy import *
from holocube.tools import mseq

# horizon test
expi = 1

# how long for the exp?
numframes = 500

# how fast is forward velocity and horizontal translational velocities, triangle wav velocity?
fwd_v = 0.01
trng_wav_v = 0.05
tampl = 0.05

# where should our theta boundaries be?
theta_ranges = [[0.0, 0.89566479385786502],
                [0.89566479385786502, 1.318116071652818],
                [1.318116071652818, 1.696124157962962],
                [1.696124157962962, 2.0943951023931957]]

def calc_theta(x,y,z):
    '''from cartesian coords return spherical coords declination theta (pi - theta)'''
    r = sqrt(x**2 + y**2 + z**2)
    theta = pi - arccos(z/r)
    return theta

def inds_btw_thetas(coords_array, theta_min, theta_max):
    ''' check if coords in range of thetas. return frame and point inds for which wn should be active '''
    for frame in coords_array:
        for point in arange(len(coords_array[0][0])):
            if theta_min <= calc_theta(frame[0][point], frame[1][point], frame[2][point]) <= theta_max:
                frame[3][point] = 1
            else:
                frame[3][point] = 0
    return array([frame[3] for frame in coords_array], dtype='bool')

def hrz_trngl_wv(number_frames, wav_freq = 0.5, cpu_freq = 120):
    ''' triangular wave function '''
    frames_p_cycle = cpu_freq/wav_freq
    frame_shift = int(frames_p_cycle/4)
    curr_frame = frame_shift
    trans = zeros(number_frames)
    while curr_frame < (number_frames + frame_shift):
        if curr_frame%frames_p_cycle <= frames_p_cycle/2:
            trans[curr_frame- frame_shift]= 1
        if curr_frame%frames_p_cycle > frames_p_cycle/2:
            trans[curr_frame-frame_shift]= -1
        curr_frame += 1
    return trans
    
# motions
wn0 = mseq(2,9,0,1)
wn1 = mseq(2,9,0,2)
wn2 = mseq(2,9,0,3)
wn3 = mseq(2,9,0,4)
tr_wav = hrz_trngl_wv(numframes, 0.5, 120)


# a set of points
pts = hc5.stim.Points(hc5.window, 5000, dims=[[-2,2],[-2,2],[-30,5]], color=.5, pt_size=3)

# simulation to calculate points in frames that are between thetas
coords_over_t = zeros([numframes, 4, pts.num]) 

# add fwd_v position to each z coordinate
coords_over_t[0] = [pts.coords[0] , pts.coords[1], pts.coords[2], [0]*pts.num]
for frame in arange(1, numframes):
    coords_over_t[frame] = array([pts.coords[0], pts.coords[1], coords_over_t[frame-1][2] + fwd_v, [0]*pts.num])

act_inds = array([inds_btw_thetas(coords_over_t, t_range[0], t_range[1]) for t_range in theta_ranges])

# lights
lights0 = array([(0,175+wn*80,0) for wn in wn0], dtype='int')
lights0[-1] = array([0, 0, 0])

lights1 = array([(0,175+wn*80,0) for wn in wn1], dtype='int')
lights1[-1] = array([0, 0, 0])

lights2 = array([(0,175+wn*80,0) for wn in wn2], dtype='int')
lights2[-1] = array([0, 0, 0])

lights3 = array([(0,175+wn*80,0) for wn in wn3], dtype='int')
lights3[-1] = array([0, 0, 0])

tr_lights = array([(0, 175 + step*80, 0) for step in tr_wav], dtype='int') 

orig_x = pts.coords[0, :].copy()
select_all = array([True]*pts.num)

hc5.scheduler.add_exp()

## experiments

##################### all angles wn #########################
expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[0], wn0*tampl],
           [pts.subset_inc_px,  act_inds[1], wn1*tampl],
           [pts.subset_inc_px,  act_inds[2], wn2*tampl],
           [pts.subset_inc_px,  act_inds[3], wn3*tampl],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, lights1]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.set_ref, 1, [0,0,0]],
           [hc5.window.reset_pos, 1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)


################### single angle wn #########################
expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[0], wn1*tampl],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, lights0]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.set_ref, 1, [0,0,0]],
           [hc5.window.reset_pos, 1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)


expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[1], wn1*tampl],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, lights1]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.reset_pos, 1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)



expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[2], wn1*tampl],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, lights2]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.reset_pos, 1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)



expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[3], wn1*tampl],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, lights3]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.reset_pos, 1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)


####################### triangle waves #########################################
expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[0], tr_wav*trng_wav_v],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, tr_lights]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.set_ref, 1, [0,0,0]],
           [hc5.window.reset_pos, 1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)



expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[1], tr_wav * trng_wav_v],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, tr_lights]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.reset_pos, 1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)



expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[2], tr_wav*trng_wav_v],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, tr_lights]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.reset_pos, 1]]
hc5.scheduler.add_test(numframes, starts, middles, ends)



expnumspikes = hc5.tools.test_num_flash(expi, numframes)
starts =  [[pts.on,            1],
           # [hc5.window.set_far,  100],
           [hc5.window.set_bg,  [0.0,0.0,0.0,1.0]]]

middles = [[pts.inc_pz,        fwd_v],
           [pts.subset_inc_px,  act_inds[3], tr_wav],
           [hc5.window.set_ref, 0, expnumspikes],
           [hc5.window.set_ref, 1, tr_lights]]

ends =    [[pts.on,            0],
           [pts.inc_pz, -fwd_v*numframes],
           [pts.subset_set_px, select_all, orig_x ],
           [hc5.window.reset_pos, 1]]
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

