********************
ACTION Data Overview
********************

Extracted Data
==============

Four kinds of audio metadata and two kinds of video metadata are extracted from each film.

Audio Features
--------------

We extract standard audio features every quarter second: Constant-Q Fourier Transform (12 bins), Mel-Frequency Cepstrum Coefficients (13 bins), and Chroma (12 bins). In addition we make a spectral power estimation for every frame. We are able to extract Short-term Fourier Transform data, but do not include it due to its prohibitive size (22050 bins per analysis point).

Video Features
--------------

We extract histograms of color features for every sixth frame (4 times per second at 24fps). The histogram has 16 bins, representing 16 gradations of brightness with three values (L,a, and b) for each bin. Color information is encoded using the L*a*b* spectrum, where L is Luminescence (brightness) and the remaining two channels encode color. You can read more about the L*a*b* color space `here <http://en.wikipedia.org/wiki/Lab_color_space>`_.

In addition to collecting histograms for the entire image frame, we also divide the image into a 4-by-4 grid in order to capture some sense of the spatial distribution of color values. Thus, there are 17 histograms for each frame, the overall histogram and 16 "gridded" histograms.

We have experimented with several different schemes for collecting motion vector and optical flow data. We have extracted and make available full-frame-rate optical flow data using two algorithms, as well as phase correlation data.

Explanation of File Extensions
==============================

+----------------+-------------------+----------------------------------------------------+
| Extension/     | Explanation       | Notes                                              |
| component      |                   |                                                    |
+================+===================+====================================================+
| .color_lab     | Lab-colorspace    | Series of full-frame histograms followed by        |
|                | histogram         | series of gridded histograms, as a Python tuple    |
+----------------+-------------------+----------------------------------------------------+
| .phasecorr     | PhaseCorrelation  | Series of full-frame histograms followed by        |
|                | vectors           | series of gridded histograms, as a Python tuple    |
+----------------+-------------------+----------------------------------------------------+
| .opticalflow24 | Optical flow      | Histograms summarize the distribution of motion    |
|                | estimate          | vector angles                                      |
+----------------+-------------------+----------------------------------------------------+
| .tvl1          | TVL1 Optical flow | Series of full-frame histograms followed by        |
|                | estimate          | series of gridded histograms, as a Python tuple    |
+----------------+-------------------+----------------------------------------------------+
| .chrom         | 12-bin Chromagram |                                                    |
+----------------+-------------------+----------------------------------------------------+
| .cqft          | Constant-Q        | 12 bins per octave                                 |
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
