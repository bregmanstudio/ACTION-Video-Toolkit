***************************************************
Example Six: Predicting Directors Based on Features
***************************************************

Abstract
========

This example provides an example framework for a simple machine learning prediction task. Low-level visual features (Lab color histograms) sampled from a pool of films are used to see whether they can significantly predict the films' directors. This example is also a demonstration of the film_db python file.

This example outlines the basic steps of our implementation of director prediction. See *example_six_director_prediction.py* in the examples folder for the complete code.

Overview
========

This is a multi-step process. There are several Python files involved. This procedure is modular, so that stages can be implemented in different ways. In particular there are the following:

* action_includes.py - convenient place to put the import statements
* action_filmdb.py - simple listing of available film titles and metadata
* 8way_seg_rand_task.py - handles setup of tasks and calls into the pipeline file
* mvpa_pipeline_rand.py - iterates over films collecting randomly sampled data, performs PyMVPA training and cross-validation for the task
* batch_summarize_results - handy script for turning resulting prediction accuracies and variances into a visual graphic


Setup: filmdb
=============

In order to manage a list of directors, their films, and other metadata, we made two simple Python dictionary containers, and wrapped them in a class with several useful methods: ``action_filmdb``. While this file is specific to the ACTION project, it could easily be adapted to other needs.

Looking at the film_db class, we see the two principle data structures. In the ``actionDB``, we store films with their title string, director initials, a color flag, and the year they were produced. The ``actionDirectors`` dictionary contains a mapping from initials to the full name.

.. code-block:: python
	
	self.actionDB = {
	'3_Bad_Men' : ['3_Bad_Men', 'JF', 0, 1926],
	'3_GODFATHERS' : ['3_GODFATHERS', 'JF', 0, 1936],
	'A_Hard_Days_Night': ['A_Hard_Days_Night', 'other', 1, 1962],
	'A_Serious_Man': ['A_Serious_Man', 'CB', 1, 2009],
	'A_Woman_is_a_Woman': ['A_Woman_is_a_Woman' , 'JLG', 1, 1961],

.. code-block:: python

	self.actionDirectors = {
		...
		'CB'  : ['Coen Brothers', 0, 0],
		'DA'  : ['Darren Aronofsky', 0, 0],
		'DL'  : ['David Lynch', 0, 0],
		'JLG' : ['Jean-Luc Godard', 0, 0],
		'JF'  : ['John Ford', 0, 0],
		...
		'other' : ['other', 0, 0]}
	
MVPA Pipeline for ACTION analysis
=================================

In the ``mvpa_pipeline_rand.py`` file, after imports and path setup, we have our list of films, and we do the following:

.. code-block:: python

	import action.action_filmdb as fdb
	db  = fdb.FilmDB()
	dirttl_pool = db.create_analysis_pool(directors, cflag)

This creates a dictionary of directors and potential films. We randomly sample from this list to get the actual titles that we use. There is some additional setup.

.. code-block:: python

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

We set up lists of targets and chunks according to the number of titles and samples, as previously determined. Targets and chunks are components of PyMVPA's method of assembling, classifying, and, ultimately, cross-validating processes. 

.. code-block:: python

	targets = [(i/(titles_per_director*samples_per)) for i in range(total_num_samples)]
	 
	for i, ttl in enumerate(titles):
		res_md['titles'][i] = ttl
	
	chunks = [(i/samples_per) for i in range(total_num_samples)]

Lastly, before setting up and actually running cross-validation, we gather (as Numpy arrays) the data, randomly sampling a certain number of frames from each film.

.. code-block:: python

	ad = actiondata.ActionData()
	datadict = ad.gather_color_histogram_data(titles, ACTION_MOVIE_DIR, grid='midband', cflag=True)

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

Calling the assemble-and-crossvalidate function
-----------------------------------------------

Once we have the data sampled properly and wrapped into a Numpy array, all that remains is converting it using PyMVPA's ``dataset_wizard`` and cross-validating a classifier with that dataset.

.. code-block:: python

	ds = dataset_wizard(X, targets=targets, chunks=chunks)
	
	clf = LDA()
	
	cvte = CrossValidation(clf, NFoldPartitioner(), errorfx=lambda p, t: np.mean(p == t), enable_ca=['stats'])
	cv_results = cvte(ds)
	
The results are written to the ``res_md`` dictionary, and that data is pickled (archived a la Python). This data is available on disc for summarization. See the code file for full details of how this is done. Then the actual call function actually wraps the above assembly and cross-validation in a convenient function that can be called from another code file.


The Task: Calling the pipeline with various parameters
========================================================

As it is in a different Python code file, we simply import the mvpa pipeline. We refer to this as the task file, as it encapsulates an analysis task neatly into a dictionary of parameter settings and a call to the pipeline ``call()`` function.

.. code-block:: python

	import mvpa_pipeline_rand as meta_random_sampling_analysis

The first block of code here lays out the combinations of parameters as entries in a dictionary.

.. code-block:: python
	
	params = {
		'directors' 	: ['AH', 'AK', 'CB', 'DL', 'JF', 'JLG', 'LB', 'SS'], # these are the eight directors that we have in our database
		'numbers_of_directors'	: [8], # always use all eight directors
		'cflags' 		: [2], # 2 = map color films to black/white (Luminescense)
		'titles_per'	: [6, 8], # we will run the task with 6 and 8 films per...
		'samples_per'	: [800,1200,1600,2000], # as well as these numbers of samples
	}

The next block iterates over combinations of these parameters and calls ``pipeline.call()`` for us from the convenience of a task file.

.. code-block:: python

	for cflag in params['cflags']:
		for tper in params['titles_per']:
			for samples_per in params['samples_per']:
			
				meta_random_sampling_analysis.call(
					params['directors'], 
					tper, 
					cflag, 
					samples_per,
					classifier_num=0, 
					ftail=0.1,
					cval=-1,
					pklfile='~/actionresults/8way_rand/' + time.strftime('%Y%m%d%H%M%S') + '.pkl')

A few things to notice: Since we always use all eight directors, we do not need to make subsets or permutations of the list of directors, but rather pass them directly. The ``ftail`` and ``cval`` parameters are for SVM classifiers (see the code files). The ``pklfile`` argument is a full path to a pickled file for the results with the current time as its name.

Viewing our results
===================

We have included the ``batch_summarize_results.py`` file to allow visualization of our classification of directors using low-level color data. This data shows that a simple classifier can glean enough information from the low-level features to correctly predict the director, given a sampling of color feature frames. It is successful at a rate significantly above chance.

.. image:: /images/action_ex6_8way_rand16_pools_means.png
.. image:: /images/action_ex6_8way_rand16_pools_errors.png


