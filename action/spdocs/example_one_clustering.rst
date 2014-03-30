**************************************************
Example One: K-means and Hierarchical Clustering
**************************************************

Abstract
========

This example will demonstrate simple workflows for clustering color feature histogram data with both k-means and hierarchical clustering algorithms.

Prerequisites
=============

* Data analyzed through ACTION, which can take several forms (see below). For this example, we use Hitchcock's North by Northwest.
* See previous tutorials for more information.

Step-by-step Instructions
=========================

Get the data
------------

Create a color feature instance, instantiating it with the standardized title (no extension). You can find its length through the helpful ``determine_movie_length()`` function. Create a segment describing the time interval that you would like to retrieve. Finally, grab the data. Here we are demonstrating one of the 'spatial' access functions ``center_quad_histogram_for_segment`` that returns just the histogram data for the central gridded squares of the 4-by-4 grid.

.. code-block:: python

	from action.suite import *
	title = 'North_by_Northwest'
	ACTION_DIR = '/Users/me/Movies/action'
	cfl = ColorFeaturesLAB(title, action_dir=ACTION_DIR)

	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4

	ten_minute_segment = Segment(0, duration=length)
	colors_ten_minute_segment = cfl.center_quad_color_features_for_segment(ten_minute_segment)


Perform PCA and average over a sliding window
---------------------------------------------

Here we demonstrate a helper function (see next section) that finds the principle components of the data and selects those dimensions with variance above the ``locut`` threshold. We then take an average over a sliding window (length = 8 frames, hop = 4 frames) to further reduce the dimensionality of the data.

.. code-block:: python

	# ad is an alias for ActionData
	colors_ten_minute_segment = ad.meanmask_data(colors_ten_minute_segment)
	decomposed = ad.calculate_pca_and_fit(colors_ten_minute_segment, locut=0.0001)
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

	# av is an alias for ActionView()
	av.plot_clusters(sliding_averaged, km_assigns, 'K Means - first three principle components')
	
	av.plot_hcluster_segments(km_assigns, km_max_assign, 'K Means - segmentation view', x_lbl='Time (seconds)', y_lbl='Labeling')
	
We can view the distribution of segment lengths, although this is not that informative, since the segments are non-contiguous.

.. code-block:: python

	segs = ad.convert_clustered_frames_to_segs(km_assigns, nc)
	av.plot_segment_length_distribution(segs, ttl='K Means - distribution of segment lengths', x_lbl='Segment length (1/4 seconds)', y_lbl='Frequency')

.. image:: /images/action_ex1A_kmeans.png
.. image:: /images/action_ex1A_kmeans_segments.png
.. image:: /images/action_ex1A_kmeans_seg_distro.png


Hierarchical Clustering
-----------------------

Instead of k-means clustering, here is an example of hierarchical clustering of the color histogram data. Now we look at the entire duration.

.. code-block:: python

	nc = 500 # Roughly 5 per minute for a feature-length film.
	hc_assigns = ad.cluster_hierarchically(decomposed, nc, None)

	av.plot_clusters(decomposed, hc_assigns)
	av.plot_hcluster_segments(hc_assigns, nc)

.. image:: /images/action_ex1B_dims_0_2.png
.. image:: /images/action_ex1B_segs_zoomed.png
.. image:: /images/action_ex1B_distro.png

Kmeans is not deterministic; Hierarchical is
--------------------------------------------

Since K means clustering is not deterministic, the resulting clusterings will be different each time. To cope with this, you can rerun the above several times and collect the best results. Hierarchical clustering of the same data performs the same each time, so we can do this simple clustering in one pass and always know that it will be the same.

Using clustering to view lots of films
--------------------------------------

We will use clustering in a future example to view data from a large collection of films.

`Next <example_two_centers_of_mass.html>`_: Plotting centers of mass of several film's data.