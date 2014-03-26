#########################################################################################
# change the ACTIONRESDIR to the subdirectory in your results directory that you want to average over
#
# call like so: python batch_summarize_results -d ~/actionresults/SPECIFIC_FOLDER
#
# - this script will unpack your metadata from each pickled file--data is stored in one dict per pkl file
# - this script may be adapted easily for files/dicts that each contain an array of results from multiple analysis runs

import pickle, os, glob, sys, getopt
from mvpa2.suite import *
import numpy as np
from action.suite import *
import pylab as P

def main(argv):

	av = ad.ActionView()
	try:
		opts, args = getopt.getopt(argv,"d:")
	except getopt.GetoptError:
		print 'batch_summarize_results -d PATH-TO-ACTIONRESULTS-DIR'
		sys.exit(2)

	print "OPTS: ", opts
	ACTIONRESDIR = opts[0][1]
	print "ACTIONRESDIR: ", ACTIONRESDIR

	N = 0
	directors = ['AH', 'AK', 'CB', 'DL', 'JF', 'JLG', 'LB', 'SS']
	dnum = 8
	tp_rate_grids = np.array([], dtype=np.float32)
	accs = np.array([], dtype=np.float32)

	for file in glob.glob( os.path.join(ACTIONRESDIR, "*.pkl")):

		pklfile=open(os.path.join(ACTIONRESDIR, os.path.basename(file)), "rb")
		data = pickle.load(pklfile)
		pklfile.close()
		samples_per = int(data['samples_per']) * int(data['samplings_per_title'])
		N += 1
		print ":::::>>>", data['results'].matrix
		tp_rate_grids = np.append(np.atleast_2d(tp_rate_grids), np.array([(data['results'].matrix / float(samples_per * dnum))]))

		print "num:  ", N, " --> true pos. rate grids: ", tp_rate_grids

		accs = np.append(accs, np.array([data['results'].stats['ACC']]))

		del data

	tp_rate_grids = np.reshape(tp_rate_grids, (-1,dnum,dnum))
	accs_mean = accs.mean()
	accs_stderror = accs.std() / (dnum ** 0.5)

	titlestring=('{:d}-Directors Task ({:d} runs) - means\nMean Accuracy: {:3.3f}; Standard error of mean: {:3.3f}'.format(dnum, N, accs_mean, accs_stderror))
	fig = av.imagesc2(tp_rate_grids.mean(axis=0), str=titlestring, txt=1, txtsz=9, txtprec=2,cmap=P.cm.coolwarm, labels=directors) #, stats=statstring)
	fig.savefig(ACTIONRESDIR+str(N)+"_pools_means.png")

	titlestring=('{:d}-Directors Task ({:d} runs) - errors\nMean Accuracy: {:3.3f}; Standard error of mean: {:3.3f}'.format(dnum, N, accs_mean, accs_stderror))
	fig2 = av.imagesc2((tp_rate_grids.std(axis=0) / (dnum ** 0.5)), str=titlestring, txt=1, txtsz=9, txtprec=2,cmap=P.cm.coolwarm, labels=directors) #, stats=statstring)
	fig2.savefig(ACTIONRESDIR+str(N)+"_pools_error.png")


if __name__ == "__main__":
   main(sys.argv[1:])