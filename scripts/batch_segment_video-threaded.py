import glob, os, argparse
import action.segment as aseg
from action import *
import numpy as np
import bregman.features as features
from bregman.suite import *
from mvpa2.suite import *
import pprint, pickle
import multiprocessing

ACTION_DIR = '/Volumes/ACTION/'
# ACTION_DIR = '/Users/kfl/Movies/action'

def actionAnalyzeAll(inputlist, proc_limit):
	print "Inputlist received..."
	print inputlist
	# create the pool
	pool = multiprocessing.Pool(proc_limit)
	pool.map(actionWorker, inputlist)


def actionWorker(title):	
	
	ad = actiondata.ActionData()
	ds_segs_mb, ds_segs_mfccs, ds_segs_combo = [], [], []
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	actual_fps = cfl._read_json_value('fps')
	# reinstantiate cfl with the proper fps for access
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR, fps=actual_fps)

	print '----------------------------------'
	print title
	print ''

	length = cfl.determine_movie_length() # in seconds
	length_in_frames = length * 4

	full_segment = aseg.Segment(0, duration=length)
	Dmb = cfl.middle_band_color_features_for_segment(full_segment)
	# if abFlag is True: Dmb = cfl.convertLabToL(Dmb)
	
	Dmfccs = ad.meanmask_data(adb.read(os.path.join(ACTION_DIR, title, (title + '.mfcc'))))
	Dmfccs = ad.normalize_data(Dmfccs)
	Dmfccs = ad.meanmask_data(Dmfccs)
	
	# print Dmb.shape
	print Dmfccs.shape
	print Dmfccs.min()
	print Dmfccs.max()

	# print np.isnan(Dmb).any()
	print np.isnan(Dmfccs).any()
	# print np.isnan(Dcombo).any()

	min_length = min(Dmb.shape[0], Dmfccs.shape[0])

	Dcombo = np.c_[Dmb[:min_length,:], Dmfccs[:min_length,:]]

	nc = length_in_frames / 10
	print nc
	print "----------------------------"

	if not np.isnan(Dmb).any():
		outfile_mb = open(os.path.expanduser(os.path.join(ACTION_DIR, title, (title+'_cfl_hc.pkl'))), 'wb')
		decomposed_mb = ad.calculate_pca_and_fit(Dmb, locut=0.0001)
		print "<<<<  ", decomposed_mb.shape
		hc_assigns_mb = ad.cluster_hierarchically(decomposed_mb, nc, None)
		segs_mb = ad.convert_clustered_frames_to_segs(hc_assigns_mb, nc)
		segs_mb.sort()
		for seg in segs_mb:
			ds_segs_mb += [aseg.Segment(
				seg[0]*0.25,
				duration=(seg[1]*0.25),
				features=np.mean(Dmb[seg[0]:(seg[0]+seg[1]),:],axis=0))]
		pickle.dump(ds_segs_mb, outfile_mb, -1)
		outfile_mb.close()
	
	if not np.isnan(Dmfccs).any():
		outfile_mfccs = open(os.path.expanduser(os.path.join(ACTION_DIR, title, (title+'_mfccs_hc.pkl'))), 'wb')
		decomposed_mfccs = ad.calculate_pca_and_fit(Dmfccs, locut=0.001)
		print "<<<<  ", decomposed_mfccs.shape
		hc_assigns_mfccs = ad.cluster_hierarchically(decomposed_mfccs, nc, None)
		segs_mfccs = ad.convert_clustered_frames_to_segs(hc_assigns_mfccs, nc)
		segs_mfccs.sort()
		for seg in segs_mfccs:
			ds_segs_mfccs += [aseg.Segment(
				seg[0]*0.25,
				duration=(seg[1]*0.25),
				features=np.mean(Dmfccs[seg[0]:(seg[0]+seg[1]),:],axis=0))]
		pickle.dump(ds_segs_mfccs, outfile_mfccs, -1)
		outfile_mfccs.close()

	if not np.isnan(Dcombo).any():
		outfile_combo = open(os.path.expanduser(os.path.join(ACTION_DIR, title, (title+'_combo_hc.pkl'))), 'wb')
		decomposed_combo = ad.calculate_pca_and_fit(Dcombo, locut=0.0001)	
		print "<<<<  ", decomposed_combo.shape
		hc_assigns_combo = ad.cluster_hierarchically(decomposed_combo, nc, None)
		segs_combo = ad.convert_clustered_frames_to_segs(hc_assigns_combo, nc)
		segs_combo.sort()
		for seg in segs_combo:
			ds_segs_combo += [aseg.Segment(
				seg[0]*0.25,
				duration=(seg[1]*0.25),
				features=np.mean(Dcombo[seg[0]:(seg[0]+seg[1]),:],axis=0))]
		pickle.dump(ds_segs_combo, outfile_combo, -1)
		outfile_combo.close()

	# 	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4, length_in_frames)
	# 	hc_assigns = ad.cluster_hierarchically(sliding_averaged, nc, None)
	
	# clean up
	del Dmb
	del Dmfccs
	del Dcombo
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
	
	names = [os.path.dirname(file) for file in glob.glob('*/*.mfcc')]
	#names_with_proper_pkl_exts = [os.path.dirname(file) for file in glob.glob('*/*_cfl_hc.pkl')]
	
	to_be_pickled = [ttl for ttl in names]	
	print ''
	print to_be_pickled
	print "(", len(to_be_pickled), ")"
	print ''
	# Call the mainfunction that sets up threading
	actionAnalyzeAll(to_be_pickled, int(args.proclimit))
