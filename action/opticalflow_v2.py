# opticalflow.py - Motion vectors from video
# Bregman:ACTION - Cinematic information retrieval toolkit

"""
Part of Bregman:ACTION - Cinematic information retrieval toolkit

Overview
========

Use the OpticalFlow class to generate analysis data of general motion on screen. A histogram of angular data is gathered. There are 8 bins for screen location and 8 bins for vectors' angles. 

In order to reduce the amount of data involved (and the processing time involved), a stride parameter is used. This number is the number of movie frames to account for in one analysis frame. The default is 6. As of version 1.0, there is no averaging or interpolation, the "skipped" frames are simply dropped.

Creation
========

Instantiate the OpticalFlow class, optionally with additional keyword arguments:

::

	myOpticalFlow = OpticalFlow(movie-name-string, param1=value1, param2=value2, ...)

The global default opticalflow-extractor parameters are defined in a parameter dictionary: 

::

	default_opticalflow_params = {
		'action_dir' : '~/Movies/action/',	# set a default location for movie and data files
		'movie_extension' : '.mov',
		'data_extension' : '.opticalflow',
		'mode' : 'analyze',					# 'playback' or 'analyze'
		'fps' : 24,							# fps: frames per second
		'offset' : 0,						# time offset (in seconds) into film
		'duration' : -1,					# duration (in seconds) of segment, -1 maps to full duration of media
		'stride' : 6,						# stride is set to 1
		'verbose' : True,					# useful for debugging
		'display' : True,					# Launch display screen
		'winSize' : (15, 15),				# @ full resolution, must be odd & square
		'maxLevel' : 2,						# how many Pyramids (downsampling stages)
		'criteria' : (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
		'maxCorners' : 100,					# parameters for the edge detector and optical flow tracker...
		'qualityLevel' : 0.3,
		'minDistance' : 7,
		'blockSize' : 7,
		'trackLength' : 3,
		'trackDepth' : 2
	}


Upon creation of an OpticalFlow object, parameter keywords can be passed explicitly as formal arguments or as a keyword argument parameter dict:, e.g.:

::

   myOptFlow = OpticalFlow(fileName, , verbose=True )
   myOptFlow = OpticalFlow(fileName, **{'':, 'verbose':True} )

Use
===

The functions of the OpticalFlow class define the various use cases or patterns.

Analyze a full film:

::

	optflw = OpticalFlow('Psycho')
	optflw.analyze_movie()

This also works, so you can define your own filing system:
::

	optflw = OpticalFlow('Psycho', action_dir='/Users/me/data/action')
	optflw.analyze_movie()

To screen (the video only) your film as it is analyzed:
::

	optflw = OpticalFlow('Psycho')
	optflw.analyze_movie_with_display()

To play back your analysis later:
::

	optflw = OpticalFlow('Psycho')
	optflw.playback_movie()

To directly access your analysis data as a memory-mapped array:
::

	optflw = OpticalFlow('Psycho')
	segment_in_seconds = Segment(60, 600) # requesting nine-minute segment from 1'00" to 10'00"
	optflw.opticalflow_for_segment(segment_in_seconds)

A Note on Paths
===============

This class is set up for the following directory structure. You might want to modify this to suit your needs.

/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.mov
/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.wav
/Users/me/Movies/action/NAME_OF_FILM/NAME_OF_FILM.DATA_FILE_EXTENSION
..etc...

Advanced Use
============

There is a default stride time of 6 frames (or 24 / 6 = 4 analyzed frames per second), unless overridden. The following would result in 24 / 4 = 6 analyzed frames per second:
::

	optflw = OpticalFlow('Psycho', stride=4)
	
*Very important*: Since optical flow is based on comparisons between consecutive frames (in our case we are limiting ourselves to first-order differences) we are comparing adjoining frames in the movie, even though we then 'stride' forward to the next analysis frame. For one second at 24 fps with a stride value of 6, we examine frames 0, 1, 6, 7, 12, 13, 18, and 19, giving us 4 frames of analysis data. Note that choosing 'stride' values that are not factors of 24 will result in analysis rates that do not fit neatly into one second periods.

"""

__version__ = '1.0'
__author__ = 'Thomas Stoll'
__copyright__ = "Copyright (C) 2012  Michael Casey, Thomas Stoll, Dartmouth College, All Rights Reserved"
__license__ = "gpl 2.0 or higher"
__email__ = 'thomas.m.stoll@dartmouth.edu'


import sys, time, os, math, glob
# import the necessary things for OpenCV
import cv, cv2
import numpy as np
from numpy import *
import bregman.segment as bseg

QPI = math.pi / 4.0
COLS = 64

class OpticalFlow:
	"""
	Optical flow analysis of consecutive frames (see note above on stride parameter) using a Lucas-Kanade optical flow algorithm operating tracked features (corner detector) of monochrome image data.
	
	It is based on the OpenCV Python2 example ld_track.py.
	
	::
	
		action_dir = '~/Movies/action' by default; pass a different directory if necessary.
	
	If you want to run in verbose mode (to see some debug information on calculated frame offsets, analysis ranges, etc.) pass the verbose=True flag here.
	"""
	def __init__(self, filename='Vertigo', arg=None, **analysis_params):
		self._initialize(filename, analysis_params)
	
	def _initialize(self, filename, analysis_params=None):
		"""
		"""

		self.analysis_params = self.default_opticalflow_params()
		self._check_opticalflow_params(analysis_params)

		ap = self.analysis_params
		
		if filename is None:
			print 'File name missing!'
			return
		else:
			self.movie_path = os.path.join(os.path.expanduser(ap['action_dir']), filename, (filename + ap['movie_extension']))
			self.data_path = os.path.join(os.path.expanduser(ap['action_dir']), filename, (filename + ap['data_extension']))
		
		# additional OpticalFlow-specific parameters and data structures...
		self.tracks = []
		self.frame_idx = 0
		
		self.lk_params = dict( winSize = ap['winSize'],
							maxLevel = ap['maxLevel'],
							criteria = ap['criteria'])
		
		self.feature_params = dict( maxCorners = ap['maxCorners'],
								qualityLevel = ap['qualityLevel'],
								minDistance = ap['minDistance'],
								blockSize = ap['blockSize'])
	
	
	def _check_opticalflow_params(self, analysis_params=None):
		"""
		Simple mechanism to read in default parameters while substituting custom parameters.
		"""
		self.analysis_params = analysis_params if analysis_params is not None else self.analysis_params
		ap = self.default_opticalflow_params()
		for k in ap.keys():
			self.analysis_params[k] = self.analysis_params.get(k, ap[k])
		return self.analysis_params

	@staticmethod
	def default_opticalflow_params():
		analysis_params = {
			'action_dir' : '~/Movies/action/',	# set a default location for movie and data files
			'movie_extension' : '.mov',
			'data_extension' : '.opticalflow',
			'mode' : 'analyze',					# 'playback' or 'analyze'
			'fps' : 24,							# fps: frames per second
			'offset' : 0,						# time offset (in seconds) into film
			'duration' : -1,					# duration (in seconds) of segment, -1 maps to full duration of media
			'stride' : 6,						# stride is set to 1
			'verbose' : True,					# useful for debugging
			'display' : True,					# Launch display screen
			'winSize' : (15, 15),				# @ full resolution, must be odd & square
			'maxLevel' : 2,						# how many Pyramids (downsampling stages)
			'criteria' : (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
			'maxCorners' : 100,					# for edge detector
			'qualityLevel' : 0.3,
			'minDistance' : 7,
			'blockSize' : 7,
			'trackLength' : 3,
			'trackDepth' : 2
			
		}
		return analysis_params
		
	def opticalflow_for_segment(self, segment=bseg.Segment(0, 60)):
		"""
		This is the interface for grabbing analysis data for segments of the whole film. Uses Segment objects from Bregman/ACTION!
		Takes a file name or complete path of a data file and a Segment object that describes the desired timespan.
		Returns a memory-mapped array corresponding to the reduced-dimension optical flow values: [NUMBER OF FRAMES, 64].
		
		::
		
			seg = Segment(360, 720) # which is the same as seg = Segment(360, duration=360)
			raw_opticalflow_data = oflow.opticalflow_for_segment('Psycho.opticalflow', seg)
			raw_oflow_data.shape
			>>> (1440, 64)
		
		PLEASE NOTE: Onset is relative to the onset of the analyzed file on disc. If you analyze starting at a 60 second offset, then your analysis file's 0 offset is actually the data starting 1 minute into the film!
		"""
		return self._opticalflow_for_segment_from_onset_with_duration(segment.time_span.start_time, segment.time_span.duration)
	
	def _opticalflow_for_segment_from_onset_with_duration(self, onset_time=0, duration=-1):
		"""
		This is the interface for grabbing analysis data based on onsets and durations, translating seconds into frames.
		Takes a file name or complete path of a data file, an onset time in seconds, and a duration in seconds.
		Returns a memory-mapped array corresponding to the reduced-dimension optical flow values: [NUMBER OF FRAMES, 64].
		
		::
			
			raw_opticalflow_data = opticalflow_for_segment(onset_time=360, duration=360)
		
		"""
		ap = self._check_opticalflow_params()

		onset_frame = int(onset_time * (ap['fps'] / ap['stride']))
		if duration < 0:
			dur_frames = self.determine_movie_length()
		else:
			dur_frames = int(duration * (ap['fps'] / ap['stride']))
		
		# r, c, full_data_path = self._glean_dimensions_from_filename(data_path)
		return np.memmap(self.data_path, dtype='int32', mode='c', offset=onset_frame, shape=(dur_frames,128))

	def determine_movie_length(self, **kwargs):
		"""
		Helper function for determining the length of a movie using OpenCV to capture from a file and query the length of the film.
		"""	
		ap = self._check_opticalflow_params(kwargs)
	
		capture = cv2.VideoCapture(self.movie_path)
		dur_total_seconds = int(capture.get(cv.CV_CAP_PROP_FRAME_COUNT)) / ap['fps']

		return dur_total_seconds
	
	def playback_movie_frames(self, offset=0, duration=-1):
		"""
		Play the movie alongside the analysis data visualization. Note that the stride parameter is meaningless. No resampling will be done. Equivalent to:
		
		::
		
			_process_movie(mode='playback', offset=0, duration=-1, stride=6, display=True)
		
		"""
# 		self._process_movie(movie_file, data_file, mode='playback', display=True, offset=offset, duration=duration)
		self._playback_movie(mode='playback', display=True, offset=offset, duration=duration)
	
	def analyze_opticalflow(self, offset=0, duration=-1, stride=6):
		"""
		Analyze the movie without displaying on screen. Equivalent to:
		
		::
		
			_process_movie(offset=0, duration=-1, stride=6, display=False)
		
		"""
		self._process_movie(mode='analyze', display=False, offset=offset, duration=duration)

	def analyze_opticalflow_with_display(self, offset=0, duration=-1, stride=6):
		"""
		Analyze the movie; display on screen. Equivalent to:
		
		::
		
			_process_movie(offset=0, duration=-1, stride=6, display=True)
		"""
		self._process_movie(mode='analyze', display=True, offset=offset, duration=duration)
	
	def _playback_movie(self, **kwargs):
		"""
		Play movie back; display on screen.
		Note: this function merely plays frames with no analysis data overlaid. It is meant for checking segmentation algorithm outputs and playing short clips of video from a film.
		TO DO: add optical-flow display.
		"""
		if self.movie_file is None:
			print 'Movie path or data path missing!'
			return
				
		ap = self._check_opticalflow_params(kwargs)
		verbose = ap['verbose']
				
		self.capture = cv2.VideoCapture(self.movie_path)

		fps = ap['fps']
						
		# last but not least, get total_frame_count and set up the memmapped file
		total_frame_count = int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT))	
		dur_total_secs = int(total_frame_count / fps)
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
			print 'FRAMES: ', total_frame_count
			print 'DUR TOTAL: ', dur_total_secs
			print "OFFSET (SECONDS): ", offset_secs
			print "OFFSET (STRIDES): ", offset_strides
			print "OFFSET (FRAMES): ", offset_frames
			print "DUR (SECONDS): ", dur_secs
			print 'DUR (STRIDES): ', dur_strides
			print 'DUR (FRAMES): ', dur_frames
			print "FPS: ", fps
			print "stride_frames: ", stride_frames
		self.capture.set(cv.CV_CAP_PROP_POS_FRAMES, offset_frames)
# 		self.fctrw = self.capture.get(cv.CV_CAP_PROP_FRAME_WIDTH) / 2.0
# 		self.fctrh = self.capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT) / 2.0
		self.frame_idx = offset_frames
		end_frame = offset_frames + dur_frames
		  		
  		while self.frame_idx <= end_frame:
			ret, frame = self.capture.read()
			if ap['display'] is True: vis = frame.copy()
			self.frame_idx += 1
			if ap['display'] is True: cv2.imshow('lk_track', vis)
			
			if ap['display'] is True: 
				ch = 0xFF & cv2.waitKey(1)
				if ch == 27:
					break
		
		if ap['display'] is True: cv2.destroyAllWindows()	


	def _process_movie(self, **kwargs):
		"""
		Main processing function. This is where the magic happens when we're making optical-flow analyses.
		Will exit if neither a movie path nor a data path are supplied. This function is not intended to be called directly. Normally, call one of the three more descriptive functions instead, and it will call this function.
		
		"""
				
		ap = self._check_opticalflow_params(kwargs)
		verbose = ap['verbose']
				
		self.capture = cv2.VideoCapture(self.movie_path)
		
		fps = ap['fps']
		frame_width = int(self.capture.get(cv.CV_CAP_PROP_FRAME_WIDTH))
		frame_height = int(self.capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
		frame_size = (frame_width, frame_height)
		grid_width = int(frame_width/4)
		grid_height = int(frame_height/4)
		grid_size = (grid_width, grid_height)

						
		# last but not least, get total_frame_count and set up the memmapped file
		total_frame_count = int(self.capture.get(cv.CV_CAP_PROP_FRAME_COUNT))	
		dur_total_secs = int(total_frame_count / fps)
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
			print 'FRAMES: ', total_frame_count
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
		print 'ANALYZE!'
		fp = np.memmap(self.data_path, dtype='int32', mode='w+', shape=(dur_strides,(16*8)))
		print 'dur. strides: ', dur_strides
		
		self.capture.set(cv.CV_CAP_PROP_POS_FRAMES, offset_frames)
# 		self.fctrw = self.capture.get(cv.CV_CAP_PROP_FRAME_WIDTH) / 2.0
# 		self.fctrh = self.capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT) / 2.0
# 		if verbose: print 'center pt.: ', self.fctrw, ' | ', self.fctrh
		self.frame_idx = offset_frames
		end_frame = offset_frames + dur_frames
		tdepth = ap['trackDepth']
		
# 		if ap['display']:
# 			cv.NamedWindow('Image', cv.CV_WINDOW_AUTOSIZE)
		
		while self.frame_idx < end_frame:
		
			if verbose: print 'fr. idx: ', self.frame_idx / float(end_frame), ' (/ ', end_frame, ')'
			
			ret, frame = self.capture.read()
			frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			if ap['display'] is True: vis = frame.copy()
			
			if len(self.tracks) > 0 and self.frame_idx % 3 == 0:
				img0, img1 = self.prev_gray, frame_gray
				p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
				p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **self.lk_params)
				p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **self.lk_params)

				d = abs(p0-p0r).reshape(-1, 2).max(-1)
				good = d < 1
				new_tracks = []
				for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
					if not good_flag:
						continue
					tr.append((x, y))
					if len(tr) > ap['trackLength']:
						del tr[0]
					new_tracks.append(tr)
					if ap['display'] is True: cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
				self.tracks = new_tracks
				
				if self.frame_idx % ap['stride'] == 0:
					
					tracks_now = [np.int32(tr) for tr in self.tracks]

					if ap['display'] is True: cv2.polylines(vis, tracks_now, False, (0, 255, 0))

					try:
						seq = tracks_now[0]
						track_vectors = np.append( tracks_now[0][ min(len(seq)-1, tdepth) ], seq[0])

						for n, tr in enumerate(tracks_now[1:]):
							track_vectors = np.append(track_vectors, np.append(tr[ min(len(tr)-1, tdepth) ], (tr[0])))

						# track_vectors is variable-length, up to max-number-of-corners
						track_vectors = np.reshape(np.array(track_vectors, dtype='int32'), (-1,4))
						
						xdelta = track_vectors[:,2] - track_vectors[:,0]
						ydelta = track_vectors[:,3] - track_vectors[:,1]
						thetas = np.arctan2(ydelta, xdelta)
 						mags = np.sqrt(np.add(np.power(xdelta, 2.0), np.power(ydelta, 2.0)))
# 						xcdelta = np.subtract(track_vectors[:,2], self.fctrw)
# 						ycdelta = np.subtract(track_vectors[:,3], self.fctrh)
# 						cthetas = np.arctan2(ycdelta, xcdelta)
# 						cmags = np.sqrt(np.add(np.power(xcdelta, 2.0), np.power(ycdelta, 2.0)))
						
						xbin = np.floor(track_vectors[:,0] / grid_width)
						ybin = np.floor(track_vectors[:,1] / grid_height)
						
# 						print [np.min(xbin), np.max(xbin), np.min(ybin), np.max(ybin)]
						
						# filter out zero-length vectors!
						nz_cond = np.where(mags > 0.0)
						theta_bins = np.floor_divide(np.add(thetas, math.pi), QPI)
# 						ctheta_bins = np.floor_divide(np.add(cthetas, math.pi), QPI)
												
						combo_bins = ((np.add(np.multiply(ybin, 4), xbin) * 8) + theta_bins)[nz_cond]

						if combo_bins.shape[0] > 0:

#	 						print "-----------------------------------------------"
# 							print combo_bins.shape
# 							print np.max(combo_bins)

							bins_histo, bin_edges = np.histogram(combo_bins, (16*8), (0., float((16*8) - 1)))
						
							fd6 = (self.frame_idx/6) - offset_strides
							fp[fd6] = bins_histo
						else:
						
							fd6 = (self.frame_idx/6) - offset_strides
	 						if verbose: print 'Zero! frame: ', fd6
							fp[fd6] = np.zeros(128, dtype='int32') # 16*8=128
						
					except IndexError:
						
						fd6 = (self.frame_idx/6) - offset_strides
 						if verbose: print 'Index Error! frame: ', fd6
						fp[fd6] = np.zeros(128, dtype='int32') # 16*8=128
							
			if self.frame_idx % (ap['stride']*2) == 0:
				
				mask = np.zeros_like(frame_gray)
				mask[:] = 255
				for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
					if ap['display'] is True: cv2.circle(mask, (x, y), 5, 0, -1)
				p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **self.feature_params)
				if p is not None:
					for x, y in np.float32(p).reshape(-1, 2):
						self.tracks.append([(x, y)])
			
			self.frame_idx += 1
			self.prev_gray = frame_gray
			if ap['display'] is True: cv2.imshow('lk_track', vis)
			
			if ap['display'] is True: 
				ch = 0xFF & cv2.waitKey(1)
				if ch == 27:
					break
		
		if ap['display'] is True: cv2.destroyAllWindows()
