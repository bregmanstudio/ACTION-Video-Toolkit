**************************************************
Example Two: Centers of Mass and Random Sampling
**************************************************

Abstract
========

This example demonstrates the plotting of points and centers of masses of points from multiple films. A set number of points are randomly sampled from each example film. In this tutorial, we will use optical flow histogram data.

Prerequisites
=============

* Data analyzed through ACTION.
* See previous tutorials for more information.

Randomly sampled points from a film
===================================

Get the data
------------

These are the usual includes for working with ACTION data. For this example, we will use optical flow data. There is only one way to access optical flow data (no gridding choices).

.. code-block:: python

	from action import *
	import bregman.segment as bseg
	import numpy as np

	oflow = opticalflow24.OpticalFlow24('North_by_Northwest')

	length = oflow.determine_movie_length() # in seconds
	length_in_frames = length * 4

	full_segment = bseg.Segment(0, duration=length)
	oflow_full_film = oflow.opticalflow_for_segment(full_segment)
	print oflow_full_film.shape == (length_in_frames, 512) # should be True

Perform PCA and cluster
---------------------------------------------

Here we find the principle components of the data and select those dimensions with variance above the ``locut`` threshold.

.. code-block:: python

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(oflow_full_film, locut=100.0)
	
Now we randomly sample 500 points from the entire film's data set. We use Numpy's array shuffle function to randomly select points. If we did not sort the indices, the data would look slightly more chaotic.

.. code-block:: python

	index_array = np.arange(decomposed.shape[0])
	np.random.shuffle(index_array)
	random_samples = decomposed[ np.sort(index_array[:500]) ]
	
Plot the clusters
-----------------

Finally, we plot the clusters to visualize a representative sample of the film.

.. code-block:: python

	av = actiondata.ActionView(None)
	av.plot_clusters(random_samples, np.zeros(500), ttl='ex_5A')
	av.plot_clusters(random_samples[:, np.zeros(500), ttl='ex_5A')

Here's the output. The plot of the lowest three dimensions is rotated to show a more interesting view. The graph of the segments suggested by hierarchical clustering is not very good when viewing a whole film. However, you can zoom into the image using the interactive controls in the viewer when you run this code and explore the data close up.

.. image:: /images/action_ex2_dims_0-2.png
.. image:: /images/action_ex2_dims_1-3.png

Randomly sampled points from multiple films
===========================================

When dealing with multiple films, we iterate and concatenate the resulting 500 points from each film into one grouped array of features.

.. code-block:: python

	ad = actiondata.ActionData()
	av = actiondata.ActionView()
	combo_oflow = np.array(np.zeros(512), dtype='int32')
	titles = ['North_by_Northwest', 'Psycho', 'Rope', 'Vertigo']
	num_samples_per_film = 500

	for title in titles:
	
		oflow = opticalflow24.OpticalFlow24(title)
	
		length = oflow.determine_movie_length() # in seconds
		length_in_frames = length * 4

		full_segment = bseg.Segment(0, duration=length)
		oflow_full_film = oflow.opticalflow_for_segment_with_stride(full_segment, 6)

		random_samples = ad.sample_n_frames(oflow_full_film, num_samples_per_film)[0]
	
		combo_oflow = np.append(np.atleast_2d(combo_oflow), np.atleast_2d(random_samples), axis=0)

	# get rid of the empty first row
	combo_oflow = combo_oflow[1:,:]

Finally, we demonstrate a function that will calculate principal components and retain those with variances above a threshold.

.. code-block:: python

	decomposed = ad.calculate_pca_and_fit(combo_oflow, locut=100.0)
	decomposed.shape
	>>> (2000,366)

	imagesc(decomposed.T)

The result is four clusters of points color-labeled to show which film-grouping each belongs to.

.. image:: /images/action_ex2_multiple_films_dims_0-2.png
.. image:: /images/action_ex2_multiple_films_dims_1-3.png

Centers of mass from multiple films
===================================

In a similar manner, the centers of mass of each movie's points can be graphed in three dimensions:

.. code-block:: python

	av = actiondata.ActionView(None)
	combo_oflow = np.array(np.zeros(512), dtype='int32')
	
	for title in titles:
		oflow = opticalflow24.OpticalFlow24(title)
		
		length = oflow.determine_movie_length() # in seconds
		length_in_frames = length * 4
		
		full_segment = bseg.Segment(0, duration=length)
		oflow_full_film = oflow.opticalflow_for_segment_with_stride(full_segment, 6)
				
		oflow_COM = np.mean(oflow_full_film, axis=0)
		combo_oflow = np.append(np.atleast_2d(combo_oflow), np.atleast_2d(oflow_COM), axis=0)
	
	# get rid of row of 0's
	combo_oflow = combo_oflow[1:,:]
	
	# plot once
	av.plot_clusters(np.atleast_2d(combo_oflow)[:,1:], np.array([i for i in range(len(titles))]), ttl='ex_5D')

.. image:: /images/action_ex2_multiple_centroids.png

As the number of films grows in a visualization, the need for simpler representation is more apparent.

`Next <example_three_similarity_plots.html>`_: Visualizing similarity.