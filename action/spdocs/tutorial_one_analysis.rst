********************************
Tutorial One: Setup and Analysis
********************************

Abstract
========

This tutorial will show how one performs analysis of both the audio and video in a feature-length film. It is assumed that the reader has at least some familiarity with Python or a similar coding language, i.e. Ruby, Javascript, etc. and is comfortable using the command line. The current version of the tutorial is tested with Mac OS 10.8.

Prerequisites
=============

* Python 2.7.* (2.6.* should work as well)
* Numpy, Scipy, IPython, Matplotlib, and OpenCV
* MacTheRipper, MPlayer, fftExtract, automation scripts (see below)
* A movie file, on DVD or on disc
* Terminal, or command line program on your platform of choice

This tutorial will demonstrate analysis of both the audio and video in a feature-length film using ACTION. First, we will give a high-level overview of the process, and then present detailed step-by-step instructions. It is assumed that the reader has at least some familiarity with Python or a similar coding language, i.e. Ruby, Javascript, etc. This initial version of the tutorial is based on Mac OS 10.8, but should work in earlier versions of Mac OS, as well as Windows and Linux.

Overview
========

Here are the basic steps to getting our software to work using a Mac. If you are using our metadata and do not need to set up ACTION to analyze films, you can skip steps 2-3 and 6-8.

#. Set up your Python + Numpy/Scipy/IPython/MatPlotLib/OpenCV environment. 
#. Get a DVD-to-MPEG converter like MacTheRipper or MacXDVDRipper.*
#. Get mplayer and fftExtract.*
#. Download and install ACTION and Bregman Toolkit.
#. Make a directory: ~/Movies/action.
#. Rip your DVD according to these directions. The resultant file should be placed in ~/Movies/action/DVD_TITLE.*
#. Extract audio and audio features using the audio analysis shell script. They will end up as 4 files in ~/Movies/action/DVD_TITLE.*
#. Extract video features using the video analysis Python script or by using iPython. They will end up as 2 files in ~/Movies/action/DVD_TITLE.*

This process is pretty extensive. * Note that you can skip the conversion and analysis steps (this tutorial) and proceed onto the next tutorial using data that we have extracted and made available.

Step-by-step
============

Set Up Python Environment
-------------------------
On Mac OS 10.6.8, it is highly recommended that you use `Enthought Python <https://www.enthought.com/products/epd/>`_, which includes Numpy/Scipy/IPython/MPL. Download OpenCV from `opencv.org <http://opencv.org/>`_ and install using CMake according to their instructions.

For Mac OS 10.7 and later, we use the Python version supplied by Apple: 2.7.3 (as of summer 2013). Download OpenCV from `opencv.org <http://opencv.org/>`_ and install using CMake according to their instructions.

You should be able to ``import`` all the aforementioned modules successfully; if you can, you have successfully set up Python for use with ACTION.

Get Bregman and ACTION
----------------------
Download `Bregman <http://bregman.dartmouth.edu/bregman/>`_ and `ACTION <http://bregman.dartmouth.edu/~action/code.html>`_. For each: unzip the project folder somewhere in your home folder, ``cd`` into it and type ``sudo python setup.py install``. If your Enthought Python Distribution is set up properly, ACTION will be installed into EPD's site-packages directory and available for use within Python the next time you start Python. 

Get a DVD Ripper
----------------
MacTheRipper or some other ripper is used to create an uncompressed version of the DVD. That way, each frame is accessible for analysis, etc.

Get mplayer
-----------
`Mplayer <http://www.mplayerhq.hu/design7/dload.html>`_ is an app for playing video/movie files from the command line or a bash script. We use mplayer to automate the audio extraction part. Install it according to the directions in the README file.

Get fftExtract
--------------
Finally, download `fftExtract <http://omras2.doc.gold.ac.uk/software/fftextract/>`_. fftExtract is a C program that is called from the command line or bash script. The features that it extracts are identical to those extracted by the feature extraction class in the Bregman Toolkit, but runs faster.

Locate Analysis Scripts
-----------------------
There are some analysis helper scripts in the "helpers" directory of ACTION. These are scripts, one written in bash and one in Python, for batching analyses. You can, of course, perform each command separately.

Make an Action Directory
------------------------
This is not a requirement, but simply a default. I use ~/Movies/action to organize my ACTION files. If you have a way that you would rather use, you may pass your own path to the various Python functions.

Rip Your DVD
------------
This `document <http://bregman.dartmouth.edu/action/resourses/DVD_to_JPEG_Motion.pdf>`_ covers ripping in detail, and is the method we used to produce the actual video files used for analysis.

Extract Video
-------------
This is really the heart of ACTION. We have two analysis routines that take frames of video and analyze their color content (plus implicit spatial information) and optical flow.

Using the Python classes directly:

#. Move your .mov file(s) to ~/Movies/action/DVD_TITLE, or to your preferred location. For each movie, the folder with the standardized title should contain the .mov file (copy it to there) and will be where ACTION writes all data files.
#. Fire up the Python interpreter by launching ipython.
#. ``from action import *`` 
#. Create a ColorFeaturesLAB object: ``cflab = color_features_lab.ColorFeaturesLAB(TITLE)`` where ``TITLE`` is the standardized title string for the film (without any extension).
#. Call ``cflab.analyze_histogram_for_movie()``. You can also try ``cflab.analyze_color_features_for_movie_with_display()`` to see a visualization of the analysis data as the process runs.
#. Wait for analysis to complete. You will have the ColorFeatures analysis file in your action movies folder alongside MOVIE.mov.
#. Create an optical flow object: ``oflow = opticalflow24.OpticalFlow24(TITLE)`` where ``TITLE`` is the standardized title string for the film (without any extension).
#. Call ``oflow.analyze_opticalflow_for_movie()``.
#. Once this analysis is done, you will have raw optical flow data for the entire film in your action movies folder.

Using our batch Python script:

#. Move your .mov file(s) to ~/Movies/action, or to your preferred location. For each movie, there should be a folder with the standardized title that contains the .mov file and will be where ACTION writes all data files.
#. Launch Terminal and ``cd`` to the directory with your analysis scripts.
#. Call ``python  batch_analyze_video-threaded ACTION_DIR NUM_PROCESSES``. This will run your video analysis in a batch mode. You should set ``ACTION_DIR`` to ~/Movies/action/ or whatever you used (see above). Set ``NUM_PROCS`` to the number of simultaneous processes to use.
#. Sit back and let bash do all the work. Your video analysis data will reside in two files alongside your .mov file in the movies' directories.

Extract Audio
-------------

We use mplayer to extract the raw audio data from the movie file, and then use fftExtract to extract spectral data: Short Term Fourier Transform (STFT), Constant-Q Fourier Transform (CQFT), Mel Frequency Cepstrum Coefficients (MFCC), Chroma, and Power. fftExtract, a command-line program, is simply a version of the same analysis tools found in the Bregman Toolkit, but coded in C.

Using Bregman for audio analysis : you can find a general tutorial `here <http://bregman.dartmouth.edu/~bregman/bregman/bregman_r12-09.15/bregman/examples/1_features.txt>`_ for using Bregman.

Using fftExtract:

#. Move your .mov file(s) to ~/Movies/action, or to your preferred location. For each movie, there should be a folder with the standardized title that contains the .mov file and will be where ACTION writes all data files.
#. Launch Terminal and ``cd`` to the directory with your analysis scripts. If you just performed video analysis, you should already be in that directory.
#. Call ``python  batch_analyze_audio_48000.sh``.
#. Sit back and let bash do some more work. Your audio analysis data will reside in four files alongside your .mov file in the movies directory. There will also be a .wav file created. You are free to throw it away.


Using the Data
==============

Now that you have all this data, it's time to use it for something. The `next tutorial <tutorial_two_access.html>`_ will cover access and really simple uses of the video and audio data produced in this tutorial.