# actiondata.py - data processing and viewing
# Bregman:ACTION - Cinematic information retrieval toolkit

__version__ = '1.0'
__author__ = 'Thomas Stoll'
__copyright__ = "Copyright (C) 2012  Michael Casey, Thomas Stoll, Dartmouth College, All Rights Reserved"
__license__ = "gpl 2.0 or higher"
__email__ = 'thomas.m.stoll@dartmouth.edu'

import sys, time, os, glob, pickle, pdb
import numpy as np
from bregman.suite import *
import bregman.segment as bseg
try:
	from sklearn.decomposition import *
	import sklearn.decomposition as decomp
	from sklearn.cluster import Ward
	have_sklearn = True
except ImportError:
	print 'WARNING: sklearn not found. Ward (hierarchical) clustering disabled.'
	have_sklearn = False
from scipy import sparse
from scipy import ndimage
import mpl_toolkits.mplot3d.axes3d as p3
import pylab as P
import matplotlib.pyplot as plt

import color_features_lab
import opticalflow

DEFAULT_IMAGESC_KWARGS={'origin':'upper', 'cmap':P.cm.hot, 'aspect':'auto', 'interpolation':'nearest'}

class ActionData:
	"""
	ActionData is a collection of processing algorithms for analyzing data generated in ACTION. It is lightly documented and subject to change at any time, but still useful.
	"""
	def __init__(self, arg=None, **params):
		self._initialize(params)
	
	def _initialize(self, params):
		self.params = self.default_params()
		self._check_params(params)
	
	def _check_params(self, params=None):
		"""
		Simple mechanism to read in default parameters while substituting custom parameters.
		"""
		self.params = params if params is not None else self.params
		ap = self.default_params()
		for k in ap.keys():
			self.params[k] = self.params.get(k, ap[k])
		return self.params

	@staticmethod
	def default_params():
		params = {
			'raw_type' : 'full_screen_histogram'
		}
		return params
	
	def n_order_difference(self, raw_data, order=1, absflag=False):
		"""
		Assumes that time/ordering is along the 0th axis (ML representation).
		"""
		if absflag:		return np.abs(np.diff(raw_data, n=order, axis=0))
		else:			return np.diff(raw_data, n=order, axis=0)
	
	def calculate_self_similarity_matrix(self, raw_data, dist_flag='euc2'):
		"""
		Be careful!!! O(N^2)!
		"""
		if dist_flag is 'euc_normed':
			return distance.euc_normed(raw_data, raw_data)
		elif dist_flag is 'euc2':
			return distance.euc2(raw_data, raw_data)
	
	def calculate_pca_and_fit(self, raw_data, locut=0.1, print_var=False):
		"""
		"""
		try:
			pca = decomp.PCA()
		except NameError:
			print 'WARNING: sklearn decomposition function disabled.'
			return None
			
		pca.fit(raw_data)
		if print_var: print 'explained variance: ', pca.explained_variance_
		
		pca.n_components = np.where(pca.explained_variance_>locut)[0].shape[0]
		return pca.fit_transform(raw_data)

	def average_over_sliding_window(self, raw_data, width, hop, dtype='float32'):
		"""
		Average groups of consecutive frames.
		"""
		frames = raw_data.shape[0]
		channels = raw_data.shape[1]
		win_hops = range(0, frames, hop)
		chunked_data = np.empty_like(raw_data)
		chunked_data[:] = raw_data
		print "chunked: ", chunked_data.shape
		print "rds: ", raw_data.shape
		scipy.ndimage.uniform_filter(raw_data, (width, channels), output=chunked_data)
		
		print "WH: ", win_hops[-1]
		print "hop: ", hop
		chunked_data = chunked_data[win_hops,:]
		print chunked_data.shape		
		return np.reshape(chunked_data, (-1,channels))

	def revectorize_over_sliding_window(self, raw_data, width, hop, frames, dtype='float32'):
		"""
		Instead of averaging groups of consecutive frames, combine them into combined-vectors.
		"""
		win_hops = range(0, frames-width, hop)
		revectored_data = np.array([], dtype=dtype)

		for h in win_hops:
			revectored_data = np.append(revectored_data, raw_data[h:(h+width)])
		
		return np.reshape(revectored_data, (len(win_hops), raw_data.shape[1]*width))
	

	def gather_color_histogram_data(self, titles, movie_dir, grid='midband', cflag=False):
		"""
		full 		= full frame
		allgrid		= 4*4 grid
		midband		= middle rows
		plusband	= plus bands (excludes corners)
		centerquad	= center square

		limitations: can only use full film's data
		"""
		res = {}

		for title in titles:
			# set up an instance of the ColorFeaturesLAB class
			cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=movie_dir)
			# determine the film's length (in seconds)
			length = cfl.determine_movie_length()
			# create a segment spanning the full length of the film
			full_segment = bseg.Segment(0, duration=length)
			# obtain the data
			if grid == 'full':
				res[title] =  cfl.full_color_features_for_segment(full_segment)
			elif grid == 'allgrid':
				res[title] = cfl.gridded_color_features_for_segment(full_segment)
			elif grid == 'midband':
				res[title] = cfl.middle_band_color_features_for_segment(full_segment)
			elif grid == 'plusband':
				res[title] = cfl.plus_band_color_features_for_segment(full_segment)
			elif grid == 'centerquad':
				res[title] = cfl.center_quad_color_features_for_segment(full_segment)
			else:
				return None
			
			if (cflag>0): res[title] = cfl.convert_lab_to_l(res[title])
		return res
	
	def gather_opticalflow_histogram_data(self, titles, movie_dir, stride=6, cflag=False):
		"""
		"""
		res = {}

		for title in titles:
			# set up an instance of the ColorFeaturesLAB class
			oflow = opticalflow.OpticalFlow(title, action_dir=movie_dir)
			# determine the film's length (in seconds)
			length = oflow.determine_movie_length()
			# create a segment spanning the full length of the film
			full_segment = bseg.Segment(0, duration=length)
			# obtain the data
			res[title] =  oflow.opticalflow_for_segment(full_segment)[0:-1:stride,:]
		
		return res
	
	def cluster_hierarchically(self, raw_data, num_clusters, cmtrx=None):
		"""
		"""
		if cmtrx is None: cmtrx = self.generate_connectivity_matrix(raw_data.shape[0])
		try:
			ward_clusters = Ward(n_clusters=num_clusters, connectivity=cmtrx).fit(raw_data)
		except NameError:
			print 'WARNING: sklearn Ward clustering disabled.'
			return None
		return ward_clusters.labels_
	
	
	def generate_connectivity_matrix(self, size, loop_flag=False):
		"""
		Generate a square connectivity matrix with positive connections from t -> t-1 (identity) and t -> t+1; link end to beginning if loop_flag is True.
		Returns a sparse 
		"""
		eye = np.identity(size, dtype=np.int8)
		nn1 = np.add( np.roll(eye, 1, axis=0), np.roll(eye, 1, axis=1))
		
		if not loop_flag:
			nn1[-1,0] = 0
			nn1[0,-1] = 0
		#print nn1[:30,:30]
		return sparse.csr_matrix(nn1)
	
	def cluster_k_means(self, raw_data, k):
		"""
		Simple clustering algorithm
		args: raw data in ML orientation, K number of desired clusters
		returns: array with cluster index assignments, max assignment index
		"""
		km = KMeans(k)
		assigns = km.train(raw_data)
		max_assign = np.max(assigns)
		return assigns, max_assign
	
	def sample_n_frames(self, data, n=500, sort_flag=True):
		index_array = np.arange(data.shape[0])
		np.random.shuffle(index_array)
		if sort_flag is True:
			return data[np.sort(index_array[:n])], np.sort(index_array[:n])
		else:
			return data[index_array[:n]], np.sort(index_array[:n])

	# conversion + sorting routines
	def convert_assigned_clusters_to_2d_array(self, assigned):
		z = np.zeros((nc, len(assigned)))
		for k in range (nc):
			z[k, np.where(assigned==k)[0]]=k+1
		return z
	
	def convert_clustered_frames_to_segs(self, assigned, num_clusters=100):
		segs = []
		for n in range(num_clusters):
			seg = np.where(assigned==n)[0]
			first = seg[0]
			last = seg[-1]
			length = last - first + 1
			segs += [[first, length, n]]
		return segs

	def sort_segs_by_duration(self, segs):
		return sorted(segs, key=lambda seg: seg[1])
	
	def convert_clustered_frames_to_bsegs(self, assigned, num_clusters, feature_data, secsperframe=0.25):
		segs = []
		for n in range(num_clusters):
			seg = np.where(assigned==n)[0]
			first = seg[0]*secsperframe
			last = seg[-1]*secsperframe
			length = last - first + 1
			segs += [bseg.Segment(first, last, feature=np.mean(feature_data[first:last,:], axis=0))]
		return segs
	
	def calculate_sparse_svd(self, data, k=9):
		return sparse.linalg.svds(data, k)[0]
	
	def normalize_data(self, data):
		the_max = np.max(data)
		the_min = np.min(data)
		return ((data - the_min) / (the_max - the_min))
	
	def standardize_data(self, data):
		return (data - data.mean(axis=0)) / data.var(axis=0)
	
	def meanmask_data(self, data):
		D = np.ma.masked_invalid(data)
		return D.filled(D.mean())

	def zeromask_data(self, data):
		D = np.ma.masked_invalid(data)
		return D.filled(0.0)


class ActionView:
	"""
	ActionView is a collection of plotting and playback routines for viewing data generated in ACTION. It is lightly documented and subject to change at any time, but still useful.

	Example of use:
	
	::
		av = actionview.ActionView()
		av.plot_clusters(full_histogram_data, labeling, 'Clustering for my movie's histogram data')

	To create an ActionView instance, you only need to pass a variable if you are intending to use the segment-viewer. In that case, simply create an ActionView like so:
	
	::
		oflow = opticalflow.OpticalFlow('Psycho')
		av = actionview.ActionView(oflow)
		av.view_sequences(...)

	"""
	def __init__(self, module=None, mfile=None, dfile=None):
		self.ad = ActionData()
		self.mod = module
		self.movie_file = mfile
		self.data_file = dfile
	
	# utilities
	def check_kwargs(kwargs, default=DEFAULT_IMAGESC_KWARGS):
		for k in default: kwargs.setdefault(k,default[k])
		return kwargs
	
	def plot_hcluster_segments(self, hclusters, nc=100):
		"""
		2D graph; rows are segments, cols are time points.
		"""
		z = np.zeros((nc, len(hclusters)))
		for k in range (nc):
			z[k, np.where(hclusters==k)[0]]=k+1
		imagesc(z)
		return z

	
	def plot_segment_length_distribution(self, segs):
		"""
		Get an idea of how segment lengths are distributed. Use ad.convert_clustered_frames_to_segs to create segments from clusterings.
		"""
		segs_sorted_by_length = self.ad.sort_segs_by_duration(segs)
		print segs_sorted_by_length
		fig = plt.figure()
		plt.plot(np.arange(len(segs_sorted_by_length)-1), np.array(segs_sorted_by_length)[:-1,1])
		plt.show()
	
	
	def plot_clusters(self, X, labeling, ttl='1st three dimensions'):	
		"""
		Plot the first three dimensions of data clusters---works with any data; doesn't have to be clustered.
		"""
		fig = P.figure()
		ax = p3.Axes3D(fig)
		ax.view_init(7, -80)
		for l in np.unique(labeling):
			ax.plot3D(X[labeling == l, 0], X[labeling == l, 1], X[labeling == l, 2],'o', color=P.cm.jet(np.float(l) / np.max(labeling + 1)))
		P.title(ttl)
	
# 	def plot_similarity_matrix(self, X, ttl='Similarity/distance matrix'):

	DEFAULT_IMAGESC_KWARGS={'origin':'upper', 'cmap':P.cm.hot, 'aspect':'auto', 'interpolation':'nearest'}

	# utilities
	def check_kwargs(self, kwargs, default=DEFAULT_IMAGESC_KWARGS):
		for k in default: kwargs.setdefault(k,default[k])
		return kwargs

	def imagesc2(self, data, newfig=True, str='', ax=1, cbar=1, txt=False, txtprec=2, txtsz=18, txtnz=0, txtrev=0, labels=None, **kwargs):
		kwargs = self.check_kwargs(kwargs, DEFAULT_IMAGESC_KWARGS)
		if newfig:
			fig = P.figure()
		data = P.copy(data)
		if len(data.shape)<2:
			data = P.atleast_2d(data)
	#    if txtnz:
	#        kwargs['vmin'] = data[where(data>txtnz)].min()

		P.imshow(data,**kwargs)
		if cbar: P.colorbar()
		if labels is not None:
			P.xticks(np.arange(len(labels)), labels)
			P.yticks(np.arange(len(labels)), labels)
		if txt:
			thr = data.min() + (data.max()-data.min())/2.0
			for a in range(data.shape[0]):
				for b in range(data.shape[1]):
					if data[a,b]<thr:
						col = P.array([1,1,1])
					else:
						col = P.array([0,0,0])
					if txtrev:
						col = 1 - col
					d = data[a,b].round(txtprec)
					if txtprec==0:
						d = int(d)
					if not txtnz or txtnz and d>txtnz: # scale only non-zero values
						P.text(b-0.125,a+0.125,d,color=col,fontsize=txtsz)
		plt.title(str, fontsize=12)
		return fig

	def multi_imagesc2(self, data, shape, newfig=True, offset=0, rowlabel='', collabel=None, cbar=1, labels=None, **kwargs):
		kwargs = self.check_kwargs(kwargs, DEFAULT_IMAGESC_KWARGS)
		if newfig: mfig = P.figure()
		a,b = shape
		print len(data)
		print a
		print b
		for k, d in enumerate(data):
			print "K: ", k 
			P.subplot(a,b,k+1+offset)
			if type(data) is dict:
				self.imagesc2(data[k], newfig=False, str=key, ax=0, cbar=0, labels=labels, **kwargs)
			else:
				print data[k].shape
				self.imagesc2(data[k], newfig=False, ax=0, cbar=0, labels=labels, **kwargs)
			if not k%b: ylabel(rowlabel, fontsize=16)
			if k+offset < b:
				if collabel is not None:
					plt.title(collabel[k], fontsize=16)
				else:
					plt.title('%d'%(k+1), fontsize=16)
			if cbar:
				P.colorbar()        
		return mfig
		
	
	def view_sequences(self, segments, interpause=1):
		"""
		Simple playback of segments with a pause between each. Just supply start frames.
		"""
		if self.module is None: return None
		for seg in segments:
			print 'seg: ', seg
			offset_f = seg[0] / 4.0
			dur_f = seg[1] / 4.0
			self.mod.playback_movie_frames(offset_f, dur_f)
			time.sleep(interpause)

