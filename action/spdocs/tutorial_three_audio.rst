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
Access to audio is handled with audiodb, which is part of Bregman. We are assuming that we have already written binary data to disc and are accessing this analysis data. More information on creating this data is available in `tutorial 1 </~action/docs/html/tutorial_one_analysis.html>`_. Also see Bregman's documentation on this `page <http://digitalmusics.dartmouth.edu/bregman/index.html>`_.

.. code-block:: python

	from bregman.suite import *
	import bregman.audiodb as adb
	from pylab import *

	power = adb.adb.read('~/Movies/action/Psycho/Psycho.power_C2_i16000')
	cqft = adb.adb.read('~/Movies/action/Psycho/Psycho.cqft12_a0_C2_g0_i16000')
	mfcc = adb.adb.read('~/Movies/action/Psycho/Psycho.mfcc_m13_M2_a0_C2_g0_i16000')
	chroma = adb.adb.read('~/Movies/action/Psycho/Psycho.chrom12_a0_C2_g0_i16000')

These four calls will load in power, constant-Q Fourier transform, Mel-frequency cepstral coefficients, and Chromagram data, respectively.

View audio data
---------------

Plot the power data with the plot function from Pylab:

.. code-block:: python

	plt.plot(power)

.. image:: /images/power_plot.png


Plot the other data using imagesc (wrapper in Bregman for 2D data), e.g.:

.. code-block:: python

	imagesc(mfcc)
	
.. image:: /images/mfcc_imagesc.png

`Next <example_one_clustering.html>`_: Example of basic video data clustering.