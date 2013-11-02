import glob, os, argparse
import bregman.segment as bseg
from action import *
import numpy as np
import bregman.features as features
from mvpa2.suite import *
import pprint, pickle

import multiprocessing
# ACTION_DIR = '/Volumes/ACTION/'
ACTION_DIR = '/Users/kfl/Movies/action/'
WITH_METADATA = True

def actionAnalyzeAll(inputlist, proc_limit):
	print "Inputlist received..."
	print inputlist
	# create the pool
	pool = multiprocessing.Pool(proc_limit)
	pool.map(actionWorker, inputlist)


def actionWorker(title):
	ds_segs = []
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	if WITH_METADATA:
		outfile = open(os.path.expanduser(os.path.join(cfl.analysis_params['action_dir'], title, (title+'_cfl_hc_full.pkl'))), 'wb')
	else:
		outfile = open(os.path.expanduser(os.path.join(cfl.analysis_params['action_dir'], title, (title+'_cfl_hc.pkl'))), 'wb')
	
	length = cfl.determine_movie_length() # in seconds
	length_in_frames = length * 4

	full_segment = bseg.Segment(0, duration=length)
	Dmb = cfl.middle_band_color_features_for_segment(full_segment)
	# if abFlag is True: Dmb = cfl.convertLabToL(Dmb)

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(Dmb, locut=0.0001)
	print "<<<<  ", decomposed.shape
# 	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4, length_in_frames)

	nc = length_in_frames / 10
# 	hc_assigns = ad.cluster_hierarchically(sliding_averaged, nc, None)
	hc_assigns = ad.cluster_hierarchically(decomposed, nc, None)
	segs = ad.convert_clustered_frames_to_segs(hc_assigns, nc)
	segs.sort()
	del segs[0]

	if WITH_METADATA:
		for seg in segs:
			if seg[0] > 0:
				ds_segs += [bseg.Segment(
					seg[0]*0.25,
					duration=(seg[1]*0.25),
					features=np.mean(Dmb[seg[0]:(seg[0]+seg[1]),:],axis=0))]
	else:
		for seg in segs:
			if seg[1] > 0:
				ds_segs += [{'onset': seg[0], 'duration': seg[1]}]

	print len(ds_segs)
	pickle.dump(ds_segs, outfile, -1)
	outfile.close()
	return 1

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("actiondir")
	parser.add_argument("proclimit")
	args = parser.parse_args()

	print args
	print args.actiondir
	ACTION_DIR = args.actiondir
	print args.proclimit

	# if we have some args, use them

	os.chdir(ACTION_DIR)
	names = [os.path.dirname(file) for file in glob.glob('*/*.color_lab')]
	if WITH_METADATA:
		names_with_proper_pkl_exts = [os.path.dirname(file) for file in glob.glob('*/*_cfl_hc_full.pkl')]
	else:
		names_with_proper_pkl_exts = [os.path.dirname(file) for file in glob.glob('*/*_cfl_hc.pkl')]
	to_be_pickled = [ttl for ttl in names if ttl not in set(names_with_proper_pkl_exts)]	
	print ''
	print to_be_pickled
	print "(", len(to_be_pickled), ")"
	print ''
	# Call the mainfunction that sets up threading
	actionAnalyzeAll(to_be_pickled, int(args.proclimit))
