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
# ACTION_DIR = '/Users/kfl/Movies/action/'

def actionAnalyzeAll(inputlist, proc_limit):
	print "Inputlist received..."
	print inputlist
	# create the pool
	pool = multiprocessing.Pool(proc_limit)
	pool.map(actionWorkerAudio, inputlist)


def actionWorkerAudio(title):

	ad = actiondata.ActionData()
	ds_segs = []
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	print cfl.analysis_params['action_dir']

	length = cfl.determine_movie_length() # in seconds
	length_in_frames = length * 4

	outfile = open(os.path.expanduser(os.path.join(ACTION_DIR, title, (title+'_mfccs_hc.pkl'))), 'wb')
	
	full_segment = aseg.Segment(0, duration=length)
	try:
		Dmfccs = adb.read(os.path.join(ACTION_DIR, title, (title + '.mfcc_13_M2_a0_C2_g0_i16000')))
	except TypeError:
		outfile.close()
		return 1

	decomposed = ad.meanmask_data(Dmfccs[:]) # ad.calculate_pca_and_fit(Dmfccs, locut=0)
	print "<<<<  ", decomposed.shape

	nc = length_in_frames / 10

	hc_assigns = ad.cluster_hierarchically(decomposed, nc, None)
	segs = ad.convert_clustered_frames_to_segs(hc_assigns, nc)

	segs.sort()
	del segs[0]

	for seg in segs:
		if seg[0] > 0:
			ds_segs += [aseg.Segment(
				seg[0]*0.25,
				duration=(seg[1]*0.25),
				features=np.mean(Dmfccs[seg[0]:(seg[0]+seg[1]),:],axis=0))]

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
	names = [os.path.dirname(file) for file in glob.glob('*/*.mfcc*')]
	names_with_proper_pkl_exts = [os.path.dirname(file) for file in glob.glob('*/*_mfccs_hc.pkl')]
	
	to_be_pickled = [ttl for ttl in names if ttl not in set(names_with_proper_pkl_exts)]	
	print ''
	print to_be_pickled
	print "(", len(to_be_pickled), ")"
	print ''
	# Call the mainfunction that sets up threading
	actionAnalyzeAll(to_be_pickled, int(args.proclimit))
