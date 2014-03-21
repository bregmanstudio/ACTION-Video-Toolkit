# phase_correlation.py - Phase Correlation data from video frames
# Bregman:ACTION - Cinematic information retrieval toolkit

"""
Part of Bregman:ACTION - Cinematic information retrieval toolkit

Overview
========

Use the phase correlation extractor class to analyze streams of images or video files. The phase correlation features class steps through movie frames and extracts two types of information. The first are features for the entire image. The second are set of 64 histograms, each describing a region of the image. The regions are arranged in an even 8-by-8 non-overlapping grid, with the first region at the upper left and the last at the lower right. These values are stored in a binary file using Numpy memory-mapped arrays.

In order to reduce the amount of data involved (and the processing time involved), a stride parameter is used by default during access. This parameter is the number of movie frames to account for in one analysis frame. The default is 6. There is no averaging or interpolation, the "skipped" frames are simply dropped.

Creation and Parameters
=======================

Instantiate the PhaseCorrelation class, optionally with additional keyword arguments:

.. code-block:: python

	pcorr = PhaseCorrelation (fileName, param1=value1, param2=value2, ...)

The global default phasecorr_features-extractor parameters are defined in a parameter dictionary: 

.. code-block:: python

    default_phasecorr_params = {
		'action_dir' : '~/Movies/action', # default dir
		ETC...
	}

The full list of settable parameters, with default values and explanations:

+------------------------+-----------------+----------------------------------------------------+
| keyword                | default         | explanation                                        |
+========================+=================+====================================================+
| action_dir             | ~/Movies/action | default dir                                        |
+------------------------+-----------------+----------------------------------------------------+
| movie_extension        | .mov            |                                                    |
+------------------------+-----------------+----------------------------------------------------+
| data_extension         | .phasecorr      | this is what will be output and expected for input |
+------------------------+-----------------+----------------------------------------------------+
| mode                   | analyze         | 'playback' or 'analyze'                            |
+------------------------+-----------------+----------------------------------------------------+
| fps                    | 24              | fps: frames per second                             |
+------------------------+-----------------+----------------------------------------------------+
| offset                 | 0               | time offset in seconds                             |
+------------------------+-----------------+----------------------------------------------------+
| duration               | -1              | time duration in seconds, -1 (default) maps to full|
|                        |                 | duration of media                                  |
+------------------------+-----------------+----------------------------------------------------+
| stride                 | 1               | number of video frames to that comprise one        |
|                        |                 | analysis frame, skips stride - 1 frames            |
+------------------------+-----------------+----------------------------------------------------+
| grid_divs_x            | 8               | number of divisions along x axis                   |
+------------------------+-----------------+----------------------------------------------------+
| grid_divs_y            | 8               | number of divisions along y axis                   |
+------------------------+-----------------+----------------------------------------------------+
| verbose                | False           | useful for debugging                               |
+------------------------+-----------------+----------------------------------------------------+
| display                | True            | launch display screen during analysis              |
+------------------------+-----------------+----------------------------------------------------+
| Parameters for display...                                                                     |
+------------------------+-----------------+----------------------------------------------------+
| viz_width_ratio        | 1.0             | for visualization of histogram (ratio of movie     |
|                        |                 | viewer width)                                      |
+------------------------+-----------------+----------------------------------------------------+
| viz_height_ratio       | 1.0             | for visualization of histogram (ratio)             |
+------------------------+-----------------+----------------------------------------------------+
| viz_horiz_offset_ratio | 1.0             | horizontal offset for view window (ratio)          |
+------------------------+-----------------+----------------------------------------------------+
| viz_vert_offset_ratio  | 0.0             | vertical offset for view window (ratio)            |
+------------------------+-----------------+----------------------------------------------------+

Parameter keywords can be passed explicitly as formal arguments or as a keyword argument parameter dict:, e.g.:

.. code-block:: python

   pcorr = PhaseCorrelation(fileName, vrange=[32, 256], verbose=True )
   pcorr = PhaseCorrelation(fileName, **{'vrange':[32, 256], 'verbose':True} )

Using PhaseCorrelation
======================
The functions of the PhaseCorrelation class define the various use cases or patterns.

Analyze a full film:

.. code-block:: python

	pcorr = PhaseCorrelation('Psycho')
	pcorr.analyze_movie() # Assumes that ~/Movies/action/Psycho.mov exists; returns otherwise

This also works, so you can define your own file locations:

.. code-block:: python

	pcorr = PhaseCorrelation('Psycho', action_dir='~/somewhere')
	pcorr.analyze_movie()

To screen (the video only) of your film as it is analyzed:

.. code-block:: python

	pcorr = PhaseCorrelation('Psycho')
	pcorr.analyze_movie_with_display()

To play back your analysis later:

.. code-block:: python

	pcorr = PhaseCorrelation('Psycho')
	pcorr.playback_movie()

To directly access your analysis data as a memory-mapped array:

.. code-block:: python

	import action.segment as aseg
	pcorr = PhaseCorrelation('Psycho')
	segment_in_seconds = aseg.Segment(60, 600) # requesting segment from 1'00" to 10'00"
	data = pcorr._phasecorr_features_for_segment_from_onset_with_duration(segment_in_seconds)

More commonly, the user should use the access functions that refer to the screen area from which he/she desires data:

.. code-block:: python

	pcorr = PhaseCorrelation('Psycho')
	fullseg = aseg.Segment(0, pcorr.determine_movie_length()) # requesting entire film
	data = pcorr.middle_band_phasecorr_features_for_segment(fullseg)


A Note on Paths
===============

This class (as well as all feature classes in ACTION) is set up for the following directory structure. You may place your action data directories anywhere, and there can be multiple directories/databases.

/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.mov
/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.wav
/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.phasecorr
...etc...


Advanced Use
============

There is a default stride time of 6 frames (or 24 / 6 = 4 analyzed frames per second), unless overridden. The following would result in 24 / 4 = 6 analyzed frames per second:

.. code-block:: python

	pcorr = PhaseCorrelation('Psycho', 'stride'=4)

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
	HAVE_CV = True
except ImportError:
	print 'WARNING: Access only, use of methods other than *_phasecorr_features_for_segment, etc. will cause errors! Install OpenCV to perform analysis and display movies/data.'
	HAVE_CV = False
import numpy as np
import action.segment as aseg
import action.actiondata as actiondata
import json


class PhaseCorrelation:
	"""
	Phase correlation of frame and 8-by-8 grid of subframes.
	
	::
	
		action_dir = '~/Movies/action' by default, use an "action" directory in the Movies directory; pass a different directory if necessary.
	
	If you want to run in verbose mode (to see some debug information on calculated frame offsets, analysis ranges, etc.) pass the verbose=True flag here.
	"""
	
	def __init__(self, filename='Vertigo', arg=None, **analysis_params):
		"""
		"""
		self._initialize(filename, analysis_params)
	
	def _initialize(self, filename, analysis_params=None):
		"""
		"""
		# self.analysis_params = self.default_phasecorr_params()
		self._check_pcorr_params(analysis_params)
		ap = self.analysis_params
		
		if filename is None:
			print 'File name missing!'
			return
		else:
			self.movie_path = os.path.join(os.path.expanduser(ap['action_dir']), filename, (filename + ap['movie_extension']))
			self.data_path = os.path.join(os.path.expanduser(ap['action_dir']), filename, (filename + ap['data_extension']))
			self.json_path = os.path.join(os.path.expanduser(ap['action_dir']), filename, (filename + '.json'))
			print self.json_path
			self.filename = filename

		# self.determine_movie_length() no need
 		if (os.path.exists(self.json_path) != True):
 			self._write_metadata_to_json()
		ap['afps'] = self._read_json_value('fps')

		#TO DO: try to naively get some data and store in a class var, as in color_lab...
	
	def _check_pcorr_params(self, analysis_params=None):
		"""
		Simple mechanism to read in default parameters while substituting custom parameters.
		"""
		self.analysis_params = analysis_params if analysis_params is not None else self.analysis_params
		dpcp = self.default_phasecorr_params()
		for k in dpcp.keys():
			self.analysis_params[k] = self.analysis_params.get(k, dpcp[k])
		return self.analysis_params

	@staticmethod
	def default_phasecorr_params():
		analysis_params = {
			'action_dir' : os.path.expanduser('~/Movies/action/'),	# default dir
			'movie_extension' : '.mov',
			'data_extension' : '.phasecorr',
			'mode' : 'analyze',			# 'playback' or 'analyze'
			'grid_divs_x' : 8,
			'grid_divs_y' : 8,
			'fps' : 24,					# fps: frames per second
			'afps' : 24,				# afps: frames per second for access or alignment
			'offset' : 0,				# time offset in seconds
			'duration' : -1,			# time duration in seconds, -1 (default) maps to full duration of media
			'stride' : 1,				# number of frames to that comprise one analysis point, skips stride - 1 frames
			'grid_divs_x' : 8,
			'grid_divs_y' : 8,
			'verbose' : False,			# useful for debugging
			'display' : True,			# Launch display screen
			'viz_shrink_factor' : 0.5,	# (adjustable) ratio for size of histogram window
			'viz_width_ratio' : 1.0,	# (adjustable) ratio for width of histogram window size
			'viz_height_ratio' : 1.0,	# (adjustable) ratio for height of histogram window size
			'viz_horiz_offset_ratio' : 1.0,		# (adjustable) horizontal distance of histogram window upper left corner offset from video window
			'viz_vert_offset_ratio' : 0.0			# (adjustable) vertical distance of histogram window upper left corner offset from video window
		}
		return analysis_params

	def _write_metadata_to_json(self):
		"""
		"""
		title = self.filename
		capture = cv2.VideoCapture(self.movie_path)
		fps = capture.get(cv.CV_CAP_PROP_FPS)
		aspect = capture.get(cv.CV_CAP_PROP_FRAME_WIDTH / cv.CV_CAP_PROP_FRAME_HEIGHT)
		frames = capture.get(cv.CV_CAP_PROP_FRAME_COUNT)
		length = frames / fps
		
		
		movdict = {'title':title, 'fps':fps, 'aspect': aspect,'frames': frames, 'length':length}
		fp = file(self.json_path, 'w')
		fp.write(json.dumps(movdict))
		fp.close()
		del capture
		return 1
	
	def _read_json_value(self, key='fps'):
# 		fp = file(self.json_path, 'r')
		jsonfile = open(self.json_path)
		jsondata = json.load(jsonfile)
		return jsondata[key]


	def all_phasecorr_features_for_segment(self, segment=aseg.Segment(0, -1), access_stride=6):
		"""
		This will be the interface for grabbing analysis data for segments of the whole film. Uses Segment objects from ACTION!
		Takes a movie/file name and a Segment object that describes the desired timespan.
		Returns a tuple of memory-mapped arrays corresponding to the full-frame color features followed by the 4 by 4 grid of color histograms: ([NUMBER OF FRAMES, NUMBER OF COLUMNS (3) * NUMBER OF BINS (16) (= 48)], [NUMBER OF FRAMES, NUMBER OF GRID-SQUARES(16) * NUMBER OF COLUMNS (3) * NUMBER OF BINS (16) (=768)])
		::
		
			pcorr = phase_correlation.PhaseCorrelation('Psycho')
			seg = Segment(360, 720) # which is the same as seg = Segment(360, duration=360)
			raw_hist_data = pcorr.phasecorr_features_for_segment(seg)
			raw_hist_data[0].shape
			>>> (1440, 48)
			raw_hist_data[1].shape
			>>> (1440, 768)
		
		"""
		res = self._phasecorr_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[0:-1:access_stride]
		return (res[0].reshape(-1, 2), res[1].reshape(-1, 128))
	
	def full_phasecorr_features_for_segment(self, segment=aseg.Segment(0, -1), access_stride=6):
		"""
		Equivalent to:
		::
		
			phasecorr_features_for_segment(...)[0].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._phasecorr_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[0].reshape(-1, 2)[0:-1:access_stride]
		return self.X
	
	def gridded_phasecorr_features_for_segment(self, segment=aseg.Segment(0, -1), access_stride=6):
		"""
		Return the gridded histograms (all 64 bins) in the following order:
		::
		
			 0  1  2  3  4  5  6  7
			 8  9 10 11 12 13 14 15
			 16 .  .  .  .  .  . 23
			 24 .
			 .  .
			 .  .
			 .  .
			 56 .  .  .  .  .  . 63
		
		Equivalent to:
		::
		
			phasecorr_features_for_segment(...)[1].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._phasecorr_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[1].reshape(-1, 128)[0:-1:access_stride]
		return self.X
	
	def center_quad_phasecorr_features_for_segment(self, segment=aseg.Segment(0, -1), access_stride=6):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  X ..  X  X
			 X 18 .. 21  X
			 X  . ..  .  X
			 X  . ..  .  X
			 X 42 .. 45  X
			 X  X ..  X  X
		
		Equivalent to:
		::
		
			phasecorr_features_for_segment(...)[1][:,[18..21,26..29,34..37,42..45,..],...].reshape((segment.time_span.duration*4), -1)
		
		"""
		cq_array = range(18,22)+range(26,30)+range(34,38)+range(42,46)
		self.X = self._phasecorr_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[1][:,cq_array,...].reshape(-1, 32)[0:-1:access_stride]
		return self.X

	def middle_band_phasecorr_features_for_segment(self, segment=aseg.Segment(0, -1), access_stride=6):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  X ..  X  X
			16  . ..  . 23
			 .  . ..  .  .
			 .  . ..  .  .
			40  . ..  . 47
			 X  X ..  X  X
		
		Equivalent to:
		::
		
			phasecorr_features_for_segment(...)[1][:,16:47,...].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._phasecorr_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1][:,16:48,...].reshape(-1, 64)[0:-1:access_stride]
		return self.X
	
	def plus_band_phasecorr_features_for_segment(self, segment=aseg.Segment(0, -1), access_stride=6):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  X  2 ..  5  X  X
			 X  X 10 .. 13  X  X
			16  . ..        . 23
			 .  . ..        .  .
			 .  . ..        .  .
			40  . ..        . 47
			X  X  50 .. 53  X  X
			X  X  58 .. 61  X  X
		
		Equivalent to:
		::
		
			phasecorr_features_for_segment(...)[1][:,[2..5,10..13,16..47,50..53,58..61],...].reshape((segment.time_span.duration*4), -1)
		
		"""
		plus_array = range(2,6)+range(10,14)+range(16,48)+range(50,54)+range(58,62)
		return self._phasecorr_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[1][:,plus_array,...].reshape(-1, 96)[0:-1:access_stride]

	def default_phasecorr_features_for_segment(self, func='middle_band_phasecorr_features_for_segment', segment=aseg.Segment(0, -1), access_stride=6):
		"""
		DYNAMIC ACCESS FUNCTION
		"""
		return getattr(self,func)(segment, access_stride)

	def phasecorr_features_for_segment_with_stride(self, grid_flag=1, segment=aseg.Segment(0, -1), access_stride=6):

		ap = self._check_pcorr_params()
		
		onset_frame = int(segment.time_span.start_time * (ap['fps'] / ap['stride']))
		print onset_frame
		if segment.time_span.duration < 0:
			dur_frames = int(self.determine_movie_length() * (ap['fps'] / ap['stride']))
		else:
			dur_frames = int(segment.time_span.duration * (ap['fps'] / ap['stride']))
		print self.determine_movie_length()
		print dur_frames
		
		if grid_flag == 0:
			data24 = self._phasecorr_features_for_segment_from_onset_with_duration(onset_frame, dur_frames)[0]
			# probably should have some error handling here if the reshape fails
			return np.reshape(data24[onset_frame:dur_frames:access_stride,:], (-1, 2))
		else:
			data24 = self._phasecorr_features_for_segment_from_onset_with_duration(onset_frame, dur_frames)[1]
			# probably should have some error handling here if the reshape fails
			return np.reshape(data24[onset_frame:dur_frames:access_stride,:], (-1, 128))

	def _phasecorr_features_for_segment_from_onset_with_duration(self, onset_frame=0, duration_frames=-1):
		"""
		This will be the interface for grabbing analysis data based on onsets and durations, translating seconds into frames.
		Takes a file name or complete path of a data file, an onset time in seconds, and a duration in seconds.
		Returns a tuple of memory-mapped arrays corresponding to the full-frame histogram followed by the 4 by 4 grid of histograms: ([NUMBER OF FRAMES, 1, NUMBER OF COLUMNS (3), NUMBER OF BINS (16)], [NUMBER OF FRAMES, 16, NUMBER OF COLUMNS (3), NUMBER OF BINS (16)])
		::
		
			raw_hist_data = pcorr_for_segment('Psycho', onset_time=360, duration=360)
		
		"""
		ap = self.analysis_params
		frames_per_stride = (24.0 / ap['stride']) # 24.0, not ap['fps']

		print ap['fps']
		print ap['stride']

		onset_frame = int(onset_frame)
		if duration_frames < 0:
			dur_frames = int(self.determine_movie_length() * frames_per_stride)
		else:
			dur_frames = int(duration_frames * frames_per_stride)
		
		print 'dur: ', dur_frames
		# print "data path: ", self.data_path
		mapped = np.memmap(self.data_path, dtype='float32', mode='c', offset=onset_frame, shape=(dur_frames,65,2))
		ad = actiondata.ActionData()
		mapped = ad.interpolate_time(mapped, ap['afps'])
		return (mapped[:,64,:], mapped[:,:64,:])
		
	def playback_movie(self, offset=0, duration=-1):
		"""
		Play the movie alongside the analysis data visualization, supplying the indexing as seconds. Note that if the data was analyzed with a stride factor, there will not be data for all 24 possible frames per second. Equivalent to:
		::
		
			_process_movie(movie_file='Psycho.mov', data_file='Psycho.color_lab', mode='playback', offset=0, duration=-1, stride=6, display=True)
		
		"""
		self._process_movie(mode='playback', display=True, offset=offset, duration=duration)
	
	def playback_movie_frame_by_frame(self, offset=0, duration=-1, **kwargs):
		"""
		Play the movie alongside the analysis data visualization, supplying the indexing in ANALYSIS frames (usually 4 FPS). Doesn't use general _process function; uses _display_movie_frame_by_frame()
		"""
		ap = self._check_pcorr_params(kwargs)
		offset_s = float(offset) / (ap['fps'] / ap['stride'])
		dur_s = float(duration) / (ap['fps'] / ap['stride'])
		
		self._display_movie_frame_by_frame(mode='playback', display=True, offset=offset_s, duration=dur_s)
	
	def determine_movie_length(self, **kwargs):
	
		ap = self.analysis_params
	
		if os.path.exists(self.movie_path) and HAVE_CV:
			# self.capture = cv.CaptureFromFile(self.movie_path)
	 		self.capture = cv2.VideoCapture(self.movie_path)

			dur_total_seconds = int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT) / ap['fps'])
			print "mov total secs: ", dur_total_seconds
		elif os.path.exists(self.data_path):
			dsize = os.path.getsize(self.data_path)
			# since we are reading raw color analysis data that always has the same size on disc!
			# the constant had better be correct!
			print "dsize: ", dsize
			dur_total_aframes = dsize / float(((ap['grid_divs_x'] * ap['grid_divs_y'])+1) * 2 * 4) # REGIONS * CHANNELS * BINS * BYTES
			print 'dtaf: ', dur_total_aframes
			dur_total_seconds = int(dur_total_aframes / (ap['fps'] / ap['stride']))
			print "total secs: ", dur_total_seconds
		else:
			dur_total_seconds = -1
			print "Cannot determine movie duration. Both the movie and data files are missing!"
		self.analysis_params['duration'] = dur_total_seconds			
		return dur_total_seconds
	
	def analyze_movie(self, offset=0, duration=-1, stride_frames=6):
		"""
		Analyze the movie without displaying on screen. Equivalent to:
		::
		
			_process_movie(movie_file='Psycho.mov', data_file='Psycho.color_lab', offset=0, duration=-1, stride=6, display=False)
		
		"""
		self._process_movie(mode='analyze', display=False, offset=offset, duration=duration)

	def analyze_movie_with_display(self, offset=0, duration=-1, stride=6):
		"""
		Analyze the movie; display on screen. Equivalent to:
		::
		
			_process_movie(offset=0, duration=-1, stride=6, display=True)
		"""
		self._process_movie(mode='analyze', display=True, offset=offset, duration=duration)
	
	def _process_movie(self, **kwargs):
	
		"""
			Function for analyzing a full film or video. This is where the magic happens when we're making pixel-histogram analyses. Function will exit if neither a movie path nor a data path are supplied. This function is not intended to be called directly. Normally, call one of the three more descriptive functions instead, and it will call this function.
		
		"""

		if not HAVE_CV:
			print "WARNING: You must install OpenCV in order to analyze or view!"
			return
		
		if (self.movie_path is None) or (self.data_path is None):
			print "ERROR: Must supply both a movie and a data path!"
			return
		
		ap = self._check_pcorr_params(kwargs)
		verbose = ap['verbose']
		
		self.capture = cv2.VideoCapture(self.movie_path)
		
		fps = ap['fps']
		grid_x_divs = ap['grid_divs_x']
		grid_y_divs = ap['grid_divs_y']
		frame_width = int(self.capture.get(cv.CV_CAP_PROP_FRAME_WIDTH))
		frame_height = int(self.capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
		frame_size = (frame_width, frame_height)
		grid_width = int(frame_width/grid_x_divs)
		grid_height = int(frame_height/grid_y_divs)
		grid_size = (grid_width, grid_height)
		
		centers_x = range((frame_width/16),frame_width,(frame_width/8))
		centers_y = range((frame_height/16),frame_height,(frame_height/8))
		
		if verbose:
			print fps, ' | ', frame_size, ' | ', grid_size
		
		# container for prev. frame's grayscale subframes
		prev_sub_grays = []				
		
		# last but not least, get total_frame_count and set up the memmapped file
		dur_total_secs = int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT) / fps)
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
			print 'FRAMES: ', int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT))
			print 'DUR TOTAL: ', dur_total_secs
			print "OFFSET (SECONDS): ", offset_secs
			print "OFFSET (STRIDES): ", offset_strides
			print "OFFSET (FRAMES): ", offset_frames
			print "DUR (SECONDS): ", dur_secs
			print 'DUR (STRIDES): ', dur_strides
			print 'DUR (FRAMES): ', dur_frames
			print 'XDIVS: ', grid_x_divs
			print 'YDIVS: ', grid_y_divs
			print "FPS: ", fps
			print "stride_frames: ", stride_frames
		
		# set up memmap
		if ap['mode'] == 'playback' and ap['display'] == True:
			fp = np.memmap(self.data_path, dtype='float32', mode='r+', shape=((offset_strides + dur_strides),(64+1),2))
		else:
			fp = np.memmap(self.data_path, dtype='float32', mode='w+', shape=(dur_strides,(64+1),2))
		
		# set some drawing constants
		vert_offset = int(frame_height*ap['viz_vert_offset_ratio'])	# NA
		ratio = grid_height/255.									# NA
		self.frame_idx = offset_frames
		end_frame = offset_frames + dur_frames
		
		if ap['display']:
			cv.NamedWindow('Image', cv.CV_WINDOW_AUTOSIZE)

		self.capture.set(cv.CV_CAP_PROP_POS_FRAMES, offset_frames)
		
		ret, frame = self.capture.read()
		if frame is None: 
			print 'Frame error! Exiting...'
			return # no image captured... end the processing
		frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		prev_frame_gray = np.float32(frame_gray[:])
		self.frame_idx += 1
		
		fhann = cv2.createHanningWindow((frame_width,frame_height), cv2.CV_32FC1)
		ghann = cv2.createHanningWindow((grid_width,grid_height), cv2.CV_32FC1)
		
		for row in range(grid_y_divs):
			for col in range(grid_x_divs):
				prev_sub_grays += [np.float32(frame_gray[(row*grid_height):((row+1)*grid_height), (col*grid_width):((col+1)*grid_width)])]

		while self.frame_idx < end_frame:
			
			if (self.frame_idx % 1000) == 0: print 'fr. idx: ', self.frame_idx, ' (', self.frame_idx / float(end_frame), ' | ', end_frame, ')'

			# grab next frame
			ret, frame = self.capture.read()
			if frame is None: 
				print 'Frame error! Exiting...'
				break # no image captured... end the processing
			frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			
			if ap['mode'] == 'playback' and ap['display'] == True:
				fret = fp[self.frame_idx][64]
				# print fret
			else:
				fret, fres = cv2.phaseCorrelateRes(prev_frame_gray, np.float32(frame_gray[:]), fhann)
				print fret
				if abs(fres) > 0.01:
					fp[self.frame_idx][64] = [(fret[0]/frame_width),(fret[1]/frame_height)]
				else:
					fp[self.frame_idx][64] = [0,0]
			
			# display stage (full)
			for row in range(grid_y_divs):
				for col in range(grid_x_divs):
					if ap['mode'] == 'playback':
						cell = ((row*8)+col)
						gret = fp[self.frame_idx][cell]
					else:
						sub_gray = np.float32(frame_gray[(row*grid_height):((row+1)*grid_height), (col*grid_width):((col+1)*grid_width)][:])
						gret, gres = cv2.phaseCorrelateRes(prev_sub_grays[(row*grid_x_divs)+col], sub_gray, ghann)

						prev_sub_grays[(row*grid_x_divs)+col] = sub_gray
						# if verbose:
						#	print (row, col, (gret, gres))
						if abs(gres) > 0.7: # WAS 0.01!!!!
							fp[self.frame_idx][(row*grid_x_divs)+col] = [(gret[0]/grid_width),(gret[1]/grid_height)]
 						else:
							fp[self.frame_idx][(row*grid_x_divs)+col] = [0,0]
					if ap['display'] == True:
# 						print gret
# 						print grid_size
# 						print abs(gret[0]*10.0)
# 						print grid_size[0]
# 						print abs(gret[1]*10.0)
# 						print grid_size[1]
						
						if (gret[0] != 0 and gret[1] != 0):
							xval = int(min((gret[0]*100), grid_size[0])+centers_x[col])
							yval = int(min((gret[1]*100), grid_size[1])+centers_y[row])
							# print ((centers_x[i], centers_y[j], xval, yval), False, (0,255,255))
							cv2.line(frame, (centers_x[col], centers_y[row]), (xval, yval), (255,255,255))
				
				#### SHOW
				if ap['display']:
					cv.ShowImage('Image', cv.fromarray(frame))
				fp.flush()
			
			self.frame_idx += 1
			self.prev_gray = np.float32(frame_gray[:])
			
			# handle events for abort
			k = cv.WaitKey (1)	
			if k % 0x100 == 27:
				# user has press the ESC key, so exit
					break
		
		del fp
		if ap['display']:
			cv2.destroyAllWindows()
	
	# frame-by-frame display function - TO DO
