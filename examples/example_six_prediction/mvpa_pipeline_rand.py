## *Directors task overview*
## =========================
##


## .... IMPORTS
from action_imports import *
import pickle

## .... SET MACHINE PATH
ACTION_MOVIE_DIR = os.path.expanduser("~/Movies/action/")

## .... IMPORT DATABASE OF AUTEURS

##########################################################################################


def assemble_sample_data_and_crossvalidate(
	directors, 
	titles=None, 
	titles_per_director=1, 
	cflag=2, 
	samples_per=300, 
	classifier_num=0, 
	ftail=0.1,
	cval=-1,
	pklfile="~/actionresults/"):
	
	db  = FilmDB()
	dirttl_pool = db.create_analysis_pool(directors, cflag)
	
	res_md = dict()
	res_md['titles'] = dict()
	res_md['directors'] = dict() # these are the targets!
	for i, dir in enumerate(directors):
		res_md['directors'][i] = dir
	
	# create permutations of N directors
	if titles is None:
		total_num_samples = len(directors) * titles_per_director * samples_per
		titles = []
		for dir in sorted(dirttl_pool.keys()):
			titles += random.sample(dirttl_pool[dir], titles_per_director) # list should be flat
	else:
		total_num_samples = len(titles) * titles_per_director * samples_per
		# assume that titles has been populated with actual titles
	
	# multiple dirs with multiple titles each; split on all three quantities
	targets = [(i/(titles_per_director*samples_per)) for i in range(total_num_samples)]
	 
	for i, ttl in enumerate(titles):
		res_md['titles'][i] = ttl
	
	chunks = [(i/samples_per) for i in range(total_num_samples)]
	

	# 	... SET UP PICKLING
	pklfile = open(pklfile, 'wb')
	
	res_md['dnum']					=	str(1)
	res_md['pairing']				=	str(titles)
	res_md['samples_per'] 			= 	str(samples_per)
	
	# 	... PREPROCESS DATA *
	#	..- gathering	
	# 	..* get the midband color hist data for all titles, converting Lab to LXX
	datadict = ad.gather_color_feature_data(titles, ACTION_MOVIE_DIR, grid='midband', cflag=True)
	
	#		..- random frame sampling
	for title in datadict.keys():
		print datadict[title].shape
		datadict[title] = ad.sample_n_frames(datadict[title], n=samples_per)

	#		..- gather data into Numpy array
	# still in ORDER!!! NO NEED to sort them by title-string!
	X = np.zeros(titles[0].shape[1], dtype=np.float32)
	for title in titles:
		print '-----------------------'
		print datadict[title][0].shape
		X = np.append(np.atleast_2d(X), datadict[title][0], axis=0)

	# hack out any rows with 0.0 mean (across the data from all the films)
	X = np.reshape(X[1:,np.argwhere(np.mean(X, axis=0)>0)],(X.shape[0]-1,-1))
	
	#	...	PYMVPA - dataset_wizard
	ds = dataset_wizard(X, targets=targets, chunks=chunks)
	
	#		..-	classifier(s), take your pick:
	if classifier_num == 0:
		clf = LDA()
	elif classifier_num == 1:
		clf = MappedClassifier(LinearCSVMC(C=-1), 		mapper=SVDMapper())
	elif classifier_num == 2:
		sensaMapper = SensitivityBasedFeatureSelection(
			sensitivity_analyzer=OneWayAnova(), 
			feature_selector=FractionTailSelector(
				ftail,
				mode='select',
				tail='upper'
			)
		)
		clf = MappedClassifier(LinearCSVMC(C=cval), 	mapper=sensaMapper)
	else:
		print "You must specify a classifier (0-3)."
		return None

	cvte = CrossValidation(clf, NFoldPartitioner(), errorfx=lambda p, t: np.mean(p == t), enable_ca=['stats'])
	cv_results = cvte(ds)

	# 	...	SAVE RESULTS (PICKLING)
	res_md['results'] = cvte.ca.stats
	res_md['inverted_weights'] = invert_classifier_weights(ds, clf)
	pickle.dump(res_md, pklfile)
	pklfile.close()
	
	print cvte.ca.stats.as_string(description=True)
	return cvte


def call(directors, titles_per, cflag, samples_per, classifier_num=0, ftail=0.1, cval=-1, pklfile=None):
	
	cvte = assemble_sample_data_and_crossvalidate(
		directors, 
		titles=None, 
		titles_per_director=titles_per, 
		cflag=cflag, 
		samples_per=samples_per, 
		classifier_num=classifier_num, 
		ftail=ftail,
		cval=cval,
		pklfile=pklfile);	
	return cvte
