************************************
Example Four: Distributions of Data
************************************

Abstract
========

This example demonstrates graphing average L*a*b* color histogram values from two films, full features from two films, and distributions of values (means and variances).

Compare all video features between two films
============================================

We can view the raw data from our three video features. First we normalize and standardize our data. Then we make an image out of that data.

.. code-block:: python

	from action.suite import *
	import numpy as np
	import matplotlib.pyplot as plt

	# idx = np.arange(48)
	# barwidth = 0.5
	# barwidth2 = 0.75

	cfl_vert = ColorFeaturesLAB('Vertigo')
	cfl_nbr = ColorFeaturesLAB('No_Blood_Relation')

	pcorr_vert = PhaseCorrelation('Vertigo')
	pcorr_nbr = PhaseCorrelation('No_Blood_Relation')

	oflow_vert = OpticalFlow('Vertigo')
	oflow_nbr = OpticalFlow('No_Blood_Relation')

	fullseg_vert = Segment(0, cfl_vert.determine_movie_length())
	fullseg_nbr = Segment(0, cfl_nbr.determine_movie_length())

	cfl_vert_X = cfl_vert.middle_band_color_features_for_segment(fullseg_vert)
	cfl_nbr_X = cfl_nbr.middle_band_color_features_for_segment(fullseg_nbr)
	pcorr_vert_X = pcorr_vert.middle_band_phasecorr_features_for_segment(fullseg_vert)
	pcorr_nbr_X = pcorr_nbr.middle_band_phasecorr_features_for_segment(fullseg_nbr)
	oflow_vert_X = oflow_vert.opticalflow_for_segment_with_stride(fullseg_vert)
	oflow_nbr_X = oflow_nbr.opticalflow_for_segment_with_stride(fullseg_nbr)


	cfl_vert_X = ad.normalize_data(cfl_vert_X)
	cfl_nbr_X = ad.normalize_data(cfl_nbr_X)
	pcorr_vert_X = ad.normalize_data(ad.standardize_data(pcorr_vert_X))
	pcorr_nbr_X = ad.normalize_data(ad.standardize_data(pcorr_nbr_X))
	oflow_vert_X = ad.normalize_data(np.power(oflow_vert_X, 0.2))
	oflow_nbr_X = ad.normalize_data(np.power(oflow_nbr_X, 0.2))

	video_vert_X = np.c_[cfl_vert_X, pcorr_vert_X, oflow_vert_X]
	video_nbr_X = np.c_[cfl_nbr_X, pcorr_nbr_X, oflow_nbr_X]


	imagesc(video_vert_X.T, title_string='Visual features: normalized, etc. for Vertigo')
	imagesc(video_nbr_X.T, title_string='Visual features: normalized, etc. for No Blood Relation')

	imagesc(video_vert_X[:1000,:].T, title_string='Visual features: normalized, etc. for Vertigo - first 1000 frames')
	imagesc(video_nbr_X[:1000,:].T, title_string='Visual features: normalized, etc. for No Blood Relation - first 1000 frames')


.. image:: /images/action_ex4_combined_video_vert.png
.. image:: /images/action_ex4_combined_video_nbr.png

And zoomed in to the first 1000 time points:

.. image:: /images/action_ex4_vert_1000.png
.. image:: /images/action_ex4_nbr_1000.png

Plotting distributions
----------------------

Instead of viewing raw metadata, we can plot distributions of their means and variances for each channel.

.. code-block:: python

	data_col_means = np.mean(video_vert_X, axis=0)
	data_col_means2 = np.mean(video_nbr_X, axis=0)
	data_col_vars = np.var(video_vert_X, axis=0)
	data_col_vars2 = np.var(video_nbr_X, axis=0)

	idx = np.arange(48)
	barwidth = 0.5
	barwidth2 = 0.75

	p1 = plt.bar(np.arange(960), data_col_vars2, barwidth2, color='y', bottom=data_col_means2)
	p2 = plt.bar(np.arange(960), data_col_vars, barwidth, color='g', bottom=data_col_means)
	plt.title('Video features means and variances per bin')
	plt.legend( (p1[0], p2[0]), ('Vertigo', 'No Blood Relation') )
	
.. image:: /images/action_ex4_all_video_overlaps.png


Zooming in, we can see that there is a lot of detail, but any hopes of saying (or seeing) anything about one film in particular are pretty remote: 

.. image:: /images/action_ex4_zoomed_overlaps.png


Full comparison - add three audio features
==========================================

In the above example, you should be able to see that one is color and one is black and white. Since No Blood Relation is also silent, we will only show the audio features for Vertigo.

.. code-block:: python

	title = 'Vertigo'

	mfccs = ad.read_audio_metadata(os.path.join(ACTION_DIR,title,(title+'.mfcc')))
	chromas = ad.read_audio_metadata(os.path.join(ACTION_DIR,title,(title+'.chrom')))
	powers = ad.read_audio_metadata(os.path.join(ACTION_DIR,title,(title+'.power')))

	mfccs = ad.meanmask_data(mfccs)
	mfccs = ad.standardize_data(mfccs)
	mfccs = ad.meanmask_data(mfccs)
	mfccs = ad.normalize_data(mfccs)
	mfccs = ad.meanmask_data(mfccs)

	chromas = ad.meanmask_data(chromas)
	chromas = ad.standardize_data(chromas)
	chromas = ad.meanmask_data(chromas)
	chromas = ad.normalize_data(chromas)
	chromas = ad.meanmask_data(chromas)

	powers = ad.meanmask_data(powers)
	powers = ad.normalize_data(powers)
	powers = ad.meanmask_data(powers)

	imagesc(mfccs.T, title_string='MFCCs - normalized - '+str(title))
	imagesc(chromas.T, title_string='Chromas - normalized - '+str(title))
	plt.figure()
	plt.plot(np.atleast_1d(powers))
	plt.title('Normalized power values for whole film - '+str(title))

.. image:: /images/action_ex4_powers_vert_plot.png
.. image:: /images/action_ex4_mfccs_vert_normed.png
.. image:: /images/action_ex4_chromas_vert_normed.png

.. code-block:: python


	audio_vert_X =  np.c_[np.atleast_1d(powers), mfccs, chromas]

	imagesc(audio_vert_X, title_string='Power/MFCC/Chromas - normalized - '+str(title))

.. image:: /images/action_ex4_combined_audio_vert.png

.. code-block:: python

	min_length = min(audio_vert_X.shape[0], video_vert_X.shape[0])

	all_vert_X = np.c_[video_vert_X[:min_length,:], audio_vert_X[:min_length,:]]
	
	imagesc(all_vert_X.T, title_string='Video/Audio Features - normalized - '+str(title))
	
.. image:: /images/action_ex4_all_features_vert.png

`Next <example_five_segmentation.html>`_, we look at segmentations of movie data.