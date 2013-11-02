**************************************************
Example Three: Similarity plots
**************************************************

Abstract
========

This example demonstrates how distance measurements can be used to plot similarity between sets of data or within a set of data, using both Euclidean distance and Cosine similarity.

Prerequisites
=============

* Data analyzed through ACTION.
* See previous tutorials for more information.

Example 3A: Similarity plots of visual features
====================================================

Get the data
------------

These are the usual includes for working with ACTION data. We will again use optical flow data. This time, however, we are using an array of movie titles and iterating over it to 

.. code-block:: python

	from action import *
	import bregman.segment as bseg

	title = 'North_by_Northwest'
	
	hist = color_features_lab.ColorFeaturesLAB(title)
	oflow = opticalflow24.OpticalFlow24(title)
	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4
	ten_minute_segment = bseg.Segment(0, duration=length)
	histogram_ten_minute_segment = hist.center_quad_color_features_for_segment(ten_minute_segment)
	oflow_ten_minute_segment = oflow.opticalflow_for_segment_with_stride(ten_minute_segment, 6)


View the similarity matrices
----------------------------

We now plot similarity matrices using cosine distance. They both show about the same thing, but with some subtle variations.

.. code-block:: python

	ad = actiondata.ActionData()
	h_decomposed = ad.calculate_pca_and_fit(histogram_ten_minute_segment, locut=0.0001)
	o_decomposed = ad.calculate_pca_and_fit(oflow_ten_minute_segment, locut=100)

	imagesc(distance.cosine(h_decomposed, h_decomposed), 'Cosine: Histograms-SVD - first 10 minutes')
	imagesc(distance.cosine(o_decomposed, h_decomposed), 'Cosine: Optical flow-SVD - first 10 minutes')

.. image:: /images/action_ex3_cosine_hist_svd.png
.. image:: /images/action_ex3_cosine_oflow_svd.png

Example 3B: Similarity plots of audio features
====================================================

In order to work with audio features, we use the Bregman toolkit, specifically the AudioDB class. The audio MFCC data has some Nan values, so we use a masked array to eliminate these. The visualizations show Euclidean and cosine distances with and without SVD. As you can see, there is some difference depending on the distance function used.

.. code-block:: python

	from action import *
	from bregman.suite import *
	import bregman.audiodb as adb

	title = 'North_by_Northwest'

	mfccs_ten_minute_segment = adb.adb.read('/Users/kfl/Movies/action/' + title + '.mfcc_13_M2_a0_C2_g0_i16000')[:2400,:]
	D = np.ma.masked_invalid(mfccs_ten_minute_segment)
	D = D.filled(D.mean())

	decomposed = ad.calculate_pca_and_fit(D, locut=0.0001)

	imagesc(distance.euc2(D, D))
	imagesc(distance.euc2(decomposed, decomposed))
	imagesc(distance.cosine(D, D))
	imagesc(distance.cosine(decomposed, decomposed))

.. image:: /images/action_ex3_euc_audio.png
.. image:: /images/action_ex3_euc_audio_pca.png
.. image:: /images/action_ex3_cosine_audio.png
.. image:: /images/action_ex3_cosine_audio_pca.png

Example 3C: Similarity plots of combined video + audio features
===============================================================

Using the same features as above, we combine them (before reducing dimensionality) into a single feature. We show two similarity matrices.

.. code-block:: python

	full_feature = np.c_[histogram_ten_minute_segment, oflow_ten_minute_segment, audio]
	full_feature_decomposed = ad.calculate_pca_and_fit(full_feature, locut=0)

	imagesc(distance.cosine(full_feature, full_feature))
	imagesc(distance.cosine(full_feature_decomposed, full_feature_decomposed))
	
.. image:: /images/action_ex3_cosine_combo.png
.. image:: /images/action_ex3_cosine_combo_pca.png

`Next <example_four_distributions.html>`_: Visualizing color features data distribution.