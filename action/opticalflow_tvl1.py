# opticalflow_tvl1.py - color features (L*a*b*) histogram data from video frames
# Bregman:ACTION - Cinematic information retrieval toolkit

"""
Part of Bregman:ACTION - Cinematic information retrieval toolkit

Overview
========

*PLEASE NOTE*: This TVL1 OpticalFlow class is set up for access only! TO DO: provide playback of visualization and provide OpenFrameworks/C++ analysis code.

Use the TVL1 OpticalFlow class to access optical flow features. The first 16 raw bins are a histogram over 16 angle-bins (22.5 degrees per bin) of detected angle features for the entire image. The second is a set of sixteen histograms, each describing a region of the image. The regions are arranged in an even four-by-four non-overlapping grid, with the first region at the upper left and the last at the lower right. These values, in sequence, are stored in a binary file.

In order to reduce the amount of data involved (and the processing time involved), a stride parameter is used. This number is the number of movie frames to account for in one analysis frame. The default is 6. As of version 1.0, there is no averaging or interpolation, the "skipped" frames are simply dropped.

Creation and Parameters
=======================

Instantiate the OpticalFlowTVL1 class, optionally with additional keyword arguments:

.. code-block:: python

	myTVL1 = OpticalFlowTVL1 (fileName, param1=value1, param2=value2, ...)

The global default tvl1 features-extractor parameters are defined in a parameter dictionary: 

.. code-block:: python

    default_tvl1_params = {
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
| data_extension         | .tvl1           | this is what will be output and expected for input |
+------------------------+-----------------+----------------------------------------------------+
| mode                   | playback        | 'playback' ONLY                                    |
+------------------------+-----------------+----------------------------------------------------+
| fps                    | 24              | fps: frames per second                             |
+------------------------+-----------------+----------------------------------------------------+
| afps                   | 24              | afps: 'access' frames per second                   |
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
| theta_divs             | 16              | number of divisions of angle data                  |
+------------------------+-----------------+----------------------------------------------------+
| verbose                | True            | useful for debugging                               |
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

   tvl1 = OpticalFlowTVL1(fileName, verbose=True )
   tvl1 = OpticalFlowTVL1(fileName, **{'verbose':True} )

If you ``from action.suite import *``, you will have to use the module_name.Class pattern to create ACTION visual features classes.

.. code-block:: python
	
   tvl1 = opticalflow_tvl1.OpticalFlowTVL1(fileName, verbose=True )


Using OpticalFlowTVL1
======================
The functions of the OpticalFlowTVL1 class define the various use cases or patterns.

Analyze a full film:

.. code-block:: python

	tvl1 = OpticalFlowTVL1('Psycho')
	tvl1.analyze_movie() # Assumes that ~/Movies/action/Psycho.mov exists; returns otherwise

This also works, so you can define your own file locations:

.. code-block:: python

	tvl1 = OpticalFlowTVL1('Psycho', action_dir='~/somewhere')
	tvl1.analyze_movie()

To screen (the video only) of your film as it is analyzed:

.. code-block:: python

	tvl1 = OpticalFlowTVL1('Psycho')
	tvl1.analyze_movie_with_display()

To play back your analysis later:

.. code-block:: python

	tvl1 = OpticalFlowTVL1('Psycho')
	tvl1.playback_movie()

To directly access your analysis data as a memory-mapped array:

.. code-block:: python
	
	import action.segment as aseg
	tvl1 = OpticalFlowTVL1('Psycho')
	segment_in_seconds = Segment(60, 600) # requesting segment from 1'00" to 10'00"
	data = tvl1._tvl1_features_for_segment_from_onset_with_duration(segment_in_seconds)
	
More commonly, the user should use the access functions that refer to the screen area from which he/she desires data:

.. code-block:: python

	cfl = OpticalFlowTVL1('Psycho')
	fullseg = Segment(0, tvl1.determine_movie_length()) # requesting entire film
	data = tvl1.middle_band_color_features_for_segment(fullseg)



A Note on Paths
===============

This class is set up for the following directory structure. You might want to modify this to suit your needs.

/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.mov
/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.tvl1
...etc...

Advanced Use
============

There is a default stride time of 6 frames (or 24 / 6 = 4 analyzed frames per second), unless overridden. The following would result in 24 / 4 = 6 analyzed frames per second:

.. code-block:: python

	tvl1 = OpticalFlowTVL1('Psycho', 'stride'=4)

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
	print 'WARNING: Access only, use of methods other than *_tvl1_features_for_segment, etc. will cause errors! Install OpenCV to perform analysis and display movies/data.'
	HAVE_CV = False
import numpy as np
import json, math
from segment import *
from actiondata import *
ad = ActionData()
av = ActionView()

class OpticalFlowTVL1:
	"""
	Optical Flow (TVL1) analysis of frame and 4-by-4 grid of subframes.
	
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
		# self.analysis_params = self.default_tvl1_params()
		self._check_tvl1_params(analysis_params)
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
# 		if ! exists(self.json_path):
# 			self._write_metadata_to_json()
		ap['afps'] = self._read_json_value('fps')
		
		# try to naively get some data and store in a class var
		if os.path.exists(self.data_path):
			self.default_tvl1_features_for_segment()
	
	def _check_tvl1_params(self, analysis_params=None):
		"""
		Simple mechanism to read in default parameters while substituting custom parameters.
		"""
		self.analysis_params = analysis_params if analysis_params is not None else self.analysis_params
		dcfp = self.default_tvl1_params()
		for k in dcfp.keys():
			self.analysis_params[k] = self.analysis_params.get(k, dcfp[k])
		return self.analysis_params

	@staticmethod
	def default_tvl1_params():
		analysis_params = {
			'action_dir' : os.path.expanduser('~/Movies/action/'),	# default dir
			'movie_extension' : '.mov',
			'data_extension' : '.tvl1',
			'mode' : 'playback',				# 'playback'
			'grid_divs_x' : 8,
			'grid_divs_y' : 8,
			'hist_bins' : 8,					# each bin is 22.5 degrees?
			'fps' : 24,							# fps: frames per second
			'afps' : 24,						# afps: frames per second for access or alignment
			'offset' : 0,						# time offset in seconds
			'duration' : -1,					# time duration in seconds, -1 (default) maps to full duration of media
			'stride' : 1,						# number of frames to that comprise one analysis point, skips stride - 1 frames
			'verbose' : True,					# useful for debugging
			'display' : True,					# Launch display screen
			'hist_shrink_factor' : 0.5,			# (adjustable) ratio for size of histogram window
			'hist_width_ratio' : 0.5,			# (adjustable) ratio for width of histogram window size
			'hist_height_ratio' : 0.5,			# (adjustable) ratio for height of histogram window size
			'hist_horiz_offset_ratio' : 1.0,	# (adjustable) horizontal distance of histogram window upper left corner offset from video window
			'hist_vert_offset_ratio' : 0.0		# (adjustable) vertical distance of histogram window upper left corner offset from video window
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
	
	def all_tvl1_features_for_segment(self, segment=Segment(0, -1)):
		"""
		This will be the interface for grabbing analysis data for segments of the whole film. Uses Segment objects from Bregman/ACTION!
		Takes a file name or complete path of a data file and a Segment object that describes the desired timespan.
		Returns a tuple of memory-mapped arrays corresponding to the full-frame tvl1 features followed by the 4 by 4 grid
		::
			
			seg = Segment(360, 720) # which is the same as seg = Segment(360, duration=360)
			raw_tvl1_data = hist.all_tvl1_features_for_segment(seg)
			raw_tvl1_data[0].shape
			>>> (1440, 48)
			raw_tvl1_data[1].shape
			>>> (1440, 768)

		"""
		res = self._tvl1_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)
		return (res[0].reshape(-1, 16), res[1].reshape(-1, 128))
	
	def full_tvl1_features_for_segment(self, segment=Segment(0, -1)):
		"""
		Equivalent to:
		::
		
			all_tvl1_features_for_segment(...)[0].reshape((segment.time_span.duration*4), -1)		

		"""
		self.X = self._tvl1_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[0].reshape(-1, 16)
		return self.X
	
	def gridded_tvl1_features_for_segment(self, segment=Segment(0, -1)):
		"""
		Return the gridded histograms (all 16 bins) in the following order:
		::
		
			 0  1  2  3
			 4  5  6  7
			 8  9 10 11
			12 13 14 15
		
		Equivalent to:
		::
		
			all_tvl1_features_for_segment(...)[1].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._tvl1_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1].reshape(-1, 128)
		return self.X

	def center_quad_tvl1_features_for_segment(self, segment=Segment(0, -1)):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  X  X  X
			 X  5  6  X
			 X  9 10  X
			 X  X  X  X
		
		Equivalent to:
		::
		
			all_tvl1_features_for_segment(...)[1][:,[5,6,9,10],...].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._tvl1_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1][ range((18*2),(22*2))+range((26*2),(30*2))+range((34*2),(38*2))+range((52*2),(56*2)) ].reshape(-1, 32)
		return self.X

	def middle_band_tvl1_features_for_segment(self, segment=Segment(0, -1)):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  X  X  X
			 4  5  6  7
			 8  9 10 11
			 X  X  X  X
		
		Equivalent to:
		::
		
			all_tvl1_features_for_segment(...)[1][:,::2][,16:48].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._tvl1_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1][:,(16*2):(48*2)].reshape(-1, 64)
		return self.X
	
	def plus_band_tvl1_features_for_segment(self, segment=Segment(0, -1)):
		"""
		Return the gridded histograms after applying the following filter:
		::
		
			 X  1  2  X
			 4  5  6  7
			 8  9 10 11
			 X 13 14  X
		
		Equivalent to:
		::
		
				all_tvl1_features_for_segment(...)[1][:,range(2,6)+range(10,14)+range(16,48)+range(50,54)+range(58,62)].reshape(-1, 576)
		
		"""
		
		self.X = self._tvl1_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1][:,range((2*2),(6*2))+range((10*2),(14*2))+range((16*2),(48*2))+range((50*2),(54*2))+range((58*2),(62*2))].reshape(-1, 96)
		return self.X
	
	def default_tvl1_features_for_segment(self, func='middle_band_tvl1_features_for_segment', segment=Segment(0, -1)):
		"""
		DYNAMIC ACCESS FUNCTION
		"""
		return getattr(self,func)(segment)

	def _tvl1_features_for_segment_from_onset_with_duration(self, onset_s=0, duration_s=60):
		"""
		This will be the interface for grabbing analysis data based on onsets and durations, translating seconds into frames.
		Takes a file name or complete path of a data file, an onset time in seconds, and a duration in seconds.
		Returns a tuple of memory-mapped arrays corresponding to the full-frame histogram followed by the 4 by 4 grid of histograms: ([NUMBER OF FRAMES, 1, NUMBER OF COLUMNS (3), NUMBER OF BINS (16)], [NUMBER OF FRAMES, 16, NUMBER OF COLUMNS (3), NUMBER OF BINS (16)])
		::
		
			raw_tvl1_data = tvl1_for_segment('Psycho.hist', onset_time=360, duration=360)
		
		"""
		ap = self.analysis_params
		frames_per_astride = (24.0 / ap['stride']) # 24.0 == ap['fps']

		print ap['fps']
		print ap['stride']
		print duration_s

		onset_frame = int(onset_s * frames_per_astride)
		if duration_s < 0:
			dur_frames = self.determine_movie_length() * frames_per_astride * (ap['afps'] / ap['fps']) # convert back to aframes
		else:
			dur_frames = duration_s * frames_per_astride * (ap['afps'] / ap['fps'])
		
		# memmap
		print dur_frames
		mapped = np.memmap(self.data_path, dtype='float32', mode='c') #, offset=onset_frame, shape=(dur_frames,(128+16)))
		mapped = mapped.reshape((-1,144))
		mapped = ad.interpolate_time(mapped, ap['afps'])
		return (mapped[:,:16], mapped[:,16:])
		
	
# 	def playback_movie_frame_by_frame(self, offset=None, duration=None):
# 		"""
# 		Play the movie alongside the analysis data visualization, supplying the indexing in ANALYSIS frames (usually 4 FPS). Equivalent to:
# 		::
# 		
# 			_process_movie(movie_file='Psycho.mov', data_file='Psycho.hist', mode='playback', offset=0, duration=-1, stride=6, display=True)
# 		
# 		"""
# 		# ap = self._check_tvl1_params(kwargs)
# 		ap = self.analysis_params
# 		frames_per_stride = (ap['fps'] / ap['stride'])
# 		
# 		if offset is None:
# 			offset_s = float(ap['offset']) / frames_per_stride
# 		else:
# 			offset_s = float(offset) / frames_per_stride
# 		if duration is None:
# 			dur_s = float(ap['duration']) / frames_per_stride
# 		else:
# 			dur_s = float(duration) / frames_per_stride
# 		
# 		self._display_movie_frame_by_frame(mode='playback', display=True, offset=offset_s, duration=dur_s)
# 	
	def determine_movie_length(self, **kwargs):
	
		# ap = self._check_tvl1_params(kwargs)
		ap = self.analysis_params
		strides_per_second = (ap['fps'] / ap['stride'])
	
		if os.path.exists(self.movie_path) and HAVE_CV:
			self.capture = cv2.VideoCapture(self.movie_path)
			dur_total_seconds = int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT) / ap['fps'])
			print "mov total secs: ", dur_total_seconds
		elif os.path.exists(self.data_path):
			dsize = os.path.getsize(self.data_path)
			print "dsize: ", dsize
			# since we are reading raw tvl1 analysis data that always has the same size on disc!
			# the constant had better be correct!
			dur_total_aframes = dsize / float(((ap['grid_divs_x'] * ap['grid_divs_y'] * 2) + 16) * 4) # REGIONS * CHANNELS + 16 * BYTES
			print 'dtaf: ', dur_total_aframes
			dur_total_seconds = (dur_total_aframes / strides_per_second) * (ap['fps'] / ap['afps'])
			print "total secs: ", dur_total_seconds
		else:
			dur_total_seconds = -1
			print "Cannot determine movie duration. Both the movie and data files are missing!"
		self.analysis_params['duration'] = dur_total_seconds
		return dur_total_seconds
		
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
		if not HAVE_CV:
			print "WARNING: You must install OpenCV in order to analyze or view!"
			return
		
		if (self.movie_path is None) and (self.data_path is None):
			print "Both movie path and data path are missing! Please supply at least one."
			return None
		
		have_mov = os.path.exists(self.movie_path)
		have_data = os.path.exists(self.data_path)
		
		if (have_mov is False) and (have_data is False):
			print "Both movie file and data file are missing! Please supply at least one."
			return None
		
 		ap = self._check_tvl1_params(kwargs)
		ap = self.analysis_params
		verbose = ap['verbose']
		
		if have_mov is True:
	 		self.capture = cv2.VideoCapture(self.movie_path)
			frame_width = int(self.capture.get(cv.CV_CAP_PROP_FRAME_WIDTH))
			frame_height = int(self.capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
		else:
			frame_width = 800
			frame_height = int(float(frame_width) * self._read_json_value('aspect'))
			print self._read_json_value('aspect')
		
		fps = ap['fps']
		grid_x_divs = ap['grid_divs_x']
		grid_y_divs = ap['grid_divs_y']
		frame_size = (frame_width, frame_height)
		grid_width = int(frame_width/float(grid_x_divs))
		grid_height = int(frame_height/float(grid_y_divs))
		grid_size = (grid_width, grid_height)
		
		print frame_width
		print frame_height
		
		centers_x = range((frame_width/16),frame_width,(frame_width/8))
		centers_y = range((frame_height/16),frame_height,(frame_height/8))
		
		if verbose:
			print fps, ' | ', frame_size, ' | ', grid_size
				
		# container for prev. frame's grayscale subframes
		prev_sub_grays = []								

		if ap['offset'] > 0:
			offset_secs = ap['offset']
		else:
			offset_secs = 0
		
		print "%%% ", ap['duration']
		
		if ap['duration'] > 0:
			dur_secs = ap['duration']
		elif ap['duration'] < 0:
			ap['duration'] = self.determine_movie_length()
		else:
			print "Duration cannot be 0."
			return
		dur_secs = ap['duration']
		
		stride_frames = ap['stride']
		stride_hop = stride_frames - 1

# 		print "1. ", ap['duration']
# 		print "2. ", dur_secs
		
		# check offset first, then compress duration, if needed
		offset_secs = min(max(offset_secs, 0), ap['duration'])
		dur_secs = min(max(dur_secs, 0), (ap['duration'] - offset_secs))
		offset_strides = int(offset_secs * (fps / stride_frames))
		dur_strides = int(dur_secs * (fps / stride_frames))
		offset_frames = offset_strides * stride_frames
		dur_frames = dur_strides * stride_frames
		
		if verbose:
			print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
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
		# mode should always be playback and dislay should always be true!!!
		if ap['mode'] == 'playback' and ap['display'] == True and have_data:
			fp = np.memmap(self.data_path, dtype='float32', mode='r', shape=((offset_strides + dur_strides),((8*8*16)+16)))
			cv2.namedWindow('Image', cv.CV_WINDOW_AUTOSIZE)
			cv2.resizeWindow('Image', frame_width, frame_height)
		else:
			return
		self.frame_idx = offset_frames
		end_frame = offset_frames + dur_frames

		if have_mov:
			self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, offset_frames)
			ret, frame = self.capture.read()
			if frame is None: 
				print 'Frame error! Exiting...'
				return # no image captured... end the processing		
					
		else:
			frame = np.empty((frame_width, frame_height), np.uint8)
			print frame.shape

		self.frame_idx += 1
		playing_flag = True
		p_state = 7
		
		cv.ShowImage('Image', cv.fromarray(frame))

		while playing_flag:
			
			if have_mov:
				# grab next frame
				ret, frame = self.capture.read()
				if frame is None: 
					print 'Frame error! Exiting...'
					break # no image captured... end the processing
			else:
				frame[:] = 0
				
			# display stage (gridded)
			if ap['mode'] == 'playback' and ap['display']:
				currframe = fp[self.frame_idx,:512]
			else:
				return
			currframe = fp[self.frame_idx,:128]
			framemin = currframe.min()
			framemax = currframe.max()
			framerange = framemax - framemin
			if framerange > 0:
				
				grays = np.multiply(np.subtract(currframe, framemin), (2*math.pi / framerange))
				grays_ma = np.ma.masked_invalid(grays)
				grays = grays_ma.filled(0.0)
				print grays

# 				for row in range(grid_y_divs):
# 					for col in range(grid_x_divs):
# 							gry = int(grays[(row*grid_x_divs)+(col*2)])
# 							if gry>0:
# 								gry /= 2
# 								gry += 256
# 								cv2.line(frame, (centers_x[col], centers_y[row]), ((centers_x[col]+THETAS_X[wdg]), (centers_y[row]+THETAS_Y[wdg])), (gry,gry,gry))
				#### SHOW
				cv.ShowImage('Image', cv.fromarray(frame))
				fp.flush()
	
				print self.frame_idx, ':: ', (float(self.frame_idx - offset_frames) / dur_frames)
				
			# check p_state				
			if p_state == 1: # rew. 10 sec.
				self.frame_idx -= 240
			elif p_state == 2: # rew. 1 sec.
				self.frame_idx -= 24
			elif p_state == 3:
				self.frame_idx -= 6
			elif p_state == 0:
				pass
			elif p_state == 7:
				self.frame_idx += 6
			elif p_state == 8: # adv. 1 sec.
				self.frame_idx += 24
			elif p_state == 9: # adv. 10 sec.
				self.frame_idx += 240
			if have_mov:
				self.capture.set(cv.CV_CAP_PROP_POS_FRAMES, self.frame_idx)				
			
			# handle key events
			k = cv.WaitKey (25)
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
