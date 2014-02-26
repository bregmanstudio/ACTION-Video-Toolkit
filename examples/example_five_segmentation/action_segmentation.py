import glob, os, argparse, math
from action import *
import numpy as np
import action.segment as aseg
from bregman.suite import *
# from mvpa2.suite import *
import pprint, pickle

ACTION_DIR = os.path.expanduser('~/Movies/action/')

# onset (fraction)
# dur
# frame desity (fraction) target ratio of frames to # of segments
def actionSegmenterHC(title, onset_ratio=0.0, dur_ratio=1.0, frame_density=0.1):
	ds_segs = []
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	outfile = open(os.path.expanduser(os.path.join(cfl.analysis_params['action_dir'], title, (title+'_cfl_hc.pkl'))), 'wb')

	length = cfl.determine_movie_length() # in seconds
	print ''
	print length
	print ''
	length_in_frames = length * 4

	full_segment = aseg.Segment(int(onset_ratio*length), duration=int(dur_ratio*length))
	print full_segment
	Dmb = cfl.middle_band_color_features_for_segment(full_segment)
	# if abFlag is True: Dmb = cfl.convertLabToL(Dmb)

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(Dmb, locut=0.0001)
	print "<<<<  ", decomposed.shape

	nc = int(math.floor(length_in_frames * frame_density)) - 1
	print ' NC:>> ', nc

	hc_assigns = ad.cluster_hierarchically(decomposed, nc, None)
	segs = ad.convert_clustered_frames_to_segs(hc_assigns, nc)
	segs.sort()
	print segs[0]
	# del segs[0] #???
	
	for seg in segs:
		ds_segs += [aseg.Segment(
			seg[0]*0.25, 
	    	seg[1]*0.25, 
			features=np.mean(Dmb[seg[0]:(seg[0]+seg[1]),:],axis=0))]
	return ds_segs, hc_assigns, hc_assigns.max()

# kmeans functions can be used as well...
# def actionSegmenterKM(title, onset=0.0, frame_density=0.1):
# 	ds_segs = []
# 	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
# 	outfile = open(os.path.expanduser(os.path.join(cfl.analysis_params['action_dir'], title, (title+'_cfl_hc.pkl'))), 'wb')
# 
# 	length = cfl.determine_movie_length() # in seconds
# 	length_in_frames = length * 4
# 
# 	full_segment = aseg.Segment(int(onset*length), duration=int(frame_density*length))
# 	Dmb = cfl.middle_band_color_features_for_segment(full_segment)
# 	# if abFlag is True: Dmb = cfl.convertLabToL(Dmb)
# 
# 	ad = actiondata.ActionData()
# 	decomposed = ad.calculate_pca_and_fit(Dmb, locut=0.0001)
# 	print "<<<<  ", decomposed.shape
# # 	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4, length_in_frames)
# 
# 	nc = int(length_in_frames * frame_density * 0.1)
# # 	hc_assigns = ad.cluster_hierarchically(sliding_averaged, nc, None)
# 	km_assigns, km_max = ad.cluster_k_means(decomposed, nc)
# 	segs = ad.convert_clustered_frames_to_segs(km_assigns, km_max)
# 	segs.sort()
# 	del segs[0]
# 	
# 	for seg in segs:
# 		ds_segs += [aseg.Segment(
# 			seg[0]*0.25, 
# 			seg[1]*0.25, 
# 			features=np.mean(Dmb[seg[0]:(seg[0]+seg[1]),:],axis=0))]
# 	
# 	return ds_segs, km_assigns, km_max
# def actionSegmenterKM2(title, onset=0.0, frame_density=0.1):
# 	ds_segs = []
# 	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
# 	oflow = opticalflow24.OpticalFlow24(title, action_dir=ACTION_DIR)
# 
# 	length = cfl.determine_movie_length() # in seconds
# 	length_in_frames = length * 4
# 	full_segment = aseg.Segment(int(onset*length), duration=int(fract*length))
# 	print full_segment.time_span.duration
# 	Dmb = cfl.middle_band_color_features_for_segment(full_segment)
# 	# if abFlag is True: Dmb = cfl.convertLabToL(Dmb)
# 	Dof = oflow.opticalflow_for_segment_with_stride(full_segment, access_stride=6)
# 	
# 	print Dmb.shape
# 	print Dof.shape
# 
# 	ad = actiondata.ActionData()
# 	decomposed = ad.calculate_pca_and_fit(np.c_[Dmb, Dof], locut=0.0001)
# 	print "<<<<  ", decomposed.shape
# # 	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4, length_in_frames)
# 
# 	nc = int(length_in_frames * fract * 0.1)
# # 	hc_assigns = ad.cluster_hierarchically(sliding_averaged, nc, None)
# 	km_assigns, km_max = ad.cluster_k_means(decomposed, nc)
# 	segs = ad.convert_clustered_frames_to_segs(km_assigns, km_max)
# 	segs.sort()
# 	del segs[0]
# 	
# 	for seg in segs:
# 		ds_segs += [aseg.Segment(
# 			seg[0]*0.25, 
# 			seg[1]*0.25, 
# 			features=np.mean(Dmb[seg[0]:(seg[0]+seg[1]),:],axis=0))]
# 	
# 	return ds_segs, km_assigns, km_max


dssegs, hc_assigns, hc_max = actionSegmenterHC('Vertigo', frame_density=0.1)

THRESH = 2.5
MIN_FRAMES = 10

data = np.array([seg.features for seg in dssegs])
imagesc(distance.euc2(data, data))

num_frames = data.shape[0]
sumdiffs = np.sqrt(np.sum(np.power(np.diff(data, axis=0), 2.0), axis=1))


cleaner = []
curr = -1*MIN_FRAMES

for val in np.argwhere(sumdiffs>THRESH):
        if (val[0] - curr) > MIN_FRAMES:
                cleaner += [val[0]]
        curr = val[0]

divs = []
for i in range(num_frames):
        try:
                cleaner.index(i)
                divs += [1]
        except ValueError:
                divs += [0]

plt.plot(divs)




from itertools import *
def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)

final_segs = []
i = 0
for a, b in pairwise(cleaner):
        new_start = dssegs[a].time_span.start_time
        new_dur = dssegs[b].time_span.start_time - dssegs[a].time_span.start_time
        new_med_feature = np.median(data[a:b], axis=0)
        print (new_start, new_dur,  new_med_feature.shape)
        final_segs += [aseg.Segment(label=i, start_time=new_start, duration=new_dur, features = new_med_feature)]
        i += 1

resegmented_data = np.array([seg.features for seg in final_segs])
imagesc(resegmented_data.T, title_string='Segmented features, no temporal structure')


counter = 0
final_segs_stack = final_segs[:]
final_resegmented = np.zeros(384, dtype=np.float32)
cfl = color_features_lab.ColorFeaturesLAB('Vertigo', action_dir=ACTION_DIR)

for i in range(0, int(cfl.determine_movie_length()), 60):
        # always concat
        try:
                print np.atleast_2d(final_resegmented).shape
                print np.atleast_2d(final_segs_stack[counter].features).shape
                final_resegmented = np.append(np.atleast_2d(final_resegmented), np.atleast_2d(final_segs_stack[counter].features), axis=0)
                if final_segs_stack[counter].time_span.start_time < i:
                        ##
                        counter += 1
        except IndexError:
                counter -= 1
                final_resegmented = np.append(np.atleast_2d(final_resegmented), np.atleast_2d(final_segs_stack[counter].features), axis=0)
        print '-- ', i
        print '>> ', counter

imagesc(final_resegmented.T, title_string='Segmented features (1 min. granularity)')


# Finally, let's see a segmented within-film similarity map
imagesc(distance.euc2(final_resegmented, final_resegmented), title_string='Similarity map based on segments')


# There can be a bit of a problem with white cells (nans); if so, we zero-mask nans
# distances = distance.euc2(final_resegmented, final_resegmented)
# distances = ad.zeromask_data(distances)
# imagesc(distances)


"""

###################

ad = actiondata.ActionData()
av = actiondata.ActionView()

vseg = 

## TITLE, start (percentage), duration (percentage)
dssegs, hc_assigns, hc_max = actionSegmenterHC('Vertigo', 0.0, 0.1)
aseg.cluster_plot(hc_assigns, hc_max)


## plot segments as arcs (reveals somewhat how the segmentor did its work)
diffs = np.where(np.r_[1,np.diff(hc_assigns),1])[0]
linkage_plot(hc_assigns, hc_max, diffs)


## plot segments from HC as similarity matrix
segmented_ds = []
for seg in dssegs:
	segmented_ds += [seg.features]
segmented_ds = np.array(segmented_ds)
ad.calculate_self_similarity_matrix(segmented_ds)
imagesc(ad.calculate_self_similarity_matrix(segmented_ds), title_string='Similarity of HC segments')


## plotting the segments
av.plot_hcluster_segments(dssegs[1], dssegs[2])
diffs = np.where(np.r_[1,np.diff(km_assigns),1])[0]


"""