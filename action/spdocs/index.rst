.. ACTION documentation master file, created by
   sphinx-quickstart on Fri Oct  5 14:35:42 2012.

Welcome to the ACTION toolbox from the `Bregman Music and Audio Research Studio <http://bregman.dartmouth.edu>`_ at Dartmouth College. These pages document the toolbox and show examples of its use.

What is ACTION?
===============

Audio-visual Cinematic Toolkit for Interaction, Organization, and Navigation

ACTION provides a work bench to study such features in combination with machine learning methods to yield latent stylistic patterns distributed among films and directors. As such, ACTION is a platform for researching new methodologies in the study of film and media history.

The platform allows such features as access to and analysis of low-level frame-by-frame data, automated segmentation and clustering of this data, audio analysis for soundtracks, and other content analysis tools. ACTION provides Python tools to support research and development, and depends on the Bregman Python Toolkit. OpenCV 2.4 compiled with Python bindings is required for analysis.

Co-principle investigators: `Michael Casey <http://bregman.dartmouth.edu/~mcasey/index.casey.html>`_ (Bregman) and `Mark Williams <http://dartmouth.edu/faculty-directory/mark-j-williams>`_ (Film and Media Studies). Postdoctoral researcher: `Tom Stoll (Bregman) <http://bregman.dartmouth.edu/~tstoll/>`_. Sponsored by the National Endowment for the Humanities (NEH), Office of Digital Humanities (ODH) `Grant #HD-51394-11 <https://securegrants.neh.gov/PublicQuery/main.aspx?f=1&gn=HD-51394-11>`_

Who Is ACTION for?
==================
ACTION provides Python tools to support research and development including, but not limited to:

* Multimedia IR - explore methods for video information retrieval (requires OpenCV package)
* See Bregman's documentation index for a similar list of aims.

How is ACTION Used?
===================
Using ACTION is as easy as:

.. code-block:: python

	from action.suite import *
	cfl = ColorFeaturesLAB('North_by_Northwest')
	cfl.analyze_movie()

...then access the analysis data:

.. code-block:: python

	myseg = Segment(0, cfl.determine_movie_length())
	data = cfl.full_color_features_for_segment(myseg)

You can also view the data alongside the imagery of the film (or even data for a film in the absense of the actual movie file):

.. code-block:: python

	cfl.playback_movie_frame_by_frame()

ACTION also has functionality for analyzing and accessing optical flow (movement) information and audio analysis metadata.

Demo 
====

	We have created a page demonstrating `segmentation and visualization of ACTION data for 139 films <segmenter/action_db.html>`_.


Overview
========

.. toctree::
	:maxdepth: 1
	
	ACTION - data overview <action_overview>
	ACTION - raw data <action_data>
	ACTION - interactive segmentation <http://bregman.dartmouth.edu/action/segmenter/action_db.html>
	ACTION - source code and links <action_code_links>

Tutorials
=========

.. toctree::
   :maxdepth: 1
   
	Tutorial One - setup and analysis <tutorial_one_analysis>
	Tutorial Two - access to video data <tutorial_two_access>
	Tutorial Three - access to audio data <tutorial_three_audio>

Examples
========

.. toctree::
   :maxdepth: 1

	Example One - simple clustering <example_one_clustering>
	Example Two - centers of mass and random sampling <example_two_centers_of_mass>
	Example Three - dissimilarity plots <example_three_dissimilarity_plots>
	Example Four - viewing distributions of color data <example_four_distributions>
	Example Five - in-depth example of segmentation <example_five_segmentation>
	Example Six - in-depth example of a simple director prediction ML task <example_six_director_prediction>
	Example Seven - example of viewing relationships amonng films with multidimensional scaling (MDS) - <example_seven_mds>

ACTION Python Modules
=====================
.. toctree::
   :maxdepth: 1
   
	color_features_lab - color and spatial frame-by-frame analysis and visulaization <color_features_lab>
	opticalflow - Lukas-Kanade optical flow/motion vector frame-to-frame analysis and visulaization <opticalflow>
	opticalflow_tvl1 - TVL optical flow frame-to-frame analysis and visulaization <opticalflow_tvl1>
	phase_correlation - phase correlation frame-to-frame analysis and visulaization <phase_correlation>
	segment - segmentation and container data structure <segment>
	actiondata - data analysis and view routines <actiondata>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Funding sources:
================
.. figure:: http://www.neh.gov/files/neh_at_logo.png
