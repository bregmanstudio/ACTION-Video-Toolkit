**************************************************
Example Two: Centers of Mass and Random Sampling
**************************************************

Abstract
========

This example demonstrates the plotting of points and centers of masses of points from multiple films. A set number of points are randomly sampled from each example film. In this tutorial, we will use phase correlation data.

Prerequisites
=============

* Data analyzed through ACTION.
* See previous tutorials for more information.

Randomly sampled points from a film
===================================

Get the data
------------

These are the usual includes for working with ACTION data. For this example, we will use optical flow data. There is only one way to access optical flow data (no gridding choices). Also recall that the optical flow class collects data at the full frame rate, so we will want to extract "strided" data.

.. code-block:: python

	from action import *
	import action.segment as aseg
	import numpy as np

	pcorr = phase_correlation.PhaseCorrelation('Amistad')

	length = pcorr.determine_movie_length() # in seconds
	length_in_frames = length * 4

	full_segment = aseg.Segment(0, duration=length)
	pcorr_full_film = pcorr.middle_band_phasecorr_features_for_segment(full_segment) # default stride is 6 frames
	print pcorr_full_film.shape == (length_in_frames, 512) # should be True

Perform PCA and cluster
---------------------------------------------

Here we find the principle components of the data and select those dimensions with variance above the ``locut`` threshold.

.. code-block:: python

	ad = actiondata.ActionData()
	pcorr_full_film = ad.meanmask_data(pcorr_full_film)
	decomposed = ad.calculate_pca_and_fit(ad.normalize_data(pcorr_full_film), locut=0.0025)
	
Now we randomly sample 500 points from the entire film's data set. We use Numpy's array shuffle function to randomly select points. If we did not sort the indices, the data would look slightly more chaotic.

.. code-block:: python

	index_array = np.arange(decomposed.shape[0])
	np.random.shuffle(index_array)
	random_samples = decomposed[ np.sort(index_array[:500]) ]
	
The following is a wrapper function in ``actiondata'' that will do the same thing:

.. code-block:: python

	random_samples_2, ordering = ad.sample_n_frames(decomposed, n=500, sort_flag=True)
	random_samples.shape == random_samples_2.shape # should be True
	
Plot the clusters
-----------------

Finally, we plot the clusters to visualize a representative sample of the film.

.. code-block:: python

	av = actiondata.ActionView()
	av.plot_clusters(random_samples, np.zeros(500), ttl='ex_2A dims 0-2')
	av.plot_clusters(random_samples[:,1:], np.zeros(500), ttl='ex_2A dims 1-3')

Here's the output. The plot of the lowest three dimensions is rotated to show a more interesting view. The graph of the segments suggested by hierarchical clustering is not very good when viewing a whole film. However, you can zoom into the image using the interactive controls in the viewer when you run this code and explore the data close up.

.. image:: /images/action_ex2_dims_0-2.png
.. image:: /images/action_ex2_dims_1-3.png

Randomly sampled points from multiple films
===========================================

When dealing with multiple films, we iterate and concatenate the resulting 500 points from each film into one grouped array of features.

.. code-block:: python

	ad = actiondata.ActionData()
	av = actiondata.ActionView()
	combo_pcorr = np.array(np.zeros(64), dtype='int32')
	titles = ['Amistad', 'Dune', 'Grapes_of_Wrath', 'A_Woman_is_a_Woman']
	num_samples_per_film = 500

	for title in titles:

		pcorr = phase_correlation.PhaseCorrelation(title)

		length = pcorr.determine_movie_length() # in seconds
		length_in_frames = length * 4

		full_segment = aseg.Segment(0, duration=length)
		pcorr_full_film = pcorr.middle_band_phasecorr_features_for_segment(full_segment)
	
		random_samples, ordering = ad.sample_n_frames(pcorr_full_film, num_samples_per_film)	
	
		combo_pcorr = np.append(np.atleast_2d(combo_pcorr), np.atleast_2d(random_samples), axis=0)

	# get rid of the empty first row
	combo_pcorr = combo_pcorr[1:,:]

Finally, we demonstrate a function that will calculate principal components and retain those with variances above a threshold.

.. code-block:: python

	combo_pcorr = ad.meanmask_data(combo_pcorr)
	decomposed = ad.calculate_pca_and_fit(combo_pcorr, locut=0.0025)
	decomposed.shape
	>>> (2000,40)

	av.plot_clusters(np.atleast_2d(decomposed), np.array([(i/num_samples_per_film) for i in range(len(titles)*num_samples_per_film)]), ttl='ex_2B dims 0-2')
	av.plot_clusters(np.atleast_2d(decomposed)[:,1:], np.array([(i/num_samples_per_film) for i in range(len(titles)*num_samples_per_film)]), ttl='ex_2B dims 1-3')

The result is four clusters of points color-labeled to show which film-grouping each belongs to.

.. image:: /images/action_ex2_multiple_films_dims_0-2.png
.. image:: /images/action_ex2_multiple_films_dims_1-3.png

Centers of mass from multiple films
===================================

In a similar manner, the centers of mass of each movie's points can be graphed in three dimensions:

.. code-block:: python

	av = actiondata.ActionView()
	combo_pcorr = np.array(np.zeros(64), dtype='float32')

	for title in titles:
		pcorr = phase_correlation.PhaseCorrelation(title)
	
		length = pcorr.determine_movie_length() # in seconds
		length_in_frames = length * 4
	
		full_segment = aseg.Segment(0, duration=length)
		pcorr_full_film = pcorr.middle_band_phasecorr_features_for_segment(full_segment)
			
		pcorr_full_film = ad.meanmask_data(pcorr_full_film)
		pcorr_COM = np.mean(pcorr_full_film, axis=0)
		combo_pcorr = np.append(np.atleast_2d(combo_pcorr), np.atleast_2d(pcorr_COM), axis=0)

	# get rid of row of 0's
	combo_pcorr = combo_pcorr[1:,:]

	# plot once
	av.plot_clusters(np.atleast_2d(combo_pcorr)[:,1:], np.array([i for i in range(len(titles))]), ttl='ex_2C')

.. image:: /images/action_ex2_multiple_centroids.png

As the number of films grows in a visualization, the need for simpler representation is more apparent.

`Next <example_three_dissimilarity_plots.html>`_: Visualizing (dis)similarity.