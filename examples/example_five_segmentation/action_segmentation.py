import glob, os, argparse
import bregman.segment as bseg
from action import *
import numpy as np
import bregman.features as features
import bregman.segment as bseg
from bregman.suite import *
from mvpa2.suite import *
import pprint, pickle

ACTION_DIR = '/Users/kfl/Movies/action/'

def actionSegmenterHC(title, onset=0.0, fract=0.1):
	ds_segs = []
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	outfile = open(os.path.expanduser(os.path.join(cfl.analysis_params['action_dir'], title, (title+'_cfl_hc.pkl'))), 'wb')

	length = cfl.determine_movie_length() # in seconds
	print ''
	print length
	print ''
	length_in_frames = length * 4

	full_segment = bseg.Segment(int(onset*length), duration=int(fract*length))
	print full_segment
	Dmb = cfl.middle_band_color_features_for_segment(full_segment)
	# if abFlag is True: Dmb = cfl.convertLabToL(Dmb)

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(Dmb, locut=0.0001)
	print "<<<<  ", decomposed.shape
# 	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4, length_in_frames)

	nc = int(length_in_frames * fract * 0.001)
	print '>>'
	print nc
# 	hc_assigns = ad.cluster_hierarchically(sliding_averaged, nc, None)
	hc_assigns = ad.cluster_hierarchically(decomposed, nc, None)
	segs = ad.convert_clustered_frames_to_segs(hc_assigns, nc)
	segs.sort()
	del segs[0]
	
	for seg in segs:
		ds_segs += [bseg.Segment(
			seg[0]*0.25, 
	    	seg[1]*0.25, 
			features=np.mean(Dmb[seg[0]:(seg[0]+seg[1]),:],axis=0))]
	return ds_segs, hc_assigns, hc_assigns.max()

def actionSegmenterKM(title, onset=0.0, fract=0.1):
	ds_segs = []
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	outfile = open(os.path.expanduser(os.path.join(cfl.analysis_params['action_dir'], title, (title+'_cfl_hc.pkl'))), 'wb')

	length = cfl.determine_movie_length() # in seconds
	length_in_frames = length * 4

	full_segment = bseg.Segment(int(onset*length), duration=int(fract*length))
	Dmb = cfl.middle_band_color_features_for_segment(full_segment)
	# if abFlag is True: Dmb = cfl.convertLabToL(Dmb)

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(Dmb, locut=0.0001)
	print "<<<<  ", decomposed.shape
# 	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4, length_in_frames)

	nc = int(length_in_frames * fract * 0.1)
# 	hc_assigns = ad.cluster_hierarchically(sliding_averaged, nc, None)
	km_assigns, km_max = ad.cluster_k_means(decomposed, nc)
	segs = ad.convert_clustered_frames_to_segs(km_assigns, km_max)
	segs.sort()
	del segs[0]
	
	for seg in segs:
		ds_segs += [bseg.Segment(
			seg[0]*0.25, 
			seg[1]*0.25, 
			features=np.mean(Dmb[seg[0]:(seg[0]+seg[1]),:],axis=0))]
	
	return ds_segs, km_assigns, km_max


def actionSegmenterKM2(title, onset=0.0, fract=0.1):
	ds_segs = []
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	oflow = opticalflow24.OpticalFlow24(title, action_dir=ACTION_DIR)

	length = cfl.determine_movie_length() # in seconds
	length_in_frames = length * 4
	full_segment = bseg.Segment(int(onset*length), duration=int(fract*length))
	print full_segment.time_span.duration
	Dmb = cfl.middle_band_color_features_for_segment(full_segment)
	# if abFlag is True: Dmb = cfl.convertLabToL(Dmb)
	Dof = oflow.opticalflow_for_segment_with_stride(full_segment, access_stride=6)
	
	print Dmb.shape
	print Dof.shape

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(np.c_[Dmb, Dof], locut=0.0001)
	print "<<<<  ", decomposed.shape
# 	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4, length_in_frames)

	nc = int(length_in_frames * fract * 0.1)
# 	hc_assigns = ad.cluster_hierarchically(sliding_averaged, nc, None)
	km_assigns, km_max = ad.cluster_k_means(decomposed, nc)
	segs = ad.convert_clustered_frames_to_segs(km_assigns, km_max)
	segs.sort()
	del segs[0]
	
	for seg in segs:
		ds_segs += [bseg.Segment(
			seg[0]*0.25, 
			seg[1]*0.25, 
			features=np.mean(Dmb[seg[0]:(seg[0]+seg[1]),:],axis=0))]
	
	return ds_segs, km_assigns, km_max




###################

ad = actiondata.ActionData()
av = actiondata.ActionView()

## TITLE, start (percentage), duration (percentage)
dssegs, hc_assigns, hc_max = actionSegmenterHC('Vertigo', 0.0, 0.1)
cluster_plot(hc_assigns, hc_max)


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


