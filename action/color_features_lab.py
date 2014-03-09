# color_features_lab.py - color features (L*a*b*) histogram data from video frames
# Bregman:ACTION - Cinematic information retrieval toolkit

"""
Part of Bregman:ACTION - Cinematic information retrieval toolkit

Overview
========

Use the color features (L*a*b*) extractor class to analyze streams of images or video files. The color features class steps through movie frames and extracts histograms for two frame types. The first is a histogram of color features for the entire image. The second is a set of sixteen histograms, each describing a region of the image. The regions are arranged in an even four-by-four non-overlapping grid, with the first region at the upper left and the last at the lower right. These values, in sequence, are stored in a binary file.

In order to reduce the amount of data involved (and the processing time involved), a stride parameter is used. This number is the number of movie frames to account for in one analysis frame. The default is 6. As of version 1.0, there is no averaging or interpolation, the "skipped" frames are simply dropped.

Creation and Parameters
=======================

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

+------------------------+-----------------+----------------------------------------------------+
| keyword                | default         | explanation                                        |
+========================+=================+====================================================+
| action_dir             | ~/Movies/action | default dir                                        |
+------------------------+-----------------+----------------------------------------------------+
| movie_extension        | .mov            |                                                    |
+------------------------+-----------------+----------------------------------------------------+
| data_extension         | .color_lab      | this is what will be output and expected for input |
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
| stride                 | 6               | number of video frames to that comprise one        |
|                        |                 | analysis frame, skips stride - 1 frames            |
+------------------------+-----------------+----------------------------------------------------+
| threshold              | 0.0             | (empirical) threshold for histogram values; set to |
|                        |                 | a positive number to remove extremely low values   |
+------------------------+-----------------+----------------------------------------------------+
| verbose                | True            | useful for debugging                               |
+------------------------+-----------------+----------------------------------------------------+
| display                | True            | launch display screen during analysis              |
+------------------------+-----------------+----------------------------------------------------+
| Parameters for color features histograms and display...                                       |
+------------------------+-----------------+----------------------------------------------------+
| colorspace             | lab             | this is redundant, don't try to change it          |
+------------------------+-----------------+----------------------------------------------------+
| ldims                  | 16              | number of dimensions for L (luminosity)            |
+------------------------+-----------------+----------------------------------------------------+
| adims                  | 16              | number of dimensions for a (color)                 |
+------------------------+-----------------+----------------------------------------------------+
| bdims                  | 16              | number of dimensions for b (color)                 |
+------------------------+-----------------+----------------------------------------------------+
| lrange                 | [0, 256]        | range to map to/from L                             |
+------------------------+-----------------+----------------------------------------------------+
| arange                 | [0, 256]        | range to map to/from a                             |
+------------------------+-----------------+----------------------------------------------------+
| brange                 | [0, 256]        | range to map to/from b                             |
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
	
	import action.segment as aseg
	cflab = ColorFeaturesLAB('Psycho')
	segment_in_seconds = aseg.Segment(60, 600) # requesting segment from 1'00" to 10'00"
	data = cflab.cflab_for_segment(segment_in_seconds)

A Note on Paths
===============

This class is set up for the following directory structure. You might want to modify this to suit your needs.

/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.mov
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
	HAVE_CV = True
except ImportError:
	print 'WARNING: Access only, use of methods other than *_color_features_for_segment, etc. will cause errors! Install OpenCV to perform analysis and display movies/data.'
	HAVE_CV = False
import numpy as np
import action.segment as aseg
import action.actiondata as actiondata
import json

class ColorFeaturesLAB:
	"""
	Color analysis of frame and 4-by-4 grid of subframes in L*a*b* colorspace.
	
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
		# self.analysis_params = self.default_cflab_params()
		self._check_cflab_params(analysis_params)
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
		
		# self.determine_movie_length()
		
		# try to naively get some data and store in a class var
		if os.path.exists(self.data_path):
			self.default_color_features_for_segment()
	
	def _check_cflab_params(self, analysis_params=None):
		"""
		Simple mechanism to read in default parameters while substituting custom parameters.
		"""
		self.analysis_params = analysis_params if analysis_params is not None else self.analysis_params
		dcfp = self.default_cflab_params()
		for k in dcfp.keys():
			self.analysis_params[k] = self.analysis_params.get(k, dcfp[k])
		return self.analysis_params

	@staticmethod
	def default_cflab_params():
		analysis_params = {
			'action_dir' : os.path.expanduser('~/Movies/action/'),	# default dir
			'movie_extension' : '.mov',
			'data_extension' : '.color_lab',
			'mode' : 'analyze',			# 'playback' or 'analyze'
			'colorspace' : 'lab', 		# this is redundant, don't try to change it
			'grid_divs_x' : 4,
			'grid_divs_y' : 4,
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
	
	def all_color_features_for_segment(self, segment=aseg.Segment(0, -1)):
		"""
		This will be the interface for grabbing analysis data for segments of the whole film. Uses Segment objects from Bregman/ACTION!
		Takes a file name or complete path of a data file and a Segment object that describes the desired timespan.
		Returns a tuple of memory-mapped arrays corresponding to the full-frame color features followed by the 4 by 4 grid of color histograms: ([NUMBER OF FRAMES, NUMBER OF COLUMNS (3) * NUMBER OF BINS (16) (= 48)], [NUMBER OF FRAMES, NUMBER OF GRID-SQUARES(16) * NUMBER OF COLUMNS (3) * NUMBER OF BINS (16) (=768)])
		::
			
			seg = Segment(360, 720) # which is the same as seg = Segment(360, duration=360)
			raw_hist_data = hist.all_color_features_for_segment(seg)
			raw_hist_data[0].shape
			>>> (1440, 48)
			raw_hist_data[1].shape
			>>> (1440, 768)

		"""
		res = self._color_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)
		return (res[0].reshape(-1, 48), res[1].reshape(-1, 768))
	
	def full_color_features_for_segment(self, segment=aseg.Segment(0, -1)):
		"""
		Equivalent to:
		::
		
			all_color_features_for_segment(...)[0].reshape((segment.time_span.duration*4), -1)		

		"""
		self.X = self._color_features_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)[0].reshape(-1, 48)
		return self.X
	
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
		
			all_color_features_for_segment(...)[1].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._color_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1].reshape(-1, 768)
		return self.X

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
		
			all_color_features_for_segment(...)[1][:,[5,6,9,10],...].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._color_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1][:,[5,6,9,10],...].reshape(-1, 192)
		return self.X

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
		
			all_color_features_for_segment(...)[1][:,4:12,...].reshape((segment.time_span.duration*4), -1)
		
		"""
		self.X = self._color_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1][:,4:12,...].reshape(-1, 384)
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
		
				all_color_features_for_segment(...)[1][:,[1,2,4,5,6,7,8,9,10,11,13,14],...].reshape(-1, 576)
		
		"""
		
		self.X = self._color_features_for_segment_from_onset_with_duration(int(segment.time_span.start_time), int(segment.time_span.duration))[1][:,4:12,...].reshape(-1, 576)
		return self.X
	
	def default_color_features_for_segment(self, func='middle_band_color_features_for_segment', segment=aseg.Segment(0, -1)):
		"""
		DYNAMIC ACCESS FUNCTION
		"""
		return getattr(self,func)(segment)

# 	def color_features_for_segment_with_stride(self, grid_flag=1, segment=aseg.Segment(0, -1), access_stride=6):
# 
# 		#ap = self._check_cflab_params()
# 		ap = self.analysis_params
# 		frames_per_stride = (ap['fps'] / ap['stride'])
#		
# 		onset_frame = int(segment.time_span.start_time * frames_per_stride)
# 		print onset_frame
# 		if segment.time_span.duration < 0:
# 			dur_frames = self.determine_movie_length()
# 		else:
# 			dur_frames = int(segment.time_span.duration * frames_per_stride)
# 		print self.s_movie_length()
# 		print dur_frames
# 		
# 		if grid_flag == 0:
# 			data24 = self._color_features_for_segment_from_onset_with_duration(onset_frame, dur_frames)[0]
# 			# probably should have some error handling here if the reshape fails
# 			return np.reshape(data24[onset_frame:dur_frames:access_stride,:], (-1, 48))
# 		else:
# 			data24 = self._color_features_for_segment_from_onset_with_duration(onset_frame, dur_frames)[0]
# 			# probably should have some error handling here if the reshape fails
# 			return np.reshape(data24[onset_frame:dur_frames:access_stride,:], (-1, 768))

	def _color_features_for_segment_from_onset_with_duration(self, onset_time=0, duration=60):
		"""
		This will be the interface for grabbing analysis data based on onsets and durations, translating seconds into frames.
		Takes a file name or complete path of a data file, an onset time in seconds, and a duration in seconds.
		Returns a tuple of memory-mapped arrays corresponding to the full-frame histogram followed by the 4 by 4 grid of histograms: ([NUMBER OF FRAMES, 1, NUMBER OF COLUMNS (3), NUMBER OF BINS (16)], [NUMBER OF FRAMES, 16, NUMBER OF COLUMNS (3), NUMBER OF BINS (16)])
		::
		
			raw_hist_data = cflab_for_segment('Psycho.hist', onset_time=360, duration=360)
		
		"""
		ap = self.analysis_params
		frames_per_stride = (24.0 / ap['stride']) # 24.0, not ap['fps']

		onset_frame = int(onset_time * frames_per_stride)
		if duration < 0:
			dur_frames = self.determine_movie_length() * frames_per_stride
		else:
			dur_frames = int(duration * frames_per_stride)
		
		# memmap
		mapped = np.memmap(self.data_path, dtype='float32', mode='c', offset=onset_frame, shape=(dur_frames,17,3,16))
		ad = actiondata.ActionData()
		mapped = ad.interpolate_time(mapped, ap['fps'])
		return (mapped[:,0,:,:], mapped[:,1:,:,:])

	def convert_lab_to_l(self, data):
		"""
		Zero out the a* and b* columns.
		"""
		data_L = np.empty_like(data)
		data_L[:] = data
		data_L = np.reshape(data_L, (data.shape[0], -1, 3))
		data_L[:,:,1:] = 0.0
		return np.reshape(data_L, (data.shape[0], -1))

		
	def playback_movie(self, offset=None, duration=None):
		"""
		Play the movie alongside the analysis data visualization, supplying the indexing as seconds. Note that if the data was analyzed with a stride factor, there will not be data for all 24 possible frames per second. Equivalent to:
		::
		
			_process_movie(movie_file='Psycho.mov', data_file='Psycho.hist', mode='playback', offset=0, duration=-1, stride=6, display=True)
		
		"""
		self._process_movie(mode='playback', display=True, offset=offset, duration=duration)
	
	
	def playback_movie_frame_by_frame(self, offset=None, duration=None):
		"""
		Play the movie alongside the analysis data visualization, supplying the indexing in ANALYSIS frames (usually 4 FPS). Equivalent to:
		::
		
			_process_movie(movie_file='Psycho.mov', data_file='Psycho.hist', mode='playback', offset=0, duration=-1, stride=6, display=True)
		
		"""
		# ap = self._check_cflab_params(kwargs)
		ap = self.analysis_params
		frames_per_stride = (ap['fps'] / ap['stride'])
		
		if offset is None:
			offset_s = float(ap['offset']) / frames_per_stride
		else:
			offset_s = float(offset) / frames_per_stride
		if duration is None:
			dur_s = float(ap['duration']) / frames_per_stride
		else:
			dur_s = float(duration) / frames_per_stride
		
		self._display_movie_frame_by_frame(mode='playback', display=True, offset=offset_s, duration=dur_s)
	
	def determine_movie_length(self, **kwargs):
	
		# ap = self._check_cflab_params(kwargs)
		ap = self.analysis_params
		frames_per_stride = (ap['fps'] / ap['stride'])
	
		if os.path.exists(self.movie_path) and HAVE_CV:
			self.capture = cv2.VideoCapture(self.movie_path)
			dur_total_seconds = int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT) / ap['fps'])
			print "mov total secs: ", dur_total_seconds
		elif os.path.exists(self.data_path):
			dsize = os.path.getsize(self.data_path)
			print "dsize: ", dsize
			# since we are reading raw color analysis data that always has the same size on disc!
			# the constant had better be correct!
			dur_total_aframes = dsize / float(((ap['grid_divs_x'] * ap['grid_divs_y'])+1) * 3 * ap['ldims'] * 4) # REGIONS * CHANNELS * BINS * BYTES
			print 'dtaf: ', dur_total_aframes
			dur_total_seconds = int(dur_total_aframes / frames_per_stride)
			print "total secs: ", dur_total_seconds
		else:
			dur_total_seconds = -1
			print "Cannot determine movie duration. Both the movie and data files are missing!"
		self.analysis_params['duration'] = dur_total_seconds
		return dur_total_seconds
	
	def analyze_movie(self):
		"""
		Analyze the movie without displaying on screen. Equivalent to:
		::
		
			_process_movie(mode='analyze', display=False)
		
		"""
		self._process_movie(mode='analyze', display=False)

	def analyze_movie_with_display(self):
		"""
		Analyze the movie; display on screen. Equivalent to:
		::
		
			_process_movie(mode='analyze', display=True)
		"""
		self._process_movie(mode='analyze', display=True)
	
	def _process_movie(self, mode='analyze', display=True, offset=None, duration=None):
		"""
		Function for analyzing a full film or video. This is where the magic happens when we're making pixel-histogram analyses. Function will exit if neither a movie path nor a data path are supplied. This function is not intended to be called directly. Normally, call one of the three more descriptive functions instead, and it will call this function.
		
		"""
		if not HAVE_CV:
			return
		
		if (self.movie_path is None) or (self.data_path is None):
			print "Must supply both a movie and a data path!"
			return
		
		# ap = self._check_cflab_params(kwargs)
		ap = self.analysis_params
				
		self.capture = cv2.VideoCapture(self.movie_path)
		
		self._write_metadata_to_json()
		# probably should generate and check for errors
		
		ap['mode'] = mode
		ap['display'] = display
		
		fps = ap['fps']
		grid_x_divs = ap['grid_divs_x']
		grid_y_divs = ap['grid_divs_y']
		frame_width = int(self.capture.get(cv.CV_CAP_PROP_FRAME_WIDTH))
		frame_height = int(self.capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
		frame_size = (frame_width, frame_height)
		hist_width = int(frame_width * ap['hist_width_ratio'])
		hist_height = int(frame_height * ap['hist_height_ratio'])
		hist_size = (hist_width, hist_height)
		grid_width = int(hist_width/grid_x_divs)
		grid_height = int(hist_height/grid_y_divs)
		grid_size = (grid_width, grid_height)

		verbose = ap['verbose']
		
		if verbose:
			print ap['lrange'][0], ' | ', ap['arange'][0], ' | ', ap['brange'][0], ' | ', ap['lrange'][1], ' | ', ap['arange'][1], ' | ', ap['brange'][1]
			print fps, ' | ', hist_size, ' | ', grid_size
		
		grid_l_star = np.zeros((16,1), dtype=np.float32)
		grid_a_star = np.zeros((16,1), dtype=np.float32)
		grid_b_star = np.zeros((16,1), dtype=np.float32)
		
		grid_mask = np.zeros(grid_size, dtype=np.float32)
		grid_lab = np.zeros((grid_size[0], grid_size[1], 3), dtype=np.float32)
	
		l_star = np.zeros((16,1), dtype=np.float32)
		a_star = np.zeros((16,1), dtype=np.float32)
		b_star = np.zeros((16,1), dtype=np.float32)
		
		mask = np.zeros((frame_size[0], frame_size[1], 3), dtype=np.float32)
		lab = np.zeros((frame_size[0], frame_size[1], 3), dtype=np.float32)

		dims = ap['ldims']
		
		lab_min = (ap['lrange'][0], ap['arange'][0], ap['brange'][0])
		lab_max = (ap['lrange'][1], ap['arange'][1], ap['brange'][1])
		bin_w = int((hist_width * ap['hist_width_ratio']) / (ap['ldims'] * grid_x_divs))
		third_bin_w = int(bin_w/3)
	
		l_histo = np.arange(ap['lrange'][0], ap['lrange'][1], ap['ldims']).reshape((ap['ldims'],1))
		a_histo = np.arange(ap['arange'][0], ap['arange'][1], ap['adims']).reshape((ap['adims'],1))
		b_histo = np.arange(ap['brange'][0], ap['brange'][1], ap['bdims']).reshape((ap['bdims'],1))
		
		if ap['verbose']: print third_bin_w
				
		histimg = np.zeros((int(hist_height*1.25), int(hist_width), 3), np.uint8)
		
		# last but not least, get total_frame_count and set up the memmapped file
		# dur_total_secs = int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT) / fps)
		if offset is None:
			offset_secs = ap['offset']
		else:
			offset_secs = offset
		if duration is None:
			dur_secs = ap['duration']
		else:
			dur_secs = duration
		
		stride_frames = ap['stride']
		stride_hop = stride_frames - 1
		
		# check offset first, then compress duration, if needed
		offset_secs = min(max(offset_secs, 0), ap['duration'])
		dur_secs = min(max(dur_secs, 0), (ap['duration'] - offset_secs))
		offset_strides = int(offset_secs * (fps / stride_frames))
		dur_strides = int(dur_secs * (fps / stride_frames))
		offset_frames = offset_strides * stride_frames
		dur_frames = dur_strides * stride_frames
		
		if verbose:
			print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
			print 'FRAMES: ', int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT))
			print 'DUR TOTAL: ', ap['duration']
			print "OFFSET (SECONDS): ", offset_secs
			print "OFFSET (STRIDES): ", offset_strides
			print "OFFSET (FRAMES): ", offset_frames
			print "DUR (SECONDS): ", dur_secs
			print 'DUR (STRIDES): ', dur_strides
			print 'DUR (FRAMES): ', dur_frames
			print "FPS: ", fps
			print "stride_frames: ", stride_frames
		
		# set up memmap
		if ap['mode'] == 'playback' and display == True:
			fp = np.memmap(self.data_path, dtype='float32', mode='r+', shape=((offset_strides + dur_strides),(ap['grid_divs_x']*ap['grid_divs_x'])+1,3,ap['ldims']))
		else:
			fp = np.memmap(self.data_path, dtype='float32', mode='w+', shape=(dur_strides, (ap['grid_divs_x']*ap['grid_divs_x'])+1,3,ap['ldims']))
		
		# set some drawing constants
		vert_offset = int(frame_height*ap['hist_vert_offset_ratio'])
		grid_height_ratio = grid_height/255.

		#timing state vars
		self.frame_idx = offset_frames
		end_frame = offset_frames + dur_frames
		
		if display:
			cv.NamedWindow('Image', cv.CV_WINDOW_AUTOSIZE)
			cv.NamedWindow('Histogram', hist_width)
			cv.ResizeWindow('Histogram', int(hist_width*ap['hist_width_ratio']*1.0), int(hist_height*ap['hist_height_ratio']*1.25))
			cv.MoveWindow('Histogram', int(frame_width*ap['hist_horiz_offset_ratio']), vert_offset)
			
			# should probably assert that ldims == adims == bdims, but hey we trust people
			lcolors, acolors, bcolors= range(ap['ldims']), range(ap['adims']), range(ap['bdims'])
			for d in range (dims):
				gray_val = (d * 192. / dims) + 32
				lcolors[d] = cv.Scalar(255., gray_val, gray_val)
				acolors[d] = cv.Scalar(gray_val, 128., 128.)
				bcolors[d] = cv.Scalar(gray_val, gray_val, gray_val)
			six_points = self.build_bars(grid_width, grid_height, bin_w, third_bin_w, grid_x_divs, grid_y_divs, 16) # 16: number of bins
			self.capture.set(cv.CV_CAP_PROP_POS_FRAMES, offset_frames)

		while self.frame_idx < end_frame:
			
			if verbose:
				print('fr. idx: %6i || %.4f (/%i) [ %i | %i ]' % (self.frame_idx, ((self.frame_idx - offset_frames) / float(dur_frames)), dur_frames, offset_frames, end_frame))

			if (self.frame_idx%stride_frames) == 0:

				# frame grab
				ret, frame = self.capture.read()
				curr_stride_frame = self.frame_idx/stride_frames
				# reality check
				if frame is None: 
					print 'Frame error! Exiting...'
					break # no image captured... end the processing
				
				# access stage (full)
				if ap['mode'] == 'playback':
					lbins, abins, bbins = fp[curr_stride_frame][0][0], fp[curr_stride_frame][0][1], fp[curr_stride_frame][0][2]
					# if verbose: print (np.sum(lbins), np.sum(abins), np.sum(bbins))
				else:
					lbins, abins, bbins = self._analyze_image(frame, fp, curr_stride_frame, lab, lab_min, lab_max, l_star, a_star, b_star, mask, l_histo, a_histo, b_histo, 0, 0, 0, 1., thresh=ap['threshold'])

				# display stage (full)
				if display:
					histimg[:] = 0
					for d in range(dims):
						# for all the bins, get the value, and scale to the size of the grid
						lval, aval, bval = int(lbins[d]*255.), int(abins[d]*255.), int(bbins[d]*255.)
						#draw the rectangle in the wanted color
						self.make_rectangles(cv.fromarray(histimg), six_points, 6, 0, 0, d, [lval, aval, bval], grid_height_ratio, [lcolors, acolors, bcolors], voffset=hist_height)
				
				# access stage (gridded)
				for i in range(grid_x_divs):
					for j in range(grid_y_divs):
						if ap['mode'] == 'playback':
							lbins, abins, bbins = fp[(curr_stride_frame)][(j*grid_x_divs)+i+1][0], fp[curr_stride_frame][(j*grid_x_divs)+i+1][1], fp[curr_stride_frame][(j*grid_x_divs)+i+1][2]
						else:
							sub = frame[(i*grid_width):((i+1)*grid_width),(j*grid_height):((j+1)*grid_height)]
							lbins, abins, bbins = self._analyze_image(sub, fp, (self.frame_idx/stride_frames), grid_lab, lab_min, lab_max, grid_l_star, grid_a_star, grid_b_star, grid_mask, l_histo, a_histo, b_histo, i, j, 1, 1., thresh=ap['threshold'])

						# display stage (gridded)
						if display:
							for  d in range (dims):
								# for all the bins, get the value, and scale to the size of the grid
								lval, aval, bval = int(lbins[d]*255.), int(abins[d]*255.), int(bbins[d]*255.)
								#draw the rectangle in the wanted color
								self.make_rectangles(cv.fromarray(histimg), six_points, 6, i, j, d, [lval, aval, bval], grid_height_ratio, [lcolors, acolors, bcolors], voffset=0)
				
				#### SHOW
				if ap['display']:
					cv.ShowImage('Image', cv.fromarray(frame))
					cv.ShowImage('Histogram', cv.fromarray(histimg))
				fp.flush()
				self.frame_idx += 1
				
			elif (self.frame_idx%stride_frames) == 1:
				self.capture.set(cv.CV_CAP_PROP_POS_FRAMES, int((self.frame_idx / stride_frames) + 1) * stride_frames)
				self.frame_idx += stride_hop # stride_hop = 5 = stride - 1
# 				self.frame_idx = self.capture.get(cv.CV_CAP_PROP_POS_FRAMES) # better???
			
			# no need to waitkey if we are not displaying:
			if display:
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
		
		if not HAVE_CV:
			return
		
		if (self.movie_path is None) or (self.data_path is None):
			print "Must supply both a movie and a data path!"
			return
		
		# ap = self._check_cflab_params(kwargs)
		ap = self.analysis_params
		verbose = ap['verbose']
		
 		self.capture = cv2.VideoCapture(self.movie_path)
		
		fps = ap['fps']
		grid_x_divs = ap['grid_divs_x']
		grid_y_divs = ap['grid_divs_y']
		frame_width = int(self.capture.get(cv.CV_CAP_PROP_FRAME_WIDTH))
		frame_height = int(self.capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
		frame_size = (frame_width, frame_height)
		hist_width = int(frame_width * ap['hist_width_ratio'])
		hist_height = int(frame_height * ap['hist_width_ratio'])
		hist_size = (hist_width, hist_height)
		grid_width = int(hist_width/grid_x_divs)
		grid_height = int(hist_height/grid_y_divs)
		grid_size = (grid_width, grid_height)
		
		if verbose:
			print ap['lrange'][0], ' | ', ap['arange'][0], ' | ', ap['brange'][0], ' | ', ap['lrange'][1], ' | ', ap['arange'][1], ' | ', ap['brange'][1], '\n', fps, ' | ', hist_size, ' | ', grid_size
				
		dims = ap['ldims']
		bin_w = int((hist_width * ap['hist_width_ratio']) / (ap['ldims'] * grid_x_divs))
		third_bin_w = int(bin_w/3)
		
		# histimg = cv.CreateImage ((hist_width, int(hist_height*1.25)), cv.IPL_DEPTH_8U, 3)
		histimg = np.zeros((int(hist_height*1.25), int(hist_width), 3), np.uint8)
		
		# last but not least, get total_frame_count and set up the memmapped file
		# dur_total_secs = int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT) / fps)
		dur_total_secs = ap['duration']
		stride_frames = ap['stride']
		stride_hop = stride_frames - 1
#		if ap['duration'] < 0:
# 			dur_secs = dur_total_secs
# 		else:
# 			dur_secs = ap['duration']
		
		offset_secs = min(max(ap['offset'], 0), dur_total_secs)
		dur_secs = min(max(dur_total_secs, 0), (dur_total_secs - offset_secs))
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
			print "FPS: ", fps
			print "stride_frames: ", stride_frames
		
		# set up memmap
		# mode should always be playback and dislay should always be true!!!
		if ap['mode'] == 'playback' and ap['display'] == True:
			fp = np.memmap(self.data_path, dtype='float32', mode='r+', shape=((offset_strides + dur_strides),17,3,16))
		
			# set some drawing constants
			vert_offset = int(frame_height*ap['hist_vert_offset_ratio'])
			grid_height_ratio = grid_height/255.
			
			cv.NamedWindow('Image', cv.CV_WINDOW_AUTOSIZE)
			cv.NamedWindow('Histogram')
			cv.ResizeWindow('Histogram', int(hist_width*ap['hist_width_ratio']*1.0), int(hist_height*ap['hist_height_ratio']*1.25))
			cv.MoveWindow('Histogram', int(frame_width*ap['hist_horiz_offset_ratio']), vert_offset)
			
			lcolors, acolors, bcolors= range(16), range(16), range(16)
			for d in range (dims):
				gray_val = (d * 192. / dims) + 32
				lcolors[d] = cv.Scalar(255., gray_val, gray_val)
				acolors[d] = cv.Scalar(gray_val, 128., 128.)
				bcolors[d] = cv.Scalar(gray_val, gray_val, gray_val)
			six_points = self.build_bars(grid_width, grid_height, bin_w, third_bin_w, grid_x_divs, grid_y_divs, 16) # 16: number of bins
			self.capture.set(cv.CV_CAP_PROP_POS_FRAMES, offset_frames)
		
			self.frame_idx = offset_frames
			playing_flag = True
			p_state = 7

			while playing_flag:			
				# div. by 6 everywhere (except in log prints) to count by strides
				if (self.frame_idx%stride_frames) == 0:
					ret, frame = self.capture.read()
					curr_stride_frame = self.frame_idx/stride_frames
					if frame is None: 
						print 'Frame error! Exiting...'
						break # no image captured... end the processing
		
					trio = fp[curr_stride_frame]
					lbins, abins, bbins = trio[0][0], trio[0][1], trio[0][2]

					# display stage (full)
					histimg[:] = 0 # clear/zero
					for d in range(dims):
						# for all the bins, get the value, and scale to the size of the grid
						lval, aval, bval = int(lbins[d]*255.), int(abins[d]*255.), int(bbins[d]*255.)
						#draw the rectangle in the wanted color
						self.make_rectangles(cv.fromarray(histimg), six_points, 6, 0, 0, d, [lval, aval, bval], grid_height_ratio, [lcolors, acolors, bcolors], voffset=hist_height)

					# access stage (gridded)
					for i in range(grid_x_divs):
						for j in range(grid_y_divs):
							lbins, abins, bbins = trio[(j*4)+i+1][0], trio[(j*4)+i+1][1], trio[(j*4)+i+1][2]
							# if verbose: print (np.sum(lbins), np.sum(abins), np.sum(bbins))
							# display stage (grid)
							for  d in range (dims):
								# for all the bins, get the value, and scale to the size of the grid
								lval, aval, bval = int(lbins[d]*255.), int(abins[d]*255.), int(bbins[d]*255.)
								#draw the rectangle in the wanted color
								self.make_rectangles(cv.fromarray(histimg), six_points, 6, i, j, d, [lval, aval, bval], grid_height_ratio, [lcolors, acolors, bcolors]) #, voffset=0
					
					#### SHOW
					cv.ShowImage('Image', cv.fromarray(frame))
					cv.ShowImage('Histogram', cv.fromarray(e))
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
				cv.DestroyWindow('Histogram')	

	def _analyze_image(self, img, mfp, fpindex, lab, lab_min, lab_max, l_star, a_star, b_star, mask, l_histo, a_histo, b_histo, i, j, grid_flag, grid_height=1, thresh=0.):
		"""
		Image analysis kernel function that is called to analyze each frame image. Look at the main process function to get an idea of how you would call this to return analysis data for a single image. Todo: wrap such a call into a simple one-off function call.
		"""
		# ap = self._check_cflab_params(None)
		ap = self.analysis_params
		grid_divs_x = ap['grid_divs_x']
		lab = cv2.cvtColor(img, cv.CV_BGR2Lab)
		
		item = cv2.calcHist([lab],[0],None,[16],[0,255])
		cv2.normalize(np.where(item>thresh,item,0),l_star,alpha=1.0,norm_type=cv2.NORM_L2)
		item = cv2.calcHist([lab],[1],None,[16],[0,255])
		cv2.normalize(np.where(item>thresh,item,0),a_star,alpha=1.0,norm_type=cv2.NORM_L2)
		item = cv2.calcHist([lab],[2],None,[16],[0,255])
		cv2.normalize(np.where(item>thresh,item,0),b_star,alpha=1.0,norm_type=cv2.NORM_L2)
				
		mfp[fpindex][ ((grid_divs_x*i)+j)+grid_flag ][0] = np.reshape(l_star[:], (16))
		mfp[fpindex][ ((grid_divs_x*i)+j)+grid_flag ][1] = np.reshape(a_star[:], (16))
		mfp[fpindex][ ((grid_divs_x*i)+j)+grid_flag ][2] = np.reshape(b_star[:], (16))
		
		return l_star[:], a_star[:], b_star[:]

	
	# GUI helper functions
	def build_bars(self, gw, gh, bw, tbw, xdivs, ydivs, numbins):
		"""
		Display helper function. Build list of points for the trios of histogram bars.
		"""
		# ap = self._check_cflab_params(None)
		ap = self.analysis_params
		six_points = np.ndarray((16,16,6,2), dtype=int)
		for i in range(xdivs):
			for j in range(ydivs):
				for h in range(numbins):
					foo = six_points[h][(i*xdivs)+j]
					foo[0] = [(j*gw)+(h * bw), (i+1)*gh]
					foo[1] = [(j*gw)+((h+1) * bw)-(2*tbw), ((i+1)*gh)]
					foo[2] = [(j*gw)+(h * bw)+(tbw), (i+1)*gh]
					foo[3] = [(j*gw)+((h+1) * bw)-(tbw), ((i+1)*gh)]
					foo[4] = [(j*gw)+(h * bw)+(2*tbw), (i+1)*gh]
					foo[5] = [(j*gw)+((h+1) * bw), ((i+1)*gh)]
		return six_points
	
	def make_rectangles(self, h_img, pts, num_pts, i, j, h, vals, grid_height_ratio, colors, hoffset=0, voffset=0):
		"""
		Display helper function. Make a bank of three bars for the histogram. (16 in total, via 16 calls of this function.)
		"""
		# ap = self._check_cflab_params(None)
		ap = self.analysis_params
		grid_divs_x = ap['grid_divs_x']
		grid_divs_y = ap['grid_divs_y']
		# the 0.95 scalar is there so that there are gaps between the histograms in the grid view!
		for n in range(int(num_pts/2)):
			cv.Rectangle (h_img,
							((pts[h][(i*grid_divs_x)+j][2*n][0] + hoffset),   (pts[h][(i*grid_divs_x)+j][2*n][1] + int(voffset))),
							((pts[h][(i*grid_divs_x)+j][2*n+1][0] + hoffset), (pts[h][(i*grid_divs_x)+j][2*n+1][1] + int(voffset) - int(vals[n]*grid_height_ratio*0.95))), 
							colors[n][h], -1, 8, 0)
