*********************
Tutorial Three: Audio
*********************

Abstract
========

This tutorial will demonstrate methods to access, display, and generally use audio data gathered through ACTION analysis function.

Prerequisites
=============

* Data analyzed through ACTION, which can take several forms (see below).
* See the first Tutorial for more information.

Raw data, files
===============

The raw analysis is stored in binary files. To summarize, these files, identified by descriptive extensions, are:

#. MOVIE_TITLE.stft - Short term Fourier Transform. (Not collected on our web site, but possible through our scripts.)
#. MOVIE_TITLE.cqft - Constant-Q Fourier Transform.
#. MOVIE_TITLE.mfcc - Mel Frequency Cepstral Coefficients.
#. MOVIE_TITLE.chroma - Chroma values.
#. MOVIE_TITLE.power - Log power values.

For a detailed list of the meanings of the various extensions, please see our `Overview <action_overview.html>`_. 

Access
============
We will use the Bregman MIR toolkit for basic audio processing. When we combine audio and video data, we will wrap calls to Bregman, trying not to reimplement anything not already in Bregman.

Access audio data
-----------------
Access to audio is handled by a function borrowed from audiodb, which is part of Bregman. We are assuming that we have already written binary data to disc and are accessing this analysis data. More information on creating this data is available in `tutorial 1 </~action/docs/html/tutorial_one_analysis.html>`_. Also see Bregman's documentation on this `page <http://digitalmusics.dartmouth.edu/bregman/index.html>`_.

.. code-block:: python

	from action.actiondata import *
	ad = actiondata.

	powers = adb.read_audio_metadata('/Users/kfl/Movies/action/Vertigo/Vertigo.power')
	cqfts = adb.read_audio_metadata('/Users/kfl/Movies/action/Vertigo/Vertigo.cqft')
	mfccs = adb.read_audio_metadata('/Users/kfl/Movies/action/Vertigo/Vertigo.mfcc')
	chromas = adb.read_audio_metadata('/Users/kfl/Movies/action/Vertigo/Vertigo.chrom')

These four calls will load in power, constant-Q Fourier transform, Mel-frequency cepstral coefficients, and Chromagram data, respectively.

View audio data
---------------

Plot the power data with the plot function from Pylab:

.. code-block:: python

	
	plt.plot(power)

.. image:: /images/action_tut3_powers.png


Plot the other data using imagesc (wrapper borrowed from Bregman for 2D data), e.g.:

.. code-block:: python

	imagesc(mfcc)
	
.. image:: /images/action_tut3_mfccs.png


`Next <example_one_clustering.html>`_: Examples of basic video data clustering.