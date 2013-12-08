import glob, os, argparse
import bregman.segment as seg
from action import *
import action

import multiprocessing

ACTIONDIR = '/Volumes/ACTION'

PROC_LIMIT = 4                # This is how many processes we want


def actionAnalyzeAll(hlist, plist, olist):
	print "Inputlist received..."
	print hlist
	print plist
	print olist
	# create the pool
	pool = multiprocessing.Pool(PROC_LIMIT)
	pool.map(actionHistWorker, hlist)
	pool.map(actionPCorrWorker, plist)
	pool.map(actionOFlowWorker, olist)


def actionHistWorker(hfile):
	hist = action.color_features_lab.ColorFeaturesLAB(hfile, action_dir=ACTIONDIR)
	print 'analyzing colors: ', (hfile + '.mov'), ' ', (hfile + '.color_lab')
	print 'action_dir=/Volumes/ACTION'
	hist.analyze_movie()
	print 'DONE analyzing color features: ', (hfile + '.mov'), ' ', (hfile + '.color_lab')
	return 1

def actionPCorrWorker(pfile):
	pcorr = action.phase_correlation.PhaseCorrelation(pfile, action_dir=ACTIONDIR)
	print 'analyzing phasecorr: ', (pfile + '.mov'), ' ', (pfile + '.phasecorr')
	print 'action_dir=/Volumes/ACTION'
	pcorr.analyze_movie()
	print 'DONE analyzing phasecorr: ', (pfile + '.mov'), ' ', (pfile + '.phasecorr')
	return 1

def actionOFlowWorker(ofile):
	oflow = action.opticalflow.OpticalFlow(ofile, action_dir=ACTIONDIR)
	print 'analyzing histogram: ', (ofile + '.mov'), ' ', (ofile + '.opticalflow24')
	print 'action_dir=/Volumes/ACTION'
	oflow.analyze_movie()
	print 'DONE analyzing optical flow: ', (ofile + '.mov'), ' ', (ofile + '.opticalflow24')
	return 1

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("actiondir")
	args = parser.parse_args()

	print args
	print args.actiondir

	# if we have some args, use them

	os.chdir(args.actiondir)
	names = [os.path.dirname(file) for file in glob.glob('*/*.mov')]
	names_with_proper_hist_exts = glob.glob('*/*.color_lab')
	just_names_of_hists = [os.path.dirname(file) for file in names_with_proper_hist_exts]
	names_with_proper_pcorr_exts = glob.glob('*/*.phasecorr')
	just_names_of_pcorrs = [os.path.dirname(file) for file in names_with_proper_pcorr_exts]
	names_with_proper_oflow_exts = glob.glob('*/*.opticalflow24')
	just_names_of_oflows = [os.path.dirname(file) for file in names_with_proper_oflow_exts]

	hists_to_analyze = set(names).difference(set(just_names_of_hists))
	pcorrs_to_analyze = set(names).difference(set(just_names_of_pcorrs))
	oflows_to_analyze = set(names).difference(set(just_names_of_oflows))

	print ''
	print hists_to_analyze
	print "(", len(hists_to_analyze), ")"
	print ''
	print pcorrs_to_analyze
	print "(", len(pcorrs_to_analyze), ")"
	print ''
	print oflows_to_analyze
	print "(", len(oflows_to_analyze), ")"
	print ''

	# Call the mainfunction that sets up threading.
	actionAnalyzeAll(hists_to_analyze, pcorrs_to_analyze, oflows_to_analyze)
