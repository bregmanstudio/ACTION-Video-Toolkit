**************************************************
Example Four: Distributions of Data
**************************************************

Abstract
========

This example demonstrates graphing average L*a*b* color histogram values across many films and as bar graphs comparing two films.

Across several films
====================

MIGRATE FROM EVERNOTE

Compare two films
=================

We can take a close look at the data from two films to get a sense as to where and how much it overlap. As means and error bars:

.. code-block:: python

	from action import *
	import bregman.segment as bseg
	import numpy as np


	idx = np.arange(48)
	width = 0.5
	width2 = 0.75


	cfl = color_features_lab.ColorFeaturesLAB('Rope')
	fullseg = bseg.Segment(0, cfl.determine_movie_length())
	data = cfl.full_color_features_for_segment(fullseg)


	cfl2 = color_features_lab.ColorFeaturesLAB('Vertigo')
	fullseg2 = bseg.Segment(0, cfl2.determine_movie_length())
	data2 = cfl2.full_color_features_for_segment(fullseg2)


	p1 = plt.bar(idx, data_col_vars2, width2, color='y', bottom=data_col_means2)
	p2 = plt.bar(idx, data_col_vars, width, color='g', bottom=data_col_means)


	plt.legend( (p1[0], p2[0]), ('Vertigo', 'Rope') )

.. image:: /images/action_ex4_vertigo_vs_rope.png
