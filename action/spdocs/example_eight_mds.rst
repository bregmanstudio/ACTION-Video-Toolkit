***************************************************
Example Eight: Multi-Dimensional Scaling (MDS)
***************************************************

Abstract
========

Multi-dimensional scaling will provide a views of our data that may be more intuitive than similarity matrices. We are taking random samplings of color features, as before, but now we are clustering these samples in a 2-dimensional scatter plot.

Overview
========

This is another multi-step process. There is a function that conveniently wraps the access and sampling steps, as well as a function that performs the display. We are using scikits learn for this demonstration. Again, we can use our ``filmdb''_ for this task, but first we demonstrate the basics with some hand-made lists.

Setup: filmdb
=============

You can see the two aforementioned functions in ``action_mds.py''. We build our data array by calling the access/sampling function. We also build a list ``y'' that contains integers identifying each sample's membership in a film (similar to labeling targets and chunks in PyMVPA). 

.. code-block:: python
	
	X, ttls = sampleAllFilms(TITLES, DIRECTORS, SAMPLE_FRAMES_PER_TITLE)
	y = [i/NUM_NEIGHBORS for i in range(SAMPLE_FRAMES_PER_TITLE*TITLES_PER_DIR*NUMBER_OF_DIRECTORS)]
	n_samples, n_features = X.shape

Self-similarity
---------------
After concatenation of the samples into single-block features (and some standardization), we compute a self-similarity matrix for our collection of data.

.. code-block:: python

	D = ad.calculate_self_similarity_matrix(X_reduced, X_reduced)

Calculate MDS and plot
----------------------

Finally, the MDS function is called, and the data is plotted.

.. code-block:: python

	clf = manifold.MDS(n_components=2, n_init=1, max_iter=100)

	X_mds = clf.fit_transform(D)

	plot_embedding(X_mds, yconcat, titles=ttls, plot_title='Multi-dimensional Scaling (3 directors + 9 films each)')

Multiple plots confirm some interesting structure in the results. The layout of the films in this example grouping is consistent and we see some interesting patterns: clustering of earlier black and white Hitchcock with later films (Eraserhead), the Twin Peaks titles stay together, there is a cluster of Godard's films, etc. While it would be difficult to draw any definitive conclusions based on these graphs, they do provide some insight into the relative similarities of these films' visuals.

.. image:: /images/action_ex8_3dirs_9films_MDS.png
.. image:: /images/action_ex8_3dirs_9films_MDS_2.png