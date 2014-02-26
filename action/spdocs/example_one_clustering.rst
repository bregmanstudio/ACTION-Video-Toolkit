**************************************************
Example One: K-means and Hierarchical Clustering
**************************************************

Abstract
========

This example will demonstrate simple workflows for clustering histogram data with both k-means and hierarchical clustering algorithms.

Prerequisites
=============

* Data analyzed through ACTION, which can take several forms (see below).
* See previous tutorials for more information.

Step-by-step Instructions
=========================

Import + Setup
--------------

These are the usual includes for working with ACTION data.

.. code-block:: python

	from action import *
	import action.segment as aseg
	import numpy as np

Get the data
------------

Create a histogram object, instantiating it with the standardized title (no extension). You can find its length through the helpful ``determine_movie_length()`` function. Create a segment describing the time interval that you would like to retrieve. Finally, grab the data. Here we are demonstrating one of the 'spatial' access functions ``center_quad_histogram_for_segment`` that returns just the histogram data for the central gridded squares of the 4-by-4 grid.

.. code-block:: python

	cfl = color_features_lab.ColorFeaturesLAB(TITLE, action_dir=ACTION_DIR)

	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4

	ten_minute_segment = aseg.Segment(0, duration=length)
	histogram_ten_minute_segment = cfl.center_quad_color_features_for_segment(ten_minute_segment)


Perform PCA and average over a sliding window
---------------------------------------------

Here we demonstrate a helper function (see next section) that finds the principle components of the data and selects those dimensions with variance above the ``locut`` threshold. We then take an average over a sliding window (length = 8 frames, hop = 4 frames) to further reduce the dimensionality of the data.

.. code-block:: python

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(histogram_ten_minute_segment, locut=0.0001)
	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4, length_in_frames)

Aside: ActionData/ActionView classes provide helper functions
-------------------------------------------------------------

We have provided some convenient helper functions in the ``ActionData`` and ``ActionView`` classes. These functions should make coding and reading code a little simple. Of course, users are welcome to code their own processing functions.

Perform the actual clustering
-----------------------------

Now we do some actual clustering. There are 600 * 4 / 4 = 600 frames in our segment that we extracted above, so let's assign 60 clusters or 10% of the total. Each frame is assigned to a K means cluster.

.. code-block:: python

	nc = 60
	km_assigns, km_max_assign = ad.cluster_k_means(sliding_averaged, nc)

Plot the clusters
-----------------

Finally, we plot the clusters two ways. First as points in 3-dimensional space (using the three dimensions with the highest variance) then as bars over time, to get a sense of their distibution over the film. 

.. code-block:: python

	av = actiondata.ActionView()
	av.plot_clusters(sliding_averaged, km_assigns)
	av.plot_hcluster_segments(km_assigns, km_max_assign)

.. image:: /images/action_ex1A_kmeans.png
.. image:: /images/action_ex1A_kmeans_segments.png

Hierarchical Clustering
-----------------------

Instead of k-means clustering, here is an example of hierarchical clustering of the histogram data. Now we look at the entire duration.

.. code-block:: python

	nc = 1000
	hc_assigns = ad.cluster_hierarchically(decomposed, nc, None)

	av = actiondata.ActionView()
	av.plot_clusters(decomposed, hc_assigns)
	av.plot_hcluster_segments(hc_assigns, nc)

.. image:: /images/action_ex1B_dims_0_2.png
.. image:: /images/action_ex1B_segs_zoomed.png

Let's try looking at dimensions 1-3 of the decomposed result (leaving out the dimension with the most variance). Since we can only visualize up to three dimensions of data at one time, this will give us a new way of seeing how the points cluster (or fail to do so). The view is different, and it's been rotated to show an interesting view. Here's the code for this second view:

.. code-block:: python

	av.plot_clusters(decomposed[:,1:], hc_assigns)

.. image:: /images/action_ex1B_dims_1_3.png

Kmeans is not deterministic; Hierarchical is
--------------------------------------------

Since K means clustering is not deterministic, the resulting clusterings will be different each time. To cope with this, you can rerun the above several times and collect the best results. Hierarchical clustering of the same data performs the same each time, so we can do this simple clustering in one pass and always know that it will be the same.

Using clustering to view lots of films
--------------------------------------

We will use clustering in a future example to view data from a large collection of films.

`Next <example_two_centers_of_mass.html>`_: Plotting centers of mass of several film's data.