********************
ACTION Data Overview
********************

Extracted Data
==============

Four kinds of audio metadata and two kinds of video metadata are extracted from each film.

Audio Features
--------------

ACTION allows users to extract standard audio features every quarter second: Constant-Q Fourier Transform (95 bins), Mel-Frequency Cepstrum Coefficients (13 bins), and Chroma (12 bins). In addition we make a spectral power estimation for every frame. We are able to extract Short-term Fourier Transform data, but do not include it in our published data sets due to its prohibitive size (22050 bins per analysis point).

Video Features
--------------

ACTION allows us to extract histograms of color features for every sixth frame (4 times per second at 24fps). Color information is encoded using the L*a*b* color space, where L is Luminescence (brightness) and the remaining two channels encode color. You can read more about the L*a*b* color space `here <http://en.wikipedia.org/wiki/Lab_color_space>`_.

In addition to collecting histograms for color over the entire image frame, we also divide the image into a 4-by-4 grid in order to capture some sense of the spatial distribution of color values. Thus, there are 17 histograms for each frame, the overall histogram and 16 "gridded" histograms.

We have experimented with several different schemes for collecting motion and optical flow data. Phase correlation data is collected as 2D vectors over an 8-by-8 grid over the entire screen, as well as a vector for the entire screen. For more information, please see the `OpenCV documentation <http://docs.opencv.org/modules/imgproc/doc/motion_analysis_and_object_tracking.html#phasecorrelate>`_. 

Optical flow data is collected using the `TV-L1 optical flow algorithm <https://github.com/pkmital/ofxOpenCV2461>`_, as adapted by Parag Mital. This algorithm  collects data over the entire screen, as well as over an 8-by-8 grid. The data is a normalized histogram of angular data. Finally, ACTION has the capability to analyze films for optical flow data using the `Lukas-Kanade optical flow algorithm <http://docs.opencv.org/modules/video/doc/motion_analysis_and_object_tracking.html>`_. This data is collected over an 4-by-4 grid, and within each region, angles are ''binned'' into 8 bins.

Explanation of File Extensions
==============================

+----------------+-------------------+----------------------------------------------------+
| Extension/     | Explanation       | Notes                                              |
| component      |                   |                                                    |
+================+===================+====================================================+
| .color_lab     | Lab-colorspace    | Series of full-frame histograms followed by        |
|                | histogram         | series of gridded histograms, as a Python tuple    |
+----------------+-------------------+----------------------------------------------------+
| .phasecorr     | Phase correlation | Series of full-frame histograms followed by        |
|                | vectors           | series of gridded histograms, as a Python tuple    |
+----------------+-------------------+----------------------------------------------------+
| .opticalflow24 | Optical flow      | Histograms summarize the distribution of motion    |
|                | estimate          | vector angles                                      |
+----------------+-------------------+----------------------------------------------------+
| .tvl1          | TV-L1 optical flow| Series of full-frame histograms followed by        |
|                | estimate          | series of gridded histograms, as a Python tuple    |
+----------------+-------------------+----------------------------------------------------+
| .chrom         | 12-bin Chromagram |                                                    |
+----------------+-------------------+----------------------------------------------------+
| .cqft          | Constant-Q        | 12 bins per octave, 95 total                       |
|                | Fourier Transform |                                                    |
+----------------+-------------------+----------------------------------------------------+
| .mfcc          | 13 Mel-frequency  |                                                    |
|                | Cepstral Coeffs.  |                                                    |
+----------------+-------------------+----------------------------------------------------+
| .power         | Log power         |                                                    |
+----------------+-------------------+----------------------------------------------------+
| .stft          | Short-Term        |                                                    |
|                | Fourier Transform | Not included in our sets of data files...          |
+----------------+-------------------+----------------------------------------------------+
| .json          | Movie info        | Actual fps, duration, etc.                         |
+----------------+-------------------+----------------------------------------------------+
