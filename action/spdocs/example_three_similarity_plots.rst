**************************************************
Example Three: Dissimilarity plots
**************************************************

Abstract
========

This example demonstrates how distance measurements can be used to plot dissimilarity between sets of data or within a set of data, using both Euclidean distance and cosine (dis)similarity.

Prerequisites
=============

* Data analyzed through ACTION.
* See previous tutorials for more information.

Example 3A: Dissimilarity plots of visual features
====================================================

Get the data
------------

These are the usual includes for working with ACTION data. We will use color and phase correlation data, as well as audio MFCCs. We will concentrate on the first 10 minutes of an early experimental film. You will have to change the ``title`` and ``action_dir`` to values that make sense on your system (see earlier tutorials for an overview.)

.. code-block:: python

	title = TITLE

	cfl = color_features_lab.ColorFeaturesLAB(title, ACTION_DIR)
	pcorr = phase_correlation.PhaseCorrelation(title, ACTION_DIR)
	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4
	ten_minute_segment = aseg.Segment(0, duration=length)
	cfl_ten_minute_segment = cfl.center_quad_color_features_for_segment(ten_minute_segment)
	pcorr_ten_minute_segment = pcorr.center_quad_phasecorr_features_for_segment(ten_minute_segment, access_stride=6) # 6 is the default


View the dissimilarity matrices
----------------------------

We now plot dissimilarity matrices using cosine distance. They both show about the same thing, but with some subtle variations.

.. code-block:: python

	ad = actiondata.ActionData()
	c_decomposed = ad.calculate_pca_and_fit(cfl_ten_minute_segment, locut=0.0001)
	p_decomposed = ad.calculate_pca_and_fit(pcorr_ten_minute_segment, locut=0.01)

	imagesc(distance.euc2(c_decomposed, c_decomposed), 'EUC: Color Features-PCA - first 10 minutes')
	imagesc(distance.euc2(p_decomposed, p_decomposed), 'EUC: Phase corr.-PCA - first 10 minutes')

.. image:: /images/action_ex3A_euc_hist_pca.png
.. image:: /images/action_ex3A_euc_pcorr_pca.png

.. code-block:: python

	imagesc(distance.cosine(c_decomposed, c_decomposed), 'Cosine: Color Features-PCA - first 10 minutes')
	imagesc(distance.cosine(p_decomposed, p_decomposed), 'Cosine: Phase Corr.-PCA - first 10 minutes')

.. image:: /images/action_ex3A_cosine_hist_pca.png
.. image:: /images/action_ex3A_cosine_pcorr_pca.png

.. code-block:: python

	combo_decomposed = np.c_[c_decomposed, p_decomposed]

	imagesc(distance.euc2(combo_decomposed, combo_decomposed), 'EUC: Combo-PCA - first 10 minutes')
	imagesc(distance.cosine(combo_decomposed, combo_decomposed), 'Cosine: Combo-PCA - first 10 minutes')

.. image:: /images/action_ex3A_euc_combo_pca.png
.. image:: /images/action_ex3A_cosine_combo_pca.png


Example 3B: Dissimilarity plots of audio features
====================================================

In order to work with audio features, we use the Bregman toolkit, specifically the AudioDB class. The audio MFCC data has some Nan values, so we use a masked array to eliminate these. The visualizations show Euclidean and cosine distances with and without PCA. As you can see, there is some difference depending on the distance function used.

.. code-block:: python

	title = TITLE

	mfccs_ten_minute_segment = adb.read(os.path.expanduser(ACTION_DIR) + title + '/' + title + '.mfcc')[:2400,:]
	D = np.ma.masked_invalid(mfccs_ten_minute_segment)
	D = D.filled(D.mean())

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(D, locut=0.2)

	imagesc(distance.euc2(D, D), title_string='EUC: MFCC - first 10 minutes')
	imagesc(distance.euc2(decomposed, decomposed), title_string='EUC: MFCC-PCA - first 10 minutes')
	imagesc(distance.cosine(D, D), title_string='Cosine: MFCC - first 10 minutes')
	imagesc(distance.cosine(decomposed, decomposed), title_string='Cosine: MFCC-PCA - first 10 minutes')

.. image:: /images/action_ex3B_euc_mfcc.png
.. image:: /images/action_ex3B_euc_mfcc_pca.png
.. image:: /images/action_ex3B_cosine_mfcc.png
.. image:: /images/action_ex3B_cosine_mfcc_pca.png

Example 3C: Dissimilarity plots of combined video + audio features
===============================================================

Using the same visual and audio features as above, we **normalize** them and then combine them (before reducing dimensionality) into a single feature. We show two dissimilarity matrices.

.. code-block:: python

	cfl_normed		= cfl_ten_minute_segment # already normed!
	pcorr_normed	= ad.normalize_data(pcorr_ten_minute_segment)
	mfccs_normed	= ad.normalize_data(audio)

	full_feature = np.c_[cfl_normed, pcorr_normed, mfccs_normed]
	ad = actiondata.ActionData()
	full_feature_decomposed = ad.calculate_pca_and_fit(full_feature, locut=0.01)

	imagesc(distance.cosine(full_feature, full_feature), title_string='Cosine: full feature - first 10 minutes')
	imagesc(distance.cosine(full_feature_decomposed, full_feature_decomposed), title_string='Cosine: PCA - full feature - first 10 minutes')

	imagesc(distance.euc2(full_feature, full_feature), title_string='EUC: full feature - first 10 minutes')
	imagesc(distance.euc2(full_feature_decomposed, full_feature_decomposed), title_string='EUC: PCA - full feature - first 10 minutes')
	
.. image:: /images/action_ex3C_euc_fullnormed.png
.. image:: /images/action_ex3C_euc_fullnormed_pca.png
.. image:: /images/action_ex3C_cosine_fullnormed.png
.. image:: /images/action_ex3C_cosine_fullnormed_pca.png


Source
======
All the data on this page was gathered from the first 10 minutes of Meshes of the Afternoon. "Meshes of the Afternoon (1943) is a short experimental film directed by wife-and-husband team, Maya Deren and Alexander Hammid." [#f1]_

`Next <example_four_distributions.html>`_: Visualizing color features data distribution.

.. rubric:: Footnotes

.. [#f1] Source: `Wikipedia <https://en.wikipedia.org/wiki/Meshes_of_the_Afternoon>`_ Accessed 2/25/14 .