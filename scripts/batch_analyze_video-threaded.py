import glob, os, argparse
import multiprocessing
from action.suite import *

ACTIONDIR = '/Volumes/ACTION'
NUM_PROCS = 4 # This is how many processes we want

def actionAnalyzeAll(clist, plist, olist):
	print "Inputlist received..."
	print clist
	print plist
	print olist
	print NUM_PROCS
	# create the pool
	pool = multiprocessing.Pool(NUM_PROCS)
	
#	# COMMENT OUT LINES HERE TO SKIP ANALYSIS TYPES
#	if len(clist) > 0:
#		pool.map(actionCFLabWorker, clist)
#	if len(plist) > 0:
#		pool.map(actionPCorrWorker, plist)
#	if len(olist) > 0:
#		pool.map(actionOFlowWorker, olist)


def actionCFLabWorker(cfile):
	cflab = ColorFeaturesLAB(cfile, action_dir=ACTIONDIR)
	print 'analyzing colors: ', (hfile + '.mov'), ' ', (cfile + '.color_lab')
	print 'action_dir=/Volumes/ACTION'
	cflab.analyze_movie()
	print 'DONE analyzing color features: ', (cfile + '.mov'), ' ', (cfile + '.color_lab')
	return 1

def actionPCorrWorker(pfile):
	pcorr = PhaseCorrelation(pfile, action_dir=ACTIONDIR)
	print 'analyzing phasecorr: ', (pfile + '.mov'), ' ', (pfile + '.phasecorr')
	print 'action_dir=/Volumes/ACTION'
	pcorr.analyze_movie()
	print 'DONE analyzing phasecorr: ', (pfile + '.mov'), ' ', (pfile + '.phasecorr')
	return 1

def actionOFlowWorker(ofile):
	oflow = OpticalFlow(ofile, action_dir=ACTIONDIR)
	print 'analyzing CFLab: ', (ofile + '.mov'), ' ', (ofile + '.opticalflow24')
	print 'action_dir=/Volumes/ACTION'
	oflow.analyze_movie()
	print 'DONE analyzing optical flow: ', (ofile + '.mov'), ' ', (ofile + '.opticalflow24')
	return 1

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("actiondir")
	parser.add_argument("numprocs")
	args = parser.parse_args()

	print args
	print args.actiondir
	
	if args.actiondir is not None:
		ACTIONDIR = args.actiondir
	if args.numprocs is not None:
		NUM_PROCS = args.numprocs

	# if we have some args, use them

	os.chdir(ACTIONDIR)
	names = [os.path.dirname(file) for file in glob.glob('*/*.mov')]
	names_with_proper_cflab_exts = glob.glob('*/*.color_lab')
	just_names_of_cflabs = [os.path.dirname(file) for file in names_with_proper_cflab_exts]
	names_with_proper_pcorr_exts = glob.glob('*/*.phasecorr')
	just_names_of_pcorrs = [os.path.dirname(file) for file in names_with_proper_pcorr_exts]
	names_with_proper_oflow_exts = glob.glob('*/*.opticalflow24')
	just_names_of_oflows = [os.path.dirname(file) for file in names_with_proper_oflow_exts]

	cflabs_to_analyze = set(names).difference(set(just_names_of_cflabs))
	pcorrs_to_analyze = set(names).difference(set(just_names_of_pcorrs))
	oflows_to_analyze = set(names).difference(set(just_names_of_oflows))

	print ''
	print cflabs_to_analyze
	print "(", len(cflabs_to_analyze), ")"
	print ''
	print pcorrs_to_analyze
	print "(", len(pcorrs_to_analyze), ")"
	print ''
	print oflows_to_analyze
	print "(", len(oflows_to_analyze), ")"
	print ''

	# Call the mainfunction that sets up threading.
	actionAnalyzeAll(cflabs_to_analyze, pcorrs_to_analyze, oflows_to_analyze)
