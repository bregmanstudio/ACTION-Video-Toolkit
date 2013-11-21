# color_features_lab.py - color features (L*a*b*) histogram data from video frames
# Bregman:ACTION - Cinematic information retrieval toolkit

"""
Part of Bregman:ACTION - Cinematic information retrieval toolkit

Overview
========

Use the color features (L*a*b*) extractor class to analyze streams of images or video files. The color features class steps through movie frames and extracts histograms for two frame types. The first is a histogram of color features for the entire image. The second is a set of sixteen histograms, each describing a region of the image. The regions are arranged in an even four-by-four non-overlapping grid, with the first region at the upper left and the last at the lower right. These values, in sequence, are stored in a binary file.

In order to reduce the amount of data involved (and the processing time involved), a stride parameter is used. This number is the number of movie frames to account for in one analysis frame. The default is 6. As of version 1.0, there is no averaging or interpolation, the "skipped" frames are simply dropped.

Use
===

Instantiate the ColorFeaturesLAB class, optionally with additional keyword arguments:

.. code-block:: python

	myCFLAB = ColorFeaturesLAB (fileName, param1=value1, param2=value2, ...)

The global default color_features-extractor parameters are defined in a parameter dictionary: 

.. code-block:: python

    default_color_params = {
		'action_dir' : '~/Movies/action', # default dir
		ETC...
	}

The full list of settable parameters, with default values and explanations:

+-----------------+-----------------+----------------------------------------------------+
| keyword         | default         | explanation                                        |
+=================+=================+====================================================+
| action_dir      | ~/Movies/action | default dir                                        |
+-----------------+-----------------+----------------------------------------------------+
| movie_extension | .mov            |                                                    |
+-----------------+-----------------+----------------------------------------------------+
| data_extension  | .color_lab      | this is what will be output and expected for input |
+-----------------+-----------------+----------------------------------------------------+
| mode            | analyze         | 'playback' or 'analyze'                            |
+-----------------+-----------------+----------------------------------------------------+
| fps             | 24              | fps: frames per second                             |
+-----------------+-----------------+----------------------------------------------------+
| offset          | 0               | time offset in seconds                             |
+-----------------+-----------------+----------------------------------------------------+
| duration        | -1              | time duration in seconds, -1 (default) maps to full|
|                 |                 | duration of media                                  |
+-----------------+-----------------+----------------------------------------------------+
| stride          | 6               | number of video frames to that comprise one        |
|                 |                 | analysis frame, skips stride - 1 frames            |
+-----------------+-----------------+----------------------------------------------------+
| threshold       | 0.0             | (empirical) threshold for histogram values; set to |
|                 |                 | a positive number to remove extremely low values   |
+-----------------+-----------------+----------------------------------------------------+
| verbose         | True            | useful for debugging                               |
+-----------------+-----------------+----------------------------------------------------+
| display         | True            | launch display screen during analysis              |
+-----------------+-----------------+----------------------------------------------------+
| Parameters for color features histograms and display...                                |
+-----------------+-----------------+----------------------------------------------------+
| colorspace      | lab             | this is redundant, don't try to change it          |
+-----------------+-----------------+----------------------------------------------------+
| ldims           | 16              | number of dimensions for L (luminosity)            |
+-----------------+-----------------+----------------------------------------------------+
| adims           | 16              | number of dimensions for a (color)                 |
+-----------------+-----------------+----------------------------------------------------+
| bdims           | 16              | number of dimensions for b (color)                 |
+-----------------+-----------------+----------------------------------------------------+
| lrange          | [0, 256]        | range to map to/from L                             |
+-----------------+-----------------+----------------------------------------------------+
| arange          | [0, 256]        | range to map to/from a                             |
+-----------------+-----------------+----------------------------------------------------+
| brange          | [0, 256]        | range to map to/from b                             |
+-----------------+-----------------+----------------------------------------------------+
| hist_width      | 640             | for visualization                                  |
+-----------------+-----------------+----------------------------------------------------+
| hist_height     | 480             | for visualization                                  |
+-----------------+-----------------+----------------------------------------------------+
| vert_offset     | 500             | for 17th/full histogram in visualization           |
+-----------------+-----------------+----------------------------------------------------+


Parameter keywords can be passed explicitly as formal arguments or as a keyword argument parameter dict:, e.g.:

.. code-block:: python

   myCFLAB = ColorFeaturesLAB(fileName, vrange=[32, 256], verbose=True )
   myCFLAB = ColorFeaturesLAB(fileName, **{'vrange':[32, 256], 'verbose':True} )

Using ColorFeaturesLAB
======================
The functions of the ColorFeaturesLAB class define the various use cases or patterns.

Analyze a full film:

.. code-block:: python

	cflab = ColorFeaturesLAB('Psycho')
	cflab.analyze_movie() # Assumes that ~/Movies/action/Psycho.mov exists; returns otherwise

This also works, so you can define your own file locations:

.. code-block:: python

	cflab = ColorFeaturesLAB('Psycho', action_dir='~/somewhere')
	cflab.analyze_movie()

To screen (the video only) of your film as it is analyzed:

.. code-block:: python

	cflab = ColorFeaturesLAB('Psycho')
	cflab.analyze_movie_with_display()

To play back your analysis later:

.. code-block:: python

	cflab = ColorFeaturesLAB('Psycho')
	cflab.playback_movie()

To directly access your analysis data as a memory-mapped array:

.. code-block:: python

	cflab = ColorFeaturesLAB('Psycho')
	segment_in_seconds = Segment(60, 600) # requesting segment from 1'00" to 10'00"
	data = cflab.cflab_for_segment(segment_in_seconds)

A Note on Paths
===============

This class is set up for the following directory structure. You might want to modify this to suit your needs.

/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.mov
/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.wav
/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.color_lab
...etc...

Advanced Use
============

There is a default stride time of 6 frames (or 24 / 6 = 4 analyzed frames per second), unless overridden. The following would result in 24 / 4 = 6 analyzed frames per second:

.. code-block:: python

	cflab = ColorFeaturesLAB('Psycho', 'stride'=4)

Note that choosing 'stride' values that are not factors of 24 will result in analysis rates that do not fit neatly into one second periods.


Class Module and Specific Functions
===================================

"""
__version__ = '1.0'
__author__ = 'Thomas Stoll'
__copyright__ = "Copyright (C) 2012  Michael Casey, Thomas Stoll, Dartmouth College, All Rights Reserved"
__license__ = "gpl 2.0 or higher"
__email__ = 'thomas.m.stoll@dartmouth.edu'


import sys, time, os
# import the necessary things for OpenCV
try:
	import cv2
	import cv2.cv as cv
	have_cv = True
except ImportError:
	print 'WARNING: Access only, use of methods other than *_color_features_for_segment, etc. will cause errors! Install OpenCV to perform analysis and display movies/data.'
	have_cv = False
import numpy as np
import action.segment as aseg

GRID_X_DIVISIONS = 4
GRID_Y_DIVISIONS = 4
DISPLAY_SHRINK_FACTOR = 0.5

class ColorFeaturesLAB:
	"""
	Color analysis of frame and 4-by-4 grid of subframes in L*a*b* colorspace.
	
	::
	
		action_dir = '~/Movies/action' by default, use an "action" directory in the Movies directory; pass a different directory if necessary.
	
	If you want to run in verbose mode (to see some debug information on calculated frame offsets, analysis ranges, etc.) pass the verbose=True flag here.
	"""
	
	def __init__(self, filename=None, arg=None, **analysis_params):
		self._initialize(filename, analysis_params)
	
	def _initialize(self, filename, analysis_params=None):
		self.analysis_params = self.default_cflab_params()
		self._check_analysis_params(analysis_params)
		ap = self.analysis_params
		
		if filename is None:
			print 'File name missing!'
			return
		else:
			self.movie_path = os.path.join(os.path.expanduser(ap['action_dir']), filename, (filename + ap['movie_extension']))
			self.data_path = os.path.join(os.path.expanduser(ap['action_dir']), filename, (filename + ap['data_extension']))
		
		self.default_color_features_for_segment()
	
	def _check_analysis_params(self, analysis_params=None):
		"""
		Simple mechanism to read in default parameters while substituting custom parameters.
		"""
		self.analysis_params = analysis_params if analysis_params is not None else self.analysis_params
		ap = self.default_cflab_params()
		for k in ap.keys():
			self.analysis_params[k] = self.analysis_params.get(k, ap[k])
		return self.analysis_params

	@staticmethod
	def default_cflab_params():
		analysis_params = {
			'action_dir' : '~/Movies/action/',	# default dir
			'movie_extension' : '.mov',
			'data_extension' : '.color_lab',
			'mode' : 'analyze',			# 'playback' or 'analyze'
			'colorspace' : 'lab', 		# this is redundant, don't try to change it
			'ldims' : 16,				# number of dimensions for L histogram
			'adims' : 16,				# number of dimensions for a histogram saturation
			'bdims' : 16,				# number of dimensions for b histogram value
			'lrange' : [0, 256],		# range to map to/from L
			'arange' : [0, 256],		# range to map to/from a
			'brange' : [0, 256],		# range to map to/from b
			'fps' : 24,					# fps: frames per second
			'offset' : 0,				# time offset in seconds
			'duration' : -1,			# time duration in seconds, -1 (default) maps to full duration of media
			'stride' : 6,				# number of frames to that comprise one analysis point, skips stride - 1 frames
			'threshold' : 0.0,			# (empirical) threshold for histogram; set to a positive number to remove extremely low values
			'verbose' : False,			# useful for debugging
			'display' : True,			# Launch display screen
			'hist_width' : 640,			# to-do
			'hist_height' : 480,		# to-do
			'vert_offset' : 500			# to-do: vertical offset for 17th histogram (the one for the whole, non-gridded frame)
		}
		return analysis_params
	
	def color_features_for_segment(self, segment=aseg.Segment(0, -1)):
		"""
		This will be the interface for grabbing analysis data for segments of the whole film. Uses Segment objects from Bregman/ACTION!
		Takes a file name or complete path of a data file and a Segment object that describes the desired timespan.
		Returns a tuple of memory-mapped arrays corresponding to the full-frame color features followed by the 4 by 4 grid of color histograms: ([NUMBER OF FRAMES, NUMBER OF COLUMNS (3) * NUMBER OF BINS (16) (= 48)], [NUMBER OF FRAMES, NUMBER OF GRID-SQUARES(16) * NUMBER OF COLUMNS (3) * NUMBER OF BINS (16) (=768)])
		::
		
			seg = Segment(360, 720) # which is the same as seg = Segment(360, duration=360)
			raw_hist_data = hist.color_features_for_segment('Psycho.hist', seg)
			raw_hist_data[0].shape
			>>> (1440, 48)
			raw_hist_data[1].shape
			>>> (1440, 768)
		
		"""
		res = self._color_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)
		#return (res[0].reshape((segment.time_span.duration*4), -1), res[1].reshape((segment.time_span.duration*4), -1))
		return (res[0].reshape(-1, 48), res[1].reshape(-1, 768))
	
	def full_color_features_for_segment(self, segment=aseg.Segment(0, -1)):
		"""
		Equivalent to:
		::
		
			color_features_for_segment(...)[0].reshape((segment.time_span.duration*4), -1)
		
		"""
		return self._color_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[0].reshape(-1, 48) #((segment.time_span.duration*4), -1)
	
	def gridded_color_features_for_segment(self, segment=aseg.Segment(0, -1)):
		"""
		Return the gridded histograms (all 16 bins) in the following order:
		::
		
			 0  1  2  3
			 4  5  6  7
			 8  9 10 11
			12 13 14 15
		
		Equivalent to:
		::
		
			color_features_for_segment(...)[1].reshape((segment.time_span.duration*4), -1)
		
		"""
		return self._color_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[1].reshape(-1, 768) #((segment.time_span.duration*4), -1)
	
	def center_quad_color_features_for_segment(self, segment=aseg.Segment(0, -1)):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  X  X  X
			 X  5  6  X
			 X  9 10  X
			 X  X  X  X
		
		Equivalent to:
		::
		
			color_features_for_segment(...)[1][:,[5,6,9,10],...].reshape((segment.time_span.duration*4), -1)
		
		"""
		return self._color_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[1][:,[5,6,9,10],...].reshape(-1, 192) #((segment.time_span.duration*4), -1)

	def middle_band_color_features_for_segment(self, segment=aseg.Segment(0, -1)):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  X  X  X
			 4  5  6  7
			 8  9 10 11
			 X  X  X  X
		
		Equivalent to:
		::
		
			color_features_for_segment(...)[1][:,4:12,...].reshape((segment.time_span.duration*4), -1)
		
		"""
		# print segment
		# print segment.time_span
		self.X = self._color_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1][:,4:12,...].reshape(-1, 384) # (int(segment.time_span.duration*4)), -1)
		return self.X
	
	def plus_band_color_features_for_segment(self, segment=aseg.Segment(0, -1)):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  1  2  X
			 4  5  6  7
			 8  9 10 11
			 X 13 14  X
		
		Equivalent to:
		::
		
			color_features_for_segment(...)[1][:,[1,2,4,5,6,7,8,9,10,11,13,14],...].reshape((segment.time_span.duration*4), -1)
		
		"""
		
		return self._color_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[1][:,[1,2,4,5,6,7,8,9,10,11,13,14],...].reshape(-1, 576) #((segment.time_span.duration*4), -1)

	
	def default_color_features_for_segment(self, func='middle_band_color_features_for_segment', segment=aseg.Segment(0, -1)):
		"""
		DYNAMIC ACCESS FUNCTION
		"""
		return getattr(self,func)(segment)


	def _color_features_for_segment_from_onset_with_duration(self, onset_time=0, duration=60):
		"""
		This will be the interface for grabbing analysis data based on onsets and durations, translating seconds into frames.
		Takes a file name or complete path of a data file, an onset time in seconds, and a duration in seconds.
		Returns a tuple of memory-mapped arrays corresponding to the full-frame histogram followed by the 4 by 4 grid of histograms: ([NUMBER OF FRAMES, 1, NUMBER OF COLUMNS (3), NUMBER OF BINS (16)], [NUMBER OF FRAMES, 16, NUMBER OF COLUMNS (3), NUMBER OF BINS (16)])
		::
		
			raw_hist_data = cflab_for_segment('Psycho.hist', onset_time=360, duration=360)
		
		"""
		ap = self.analysis_params

		onset_frame = int(onset_time * (ap['fps'] / ap['stride']))
		if duration < 0:
			dur_frames = self.determine_movie_length() * (ap['fps'] / ap['stride'])
		else:
			dur_frames = int(duration * (ap['fps'] / ap['stride']))
		
		# print "data path: ", self.data_path
		mapped = np.memmap(self.data_path, dtype='float32', mode='c', offset=onset_frame, shape=(dur_frames,17,3,16))
		return (mapped[:,0,:,:], mapped[:,1:,:,:])
		
	def playback_movie(self, offset=0, duration=-1):
		"""
		Play the movie alongside the analysis data visualization. Played back according to the analysis stride. Equivalent to:
		::
		
			_process_movie(movie_file='Psycho.mov', data_file='Psycho.hist', mode='playback', offset=0, duration=-1, stride=6, display=True)
		
		"""
		self._process_movie(mode='playback', display=True, offset=offset, duration=duration)
	
	def playback_movie_frame_by_frame(self, offset=0, duration=-1, **kwargs):
		"""
		Play the movie alongside the analysis data visualization, supplying the indexing in ANALYSIS frames (usually 4 FPS). Equivalent to:
		::
		
			_process_movie(movie_file='Psycho.mov', data_file='Psycho.hist', mode='playback', offset=0, duration=-1, stride=6, display=True)
		
		"""
		ap = self._check_analysis_params(kwargs)
		offset_s = float(offset) / (ap['fps'] / ap['stride'])
		dur_s = float(duration) / (ap['fps'] / ap['stride'])
		
		self._display_movie_frame_by_frame(mode='playback', display=True, offset=offset_s, duration=dur_s)
	
	def determine_movie_length(self, **kwargs):
	
		ap = self._check_analysis_params(kwargs)
	
		if os.path.exists(self.movie_path) and have_cv:
			capture = cv.CaptureFromFile(self.movie_path)
			dur_total_seconds = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT)) / ap['fps']
		else:
			dsize = os.path.getsize(self.data_path)
			# since we are reading raw color analysis data that always has the same size on disc!
			# the constant had better be correct!
			dur_total_seconds = dsize / 13056 # 16 * 16 * 3 * 17  = 16 bits * 16 bins * 3 color channels * (16 + 1) regions
			# print "total secs: ", dur_total_seconds

		return dur_total_seconds
	
	def analyze_movie(self, offset=0, duration=-1, stride_frames=6):
		"""
		Analyze the movie without displaying on screen. Equivalent to:
		::
		
			_process_movie(movie_file='Psycho.mov', data_file='Psycho.hist', offset=0, duration=-1, stride=6, display=False)
		
		"""
		self._process_movie(mode='analyze', display=False, offset=offset, duration=duration)

	def analyze_movie_with_display(self, offset=0, duration=-1, stride=6):
		"""
		Analyze the movie; display on screen. Equivalent to:
		::
		
			_process_movie(offset=0, duration=-1, stride=6, display=True)
		"""
		self._process_movie(mode='analyze', display=True, offset=offset, duration=duration)
	
	def _analyze_image(self, img, mfp, fpindex, lab, lab_min, lab_max, l_star, a_star, b_star, mask, l_histo, a_histo, b_histo, i, j, grid_flag, grid_height=1, thresh=0.):
		"""
		Image analysis kernel function that is called to analyze each frame image. Look at the main process function to get an idea of how you would call this to return analysis data for a single image. Todo: wrap such a call into a simple one-off function call.
		"""
		cv.CvtColor(img, lab, cv.CV_BGR2Lab)
		cv.Split(lab, l_star, a_star, b_star, None)			# extract the components from the Lab array
		
		cv.CalcHist ([cv.GetImage( l_star )], l_histo, 0, None)
		cv.CalcHist ([cv.GetImage( a_star )], a_histo, 0, None)
		cv.CalcHist ([cv.GetImage( b_star )], b_histo, 0, None)
		cv.ThreshHist(l_histo, thresh)
		cv.ThreshHist(a_histo, thresh)
		cv.ThreshHist(b_histo, thresh)
		
		cv.NormalizeHist(l_histo, 1.0) # L1_NORM!!!
		cv.NormalizeHist(a_histo, 1.0)
		cv.NormalizeHist(b_histo, 1.0)

		l_bins = l_histo.bins
		a_bins = a_histo.bins
		b_bins = b_histo.bins
		
		mfp[fpindex][ ((GRID_X_DIVISIONS*i)+j)+grid_flag ][0] = l_bins
		mfp[fpindex][ ((GRID_X_DIVISIONS*i)+j)+grid_flag ][1] = a_bins
		mfp[fpindex][ ((GRID_X_DIVISIONS*i)+j)+grid_flag ][2] = b_bins
		
		return l_bins, a_bins, b_bins

	def _process_movie(self, **kwargs):
		"""
		Function for analyzing a full film or video. This is where the magic happens when we're making pixel-histogram analyses. Function will exit if neither a movie path nor a data path are supplied. This function is not intended to be called directly. Normally, call one of the three more descriptive functions instead, and it will call this function.
		
		"""
		if not have_cv:
			return
		
		if (self.movie_path is None) or (self.data_path is None):
			print "Must supply both a movie and a data path!"
			return
		
#		analysis_params['colorspace'] = 'lab' # now redundant...
		ap = self._check_analysis_params(kwargs)
				
		capture = cv.CaptureFromFile(self.movie_path)
		
		fps = ap['fps']
		frame_width = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH))
		frame_height = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT))
		frame_size = (frame_width, frame_height)
		grid_width = int(frame_width/GRID_X_DIVISIONS)
		grid_height = int(frame_height/GRID_Y_DIVISIONS)
		grid_size = (grid_width, grid_height)

		verbose = ap['verbose']
		
		if verbose: print ap['lrange'][0], ' | ', ap['arange'][0], ' | ', ap['brange'][0], ' | ', ap['lrange'][1], ' | ', ap['arange'][1], ' | ', ap['brange'][1]
		if verbose: print fps, ' | ', frame_size, ' | ', grid_size
				
		grid_l_star = cv.CreateImage (grid_size, cv.CV_8UC2, 1)
		grid_a_star = cv.CreateImage (grid_size, cv.CV_8UC2, 1)
		grid_b_star = cv.CreateImage (grid_size, cv.CV_8UC2, 1)
		
		grid_mask = cv.CreateImage (grid_size, cv.CV_8UC2, 1)
		grid_lab = cv.CreateImage (grid_size, cv.CV_8UC2, 3 )
	
		l_star = cv.CreateImage (frame_size, cv.CV_8UC2, 1)
		a_star = cv.CreateImage (frame_size, cv.CV_8UC2, 1)
		b_star = cv.CreateImage (frame_size, cv.CV_8UC2, 1)
		
		mask = cv.CreateImage (frame_size, cv.CV_8UC2, 1)
		lab = cv.CreateImage (frame_size, cv.CV_8UC2, 3 )

		dims = ap['ldims']
		
		lab_min = cv.Scalar(ap['lrange'][0], ap['arange'][0], ap['brange'][0], 0)
		lab_max = cv.Scalar(ap['lrange'][1], ap['arange'][1], ap['brange'][1], 0)
		bin_w = int(ap['hist_width'] / ap['ldims'] / GRID_X_DIVISIONS)
		third_bin_w = int(bin_w/3)
	
		l_histo = cv.CreateHist ([ap['ldims']], cv.CV_HIST_ARRAY, [ap['lrange']], 1)
		a_histo = cv.CreateHist ([ap['adims']], cv.CV_HIST_ARRAY, [ap['arange']], 1)
		b_histo = cv.CreateHist ([ap['bdims']], cv.CV_HIST_ARRAY, [ap['brange']], 1)
		
		if ap['verbose']: print third_bin_w
				
		histimg = cv.CreateImage ((frame_width, int(ap['hist_height']*1.5)), cv.IPL_DEPTH_8U, 3)
		
		# last but not least, get total_frame_count and set up the memmapped file
		dur_total_secs = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT) / fps)
		stride_frames = ap['stride']
		if ap['duration'] < 0:
			dur_secs = dur_total_secs
		else:
			dur_secs = ap['duration']
		
		offset_secs = min(max(ap['offset'], 0), dur_total_secs)
		dur_secs = min(max(dur_secs, 0), (dur_total_secs - offset_secs))
		offset_strides = int(offset_secs * (fps / stride_frames))
		dur_strides = int(dur_secs * (fps / stride_frames))
		offset_frames = offset_strides * stride_frames
		dur_frames = dur_strides * stride_frames
				
		if verbose:
			print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
			print 'FRAMES: ', int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT))
			print 'DUR TOTAL: ', dur_total_secs
			print "OFFSET (SECONDS): ", offset_secs
			print "OFFSET (STRIDES): ", offset_strides
			print "OFFSET (FRAMES): ", offset_frames
			print "DUR (SECONDS): ", dur_secs
			print 'DUR (STRIDES): ', dur_strides
			print 'DUR (FRAMES): ', dur_frames
			print "FPS: ", fps
			print "stride_frames: ", stride_frames
		
		# set up memmap
		if ap['mode'] == 'playback' and ap['display'] == True:
			fp = np.memmap(self.data_path, dtype='float32', mode='r+', shape=((offset_strides + dur_strides),17,3,16))
		else:
			fp = np.memmap(self.data_path, dtype='float32', mode='w+', shape=(dur_strides,17,3,16))
		
		# set some drawing constants
		vert_offset = ap['vert_offset']
		ratio = grid_height/255.
		self.frame_idx = offset_frames
		end_frame = offset_frames + dur_frames
		
		if ap['display']:
			cv.NamedWindow('Image', cv.CV_WINDOW_AUTOSIZE)
			cv.NamedWindow('Histogram', frame_width)
			cv.ResizeWindow('Histogram', int(ap['hist_width']*1.333), int(ap['hist_height']*1.5))
			cv.MoveWindow('Histogram', 840, 40)
			
			lcolors, acolors, bcolors= range(16), range(16), range(16)
			for d in range (dims):
				gray_val = (d * 192. / dims) + 32
				lcolors[d] = cv.Scalar(255., gray_val, gray_val)
				acolors[d] = cv.Scalar(gray_val, 128., 128.)
				bcolors[d] = cv.Scalar(gray_val, gray_val, gray_val)
			six_points = self.build_bars(grid_width, grid_height, bin_w, third_bin_w)
			cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, offset_frames)

		while self.frame_idx < end_frame:
			
			if verbose: print 'fr. idx: ', self.frame_idx / float(end_frame), ' (/ ', end_frame, ')'

			if (self.frame_idx%stride_frames) == 0:
				frame = cv.QueryFrame(capture)
				curr_stride_frame = self.frame_idx/stride_frames
				if frame is None: 
					print 'Frame error! Exiting...'
					break # no image captured... end the processing
	
				
				if ap['mode'] == 'playback' and ap['display'] == True:
					lbins, abins, bbins = fp[curr_stride_frame][0][0], fp[curr_stride_frame][0][1], fp[curr_stride_frame][0][2]
					if verbose: print (np.sum(lbins), np.sum(abins), np.sum(bbins))
				else:
					lbins, abins, bbins = self._analyze_image(frame, fp, curr_stride_frame, lab, lab_min, lab_max, l_star, a_star, b_star, mask, l_histo, a_histo, b_histo, 0, 0, 0, 1., thresh=ap['threshold'])
					if verbose: print (cv.Sum(lbins), cv.Sum(abins), cv.Sum(bbins))
				# display stage (full)
				if ap['display']:
					cv.SetZero(histimg) # clear/zero
					for d in range(dims):
						# for all the bins, get the value, and scale to the size of the grid
						if ap['mode'] == 'playback' and ap['display'] == True:
							lval, aval, bval = int(lbins[d] * ratio*255.), int(abins[d] * ratio*255.), int(bbins[d] *ratio*255.)
						else:
							lval, aval, bval = cv.Round(cv.GetReal1D (lbins, d) * ratio*255.), cv.Round (cv.GetReal1D (abins, d) * ratio*255.), cv.Round (cv.GetReal1D (bbins, d) * ratio*255.)
						#draw the rectangle in the wanted color
						self.make_rectangles(histimg, six_points, 6, 0, 0, d, [lval, aval, bval], ratio, [lcolors, acolors, bcolors], voffset=vert_offset)
						# 	def make_rectangles(self, h_img, pts, num_pts, i, j, h, vals, ratio, colors, hoffset=0, voffset=0):
				
				for i in range(GRID_X_DIVISIONS):
					for j in range(GRID_Y_DIVISIONS):
						if ap['mode'] == 'playback' and ap['display'] == True:
							lbins, abins, bbins = fp[(curr_stride_frame)][(j*GRID_X_DIVISIONS)+i+1][0], fp[curr_stride_frame][(j*GRID_X_DIVISIONS)+i+1][1], fp[curr_stride_frame][(j*GRID_X_DIVISIONS)+i+1][2]
							if verbose: print (np.sum(lbins), np.sum(abins), np.sum(bbins))
						else:
							sub = cv.GetSubRect(frame, (i*grid_width, j*grid_height, grid_width, grid_height))
							lbins, abins, bbins = self._analyze_image(sub, fp, (self.frame_idx/stride_frames), grid_lab, lab_min, lab_max, grid_l_star, grid_a_star, grid_b_star, grid_mask, l_histo, a_histo, b_histo, i, j, 1, 1., thresh=100.)
							if verbose: print (cv.Sum(lbins), cv.Sum(abins), cv.Sum(bbins))
						# display stage (grid)
						if ap['display']:
							for  d in range (dims):
								# for all the bins, get the value, and scale to the size of the grid
								if ap['mode'] == 'playback' and ap['display'] == True:
									lval, aval, bval = int(lbins[d] * ratio * 255.0), int(abins[d] * ratio * 255.0), int(bbins[d] * ratio * 255.0)
								else:
									lval, aval, bval = cv.Round(cv.GetReal1D (lbins, d) * ratio*255.), cv.Round (cv.GetReal1D (abins, d) * ratio*255.), cv.Round (cv.GetReal1D (bbins, d) * ratio*255.)
								#draw the rectangle in the wanted color
								self.make_rectangles(histimg, six_points, 6, i, j, d, [lval, aval, bval], ratio, [lcolors, acolors, bcolors], voffset=0)
				
				#### SHOW
				if ap['display']:
					cv.ShowImage('Image', frame)
					cv.ShowImage('Histogram', histimg)
				fp.flush()
				self.frame_idx += 1
				
			elif (self.frame_idx%stride_frames) == 1:
				cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, int((self.frame_idx / stride_frames) + 1) * stride_frames)
				self.frame_idx += 5
			
			# handle events
			k = cv.WaitKey (1)			
			if k % 0x100 == 27:
				# user has press the ESC key, so exit
					break
		
		del fp
		if ap['display']:
			cv.DestroyWindow('Image')
			cv.DestroyWindow('Histogram')	
	
	# frame-by-frame display function
	
	def _display_movie_frame_by_frame(self, **kwargs):
		"""
		Same as _process function's playback capabilities, but with interactive keyboard control.
		
		1 = rewind 10 seconds per display frame
		2 = rewind 1 second per display frame
		3 = rewind 1/4 second (one analysis frame) per display frame

		5 = pause
	
		7 = advance 1/4 second (one analysis frame) per display frame
		8 = advance 1 second per display frame
		9 = advance 10 seconds per display frame
		
		esc = quit visualization
		
		"""
		
		if not have_cv:
			return
		
		if (self.movie_path is None) or (self.data_path is None):
			print "Must supply both a movie and a data path!"
			return
		
#		cflab_params['colorspace'] = 'lab' # now redundant...
		ap = self._check_analysis_params(kwargs)
				
		capture = cv.CaptureFromFile(self.movie_path)
		
		fps = ap['fps']
		hist_width = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH) * DISPLAY_SHRINK_FACTOR)
		hist_height = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT) * DISPLAY_SHRINK_FACTOR)
		hist_size = (hist_width, hist_height)
		grid_width = int(hist_width/GRID_X_DIVISIONS)
		grid_height = int(hist_height/GRID_Y_DIVISIONS)
		grid_size = (grid_width, grid_height)

		verbose = ap['verbose']
		
		if verbose: print ap['lrange'][0], ' | ', ap['arange'][0], ' | ', ap['brange'][0], ' | ', ap['lrange'][1], ' | ', ap['arange'][1], ' | ', ap['brange'][1]
		if verbose: print fps, ' | ', hist_size, ' | ', grid_size
				
		dims = ap['ldims']		
		bin_w = int(ap['hist_width'] / ap['ldims'] / 4)
		third_bin_w = int(bin_w/3)
		
		histimg = cv.CreateImage ((hist_width, int(ap['hist_height']*1.5)), cv.IPL_DEPTH_8U, 3)
		
		# last but not least, get total_frame_count and set up the memmapped file
		dur_total_secs = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT) / fps)
		stride_frames = ap['stride']
		if ap['duration'] < 0:
			dur_secs = dur_total_secs
		else:
			dur_secs = ap['duration']
		
		offset_secs = min(max(ap['offset'], 0), dur_total_secs)
		dur_secs = min(max(dur_secs, 0), (dur_total_secs - offset_secs))
		offset_strides = int(offset_secs * (fps / stride_frames))
		dur_strides = int(dur_secs * (fps / stride_frames))
		offset_frames = offset_strides * stride_frames
		dur_frames = dur_strides * stride_frames
				
		if verbose:
			print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
			print 'FRAMES: ', int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT))
			print 'DUR TOTAL: ', dur_total_secs
			print "OFFSET (SECONDS): ", offset_secs
			print "OFFSET (STRIDES): ", offset_strides
			print "OFFSET (FRAMES): ", offset_frames
			print "DUR (SECONDS): ", dur_secs
			print 'DUR (STRIDES): ', dur_strides
			print 'DUR (FRAMES): ', dur_frames
			print "FPS: ", fps
			print "stride_frames: ", stride_frames
		
		# set up memmap
		# mode should always be playback and dislay should always be true!!!
		if ap['mode'] == 'playback' and ap['display'] == True:
			fp = np.memmap(self.data_path, dtype='float32', mode='r+', shape=((offset_strides + dur_strides),17,3,16))
		
			# set some drawing constants
			vert_offset = ap['vert_offset']
			ratio = grid_height/255.
			
			cv.NamedWindow('Image', cv.CV_WINDOW_AUTOSIZE)
			cv.NamedWindow('Histogram')
 			cv.ResizeWindow('Histogram', int(hist_width*1.333), int(hist_height*0.75))
			cv.MoveWindow('Histogram', (hist_width*2), 40)
			
			lcolors, acolors, bcolors= range(16), range(16), range(16)
			for d in range (dims):
				gray_val = (d * 192. / dims) + 32
				lcolors[d] = cv.Scalar(255., gray_val, gray_val)
				acolors[d] = cv.Scalar(gray_val, 128., 128.)
				bcolors[d] = cv.Scalar(gray_val, gray_val, gray_val)
			six_points = self.build_bars(grid_width, grid_height, bin_w, third_bin_w)
			cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, offset_frames)
			# hist_width, ap, {lcolors, acolors, bcolors}, capture, offset_frames
		
			self.frame_idx = offset_frames
			playing_flag = True
			p_state = 7
			# ap, offset_frames, dur_frames, capture, histimg, dims, six_points, ratio, lcolors, acolors, bcolors, vert_offset, fp, stride_frames
			# for c in range(offset_frames, (offset_frames + dur_frames)):
			while playing_flag:
			
				# div. by 6 everywhere (except in log prints) to count by strides
				if (self.frame_idx%stride_frames) == 0:
					frame = cv.QueryFrame(capture)
					curr_stride_frame = self.frame_idx/stride_frames
					if frame is None: 
						print 'Frame error! Exiting...'
						break # no image captured... end the processing
		
					trio = fp[curr_stride_frame]
					lbins, abins, bbins = trio[0][0], trio[0][1], trio[0][2]
					# display stage (full)
					cv.SetZero(histimg) # clear/zero
					for d in range(dims):
						# for all the bins, get the value, and scale to the size of the grid
						lval, aval, bval = int(lbins[d] * ratio * 255.0), int(abins[d] * ratio * 255.0), int(bbins[d] * ratio * 255.0)
						#draw the rectangle in the wanted color
						self.make_rectangles(histimg, six_points, 6, 0, 0, d, [lval, aval, bval], ratio, [lcolors, acolors, bcolors], voffset=int(hist_height*1.25)) #, hoffset=int(hist_width*2)
					for i in range(4):
						for j in range(4):
							lbins, abins, bbins = trio[(j*4)+i+1][0], trio[(j*4)+i+1][1], trio[(j*4)+i+1][2]
							# display stage (grid)
							for  d in range (dims):
								# for all the bins, get the value, and scale to the size of the grid
								if ap['mode'] == 'playback' and ap['display'] == True:
									lval, aval, bval = int(lbins[d] * ratio * 255.0), int(abins[d] * ratio * 255.0), int(bbins[d] * ratio * 255.0)
								#draw the rectangle in the wanted color
								self.make_rectangles(histimg, six_points, 6, i, j, d, [lval, aval, bval], ratio, [lcolors, acolors, bcolors]) #, voffset=0, hoffset=int(hist_width*2)
					
					#### SHOW
					cv.ShowImage('Image', frame)
					cv.ShowImage('Histogram', histimg)
					fp.flush()
		
					print self.frame_idx, ':: ', (float(self.frame_idx - offset_frames) / dur_frames)
					
				# check p_state				
				if p_state == 1: # rew. 10 sec.
					self.frame_idx -= 240
					cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, self.frame_idx)
				elif p_state == 2: # rew. 1 sec.
					self.frame_idx -= 24
					cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, self.frame_idx)
				elif p_state == 3:
					self.frame_idx -= 6
					cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, self.frame_idx)
				elif p_state == 0:
					cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, self.frame_idx)
				elif p_state == 7:
					self.frame_idx += 6
					cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, self.frame_idx)
				elif p_state == 8: # adv. 1 sec.
					self.frame_idx += 24
					cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, self.frame_idx)					
				elif p_state == 9: # adv. 10 sec.
					self.frame_idx += 240
					cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES, self.frame_idx)
				
				# handle key events
				k = cv.WaitKey (250)
				if verbose is True:
					print '>>>>>>>>>>>>>>>>>>'
					print k % 0x100
					print p_state
				
				if k % 0x100 == 27:
					# user has press the ESC key, so exit
					playing_flag = False
					break
				elif k % 0x100 == 49:
					p_state = 1
				elif k % 0x100 == 50:
					p_state = 2
				elif k % 0x100 == 51:
					p_state = 3
				elif k % 0x100 == 55:
					p_state = 7
				elif k % 0x100 == 56:
					p_state = 8
				elif k % 0x100 == 57:
					p_state = 9
				elif k % 0x100 == 53:
					p_state = 0			 					
			
			del fp
			if ap['display']:
				cv.DestroyWindow('Image')
				cv.DestroyWindow('Histogram')	

	
	
	# GUI helper functions
	
	def build_bars(self, gw, gh, bw, tbw):
		"""
		Display helper function. Build list of points for the 16 trios of bars.
		"""
		six_points = np.ndarray((16,16,6,2), dtype=int)
		for i in range(GRID_X_DIVISIONS):
			for j in range(GRID_Y_DIVISIONS):
				for h in range(16):
					six_points[h][(i*GRID_X_DIVISIONS)+j][0] = [(j*gw)+(h * bw), (i+1)*gh]
					six_points[h][(i*GRID_X_DIVISIONS)+j][1] = [(j*gw)+((h+1) * bw)-(2*tbw), ((i+1)*gh)]
					six_points[h][(i*GRID_X_DIVISIONS)+j][2] = [(j*gw)+(h * bw)+(tbw), (i+1)*gh]
					six_points[h][(i*GRID_X_DIVISIONS)+j][3] = [(j*gw)+((h+1) * bw)-(tbw), ((i+1)*gh)]
					six_points[h][(i*GRID_X_DIVISIONS)+j][4] = [(j*gw)+(h * bw)+(2*tbw), (i+1)*gh]
					six_points[h][(i*GRID_X_DIVISIONS)+j][5] = [(j*gw)+((h+1) * bw), ((i+1)*gh)]
		return six_points
	
	def make_rectangles(self, h_img, pts, num_pts, i, j, h, vals, ratio, colors, hoffset=0, voffset=0):
		"""
		Display helper function. Make a bar for the histogram.
		"""
		#print pts
		for n in range(int(num_pts/2)):
		# 			print (pts[h][(i*GRID_X_DIVISIONS)+j][2*n][0] + hoffset, pts[h][(i*GRID_X_DIVISIONS)+j][2*n][1] + int(voffset*1.25)), ' || ', (pts[h][(i*GRID_X_DIVISIONS)+j][2*n+1][0] + hoffset, pts[h][(i*GRID_X_DIVISIONS)+j][2*n+1][1] + int(voffset*1.0) - int(vals[n]*ratio))
			cv.Rectangle (h_img,
							(pts[h][(i*GRID_X_DIVISIONS)+j][2*n][0] + hoffset, pts[h][(i*GRID_X_DIVISIONS)+j][2*n][1] + int(voffset)),
							(pts[h][(i*GRID_X_DIVISIONS)+j][2*n+1][0] + hoffset, pts[h][(i*GRID_X_DIVISIONS)+j][2*n+1][1] + int(voffset) - int(vals[n]*ratio)),
							colors[n][h], -1, 8, 0)
# 			if (i == 0) and (j == 0):
# 				print '--00----------------------'
# 				print pts[h][(i*GRID_X_DIVISIONS)+j][2*n+1][1]
# 				print int(voffset)
# 				print int(vals[n]*ratio)
