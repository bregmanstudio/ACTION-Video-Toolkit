# segment.py - segmentation (extraction, viewing, segment container class)
# Bregman:ACTION - Cinematic information retrieval toolkit

__version__ = '1.0'
__author__ = 'Thomas Stoll'
__copyright__ = "Copyright (C) 2012  Michael Casey, Thomas Stoll, Dartmouth College, All Rights Reserved"
__license__ = "gpl 2.0 or higher"
__email__ = 'thomas.m.stoll@dartmouth.edu'

import numpy as np
import pylab as P
import scipy.signal
import actiondata


"""
Part of Bregman:ACTION - Cinematic information retrieval toolkit

Overview
========

Segment: container class for onset time, duration, and features averaged across the segment

TimeSpan: represents time in a segment: start, end, duration

Segmentation: represents a collection of time_spans and corresponding segments

VideoSegmentor: methods for performing segmentation, extracting and condensing features, plotting features. Also includes callback function for interactive segmentation.

"""

DEFAULT_IMAGESC_KWARGS={'origin':'upper', 'cmap':P.cm.hot, 'aspect':'auto', 'interpolation':'nearest'}

class TimeSpan(object):
    """
    
    """
    def __init__(self, start_time=None, end_time=None, duration=None):
        if start_time==None:
            raise ValueError("start_time must be provided")
        self.start_time=float(start_time)
        if end_time==None and start_time==None:
            raise ValueError("One of end_time or duration must be supplied")                
        self.duration = float(end_time) - self.start_time if duration is None else float(duration)
        self.end_time = self.start_time + float(duration) if end_time is None else float(end_time)
        if abs(self.end_time - self.start_time - self.duration)>np.finfo(np.float32).eps:
            raise ValueError("Inconistent end_time and duration provided")
    def __repr__(self):
        return "start_time=%.3f, end_time=%.3f, duration=%.3f"%(self.start_time, self.end_time, self.duration)

class Segment(object):
    def __init__(self, start_time=None, end_time=None, duration=None, features=None, label=0):
        self.time_span = TimeSpan(start_time, end_time, duration)
        self.features = [] if features is None else features
        self.label = str(label)
    def __repr__(self):
        return "(label=%s, %s, %s)"%(self.label, self.time_span.__repr__(), self.features.__repr__())

class Segmentation(object):
    """
    A segmentation consists of conjoined non-overlapping segments. 
    Each segment has a start_time, end_time, and implicit duration.
    
    A segmentation must be initialized with a title string.
    """
    def __init__(self, title_string):
        self.title_string = title_string
        self.time_spans = []

    def time_spans_to_frames(self, span_list):
        pass

    def frames_to_time_spans(self, frame_list):
        pass
    
    def __getitem__(self, index):
        return self.time_spans[index]

    def __setitem__(self, index, segment):
        if type(segment) is not Segment:
            raise ValueError("Segmentation requires a Segment")
        self.time_spans[index]=segment

    def __len__(self):
        return len(self.time_spans)

    def append(self, segment):
        if type(segment) is not Segment:
            raise ValueError("Segmentation requires a Segment")
        self.time_spans.append(segment)

    def __repr__(self):
        return self.time_spans.__repr__()
    
    def convert_features_to_array(self):
        """
        Creates an N * F numpy array where N is the number of segments and F is the number of features.
        arg - 
        """
        feature_len = len(self.time_spans[0].features)
        res = []
        for seg in self.time_spans:
            res += [seg.features]
        print feature_len
        print np.array(res).shape
        return np.reshape(np.array(res), (-1, feature_len))


class Segmentor(object):
    def __init__(self):
        pass
    def extract(self, media, num_clusers, feature, **kwargs):
        pass

class VideoSegmentor(Segmentor):
    def __init__(self):
        pass
    def cluster_segmentation(self, title_string, action_feature, num_clusters, cluster_algo='HC', **kwargs):
        """
        Given a media file (or signal) and num_clusters, return a segmentation.
        """
        self.ad = actiondata.ActionData()
        
        self.title_string = title_string
        self.action_feature = action_feature
        
        self.feature_params = kwargs
        
		#  action_dir is a kwarg
		# self.F will be an instance of action_feature, whatever that class may be
        self.F = self.action_feature(self.title_string, **kwargs)
        ap = self.F.analysis_params
        self.frame_rate = ap['fps'] / ap['stride']
        
        self.num_clusters = num_clusters
        # create empty segmentation
        self.segmentation = Segmentation(self.title_string)

        self.cluster_algo = cluster_algo
        if self.cluster_algo is 'HC':
            self.assigns = self.ad.cluster_hierarchically(self.F.X, self.num_clusters)
        elif self.cluster_algo is 'KM':
            self.assigns, self.num_clusters = self.ad.cluster_k_means(self.F.X, self.num_clusters)
        else:
            print 'Error, valid choices are HC or KM'
            return None
        
        self.diffs = np.where(np.r_[1,np.diff(self.assigns),1])[0]
        
        seg_labels=self.assigns[self.diffs[:-1]]
        for i in range(len(self.diffs)-1):
            self.segmentation.append(Segment(self.diffs[i]/float(self.frame_rate), self.diffs[i+1]/float(self.frame_rate),label=seg_labels[i]))
        counter = 0
        self.segmentation_map = []
        for i in range(len(self.assigns)-1):
        	self.segmentation_map += [counter]
        	if self.assigns[i] != self.assigns[i+1]: counter += 1
        return self.segmentation

    def extract_feature_means(self):
    	"""
    	"""
        if self.segmentation is None or self.F.X.shape[0] == 0:
            return None
        self.segmentation_data_type = 'mean'
        fr = self.frame_rate
        for seg in self.segmentation:
            seg.features = np.mean(self.F.X[int(seg.time_span.start_time*fr):(seg.time_span.end_time*fr)], axis=0)
        return self.segmentation
	
    def extract_feature_medians(self):
        """
        Same as means, but medians.
        """
        if self.segmentation is None or self.F.X.shape[0] == 0:
            return None
        self.segmentation_data_type = 'median'
        fr = self.frame_rate
        for seg in self.segmentation:
            seg.features = np.median(self.F.X[int(seg.time_span.start_time*fr):(seg.time_span.end_time*fr)], axis=0)
        return self.segmentation

    def extract_feature_means_and_stdevs(self):
        """
        Probably needs some post-processing tweaking?
        """
        if self.segmentation is None or self.F.X.shape[0] == 0:
            return None
        self.segmentation_data_type = 'meanstdev'
        fr = self.frame_rate
        for seg in self.segmentation:
            seg.features = [np.mean(self.F.X[int(seg.time_span.start_time*fr):(seg.time_span.end_time*fr)], axis=0),
            	np.std(self.F.X[int(seg.time_span.start_time*fr):(seg.time_span.end_time*fr)], axis=0)]
        return self.segmentation

    def segment_condensed_features_with_granularity(self, gran=15):
        # first, some preliminaries
        self.extract_feature_means()
        # flat, no time structure:
        segdata = self.segmentation.convert_features_to_array()
        self.ssm = self.ad.normalize_data(
            self.ad.zeromask_data(
                self.ad.calculate_self_similarity_matrix(segdata, segdata)))
        # first, the segmentation data
        final_resegmented = np.zeros(self.F.X.shape[1], dtype=np.float32)
        counter = 0
        for i in range(0, self.F.determine_movie_length(), gran):
            # always concat
            try:
                print counter
                final_resegmented = np.append(np.atleast_2d(final_resegmented), np.atleast_2d(self.segmentation[counter].features), axis=0)
                if self.segmentation[counter].time_span.start_time < i:
		    	    ##
                    counter += 1
            except IndexError:
                counter -= 1
                print 'backing up: ', counter
                final_resegmented = np.append(np.atleast_2d(self.segmentation), np.atleast_2d(self.segmentation[counter].features), axis=0)
        ssm_resegmented = self.ad.calculate_self_similarity_matrix(final_resegmented)
        return final_resegmented, ssm_resegmented

    def segmentation_plot(self, alpha=0.1, linewidth=1, granularity=30, with_playback=False, ):
        """
        Display features and segmentation using different visualizations, either based on KMeans clustering or hierarchical clustering; or roll your own!
        """
        if self.cluster_algo is 'KM':
            P.figure()
            P.subplot(311)
            feature_plot(self.F.X.T, nofig=1)
            P.subplot(312)
            self.cluster_plot(nofig=1)
            P.subplot(313)
            self.linkage_plot(nofig=1, alpha=alpha, linewidth=linewidth)
        elif self.cluster_algo is 'HC':
            self.segmented_condensed, self.ssm_condensed = self.segment_condensed_features_with_granularity(granularity)
            fig = P.figure()
            P.subplot(411)
            #feature_plot(self.F.X.T, nofig=1)
            feature_plot(self.ssm_condensed.T, nofig=1)
            P.subplot(412)
            feature_plot(self.segmented_condensed.T, nofig=1)
            P.subplot(413)
            self.cluster_plot(nofig=1)
            P.subplot(414)
            self.sim_linkage_plot(self.ssm, alpha=alpha, linewidth=linewidth, nofig=1)
            if with_playback is True:
                cid = fig.canvas.mpl_connect('button_press_event', self.onclick)

    def cluster_plot(self, nofig=False):
        """
        Display segmentation clusters as indicator matrix.
        Can be used to plot both contiguous and non-contiguous segmentations.
        """
        if not nofig:
            P.figure()
        z = np.zeros((self.num_clusters, len(self.assigns)))
        for k in range(self.num_clusters): z[k, np.where(self.assigns==k)[0]]=k+1
        feature_plot(z,nofig=1)
        #P.title('Segmentation')

    def linkage_plot(self, alpha=0.1, linewidth=1, nofig=False):
        """
        Display segmentation regions and linkage using arcs
        """
        if not nofig:
            P.figure()
        ax = P.gca()
        cols=['r','g','b','c','m','y','k']
        for k in range(self.num_clusters):
            kpos = np.where(self.assigns[self.diffs[:-1]]==k)
            for j in self.diffs[kpos]:
                for l in self.diffs[kpos]:
                    arc = P.Circle(((l+j)/2.0,0.),radius=abs(l-j)/2.0, color=cols[k%len(cols)],fill=0, linewidth=linewidth, alpha=alpha)
                    ax.add_patch(arc)
        P.show()
        P.axis([0,self.F.X.shape[1],0,self.F.X.shape[1]/2.])
        #P.colorbar()
        P.xlabel('Frames')

    def sim_linkage_plot(self, sim_matrix, link_threshold=0.25, alpha=0.1, linewidth=1, nofig=False):
        """
        Display segmentation regions and linkage using arcs
        """
        if not nofig:
            P.figure()
        ax = P.gca()
        cols=['r','g','b','c','m','y','k']
        for k in range(self.num_clusters):
            for l in range(1+k,self.num_clusters):
                clr = sim_matrix[k,l]
                if clr < link_threshold:
                    kpos = self.diffs[k]
                    lpos = self.diffs[l]
                    arc = P.Circle(((kpos+lpos)/2.0,0.),radius=abs(kpos-lpos)/2.0, color=str(clr), fill=0, linewidth=linewidth, alpha=alpha)
                    ax.add_patch(arc)
        P.show()
        P.axis([0,self.F.X.shape[0],0,self.F.X.shape[0]/2.])
        #P.colorbar()
        P.xlabel('Frames (1/4 second)')

    def onclick(self, event):
        print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata)
        
        segid = self.segmentation_map[int(event.xdata)]
        
        onset_secs = self.segmentation[segid].time_span.start_time
        end_secs = self.segmentation[segid].time_span.end_time
        dur_secs = self.segmentation[segid].time_span.duration
        
        print 'playing segment: ', (segid, onset_secs, end_secs, dur_secs)
        
        self.F.playback_movie(onset_secs, dur_secs)


# class SegmentationFeatureExtractor(object):
#     def __init__(self):
#         """
#         Class to perform extraction operation on Segmentation objects
#         """
#         pass
#     def extract(self, segmentation, feature, **kwargs):
#         """
#         Given a segmentation and a feature class (plus **kwargs), extract feature for each segment in the segmentation.
#         """
#         if type(segmentation.media) is not str:
#             raise TypeError("Only file segmentation extraction is currently supported.")
#         x,SR,fmt = sound.wavread(segmentation.media, last=1)
#         for seg in segmentation: 
#             x, xsr, fmt = sound.wavread(segmentation.media, 
#                                        first=int(seg.time_span.start_time*SR), last=int(seg.time_span.duration*SR))
#             f = feature(x, **kwargs)
#             seg.features.append(f)
# 
# class ChapterSegmentor(Segmentor):
#     pass
# 
# class SceneBoundarySegmentor(Segmentor):
#     pass
# 
# class ShotBoundarySegmentor(Segmentor):
#     pass
# 
# class MusicStructureSegmentor(Segmentor):
#     pass
# 
# class AudioOnsetSegmentor(Segmentor):
#     pass
# 


def _normalize(x):
    """
    ::

        static method to copy array x to new array with min 0.0 and max 1.0
    """
    y=x.copy()
    y=y-P.np.min(y)
    y=y/P.np.max(y)
    return y

def feature_plot(M, normalize=False, dbscale=False, norm=False, title_string=None, interp='nearest', bels=False, aspect='auto', nofig=False):
    """
    ::

        static method for plotting a matrix as a time-frequency distribution (audio features)
    """
    X = feature_scale(M, normalize, dbscale, norm, bels)
    if not nofig: P.figure()
    clip=-100.
    if dbscale or bels:
        if bels: clip/=10.
        P.imshow(P.clip(X,clip,0),origin='lower',aspect='auto', interpolation=interp)
    else:
        P.imshow(X,origin='lower',aspect=aspect, interpolation=interp)
        #P.axes().set_xticks([])
        P.axis('off')
    if title_string:
        P.title(title_string)
    #P.colorbar()

def feature_scale(M, normalize=False, dbscale=False, norm=False, bels=False):
    """
    ::

        Perform mutually-orthogonal scaling operations, otherwise return identity:
          normalize [False]
          dbscale  [False]
          norm      [False]        
    """
    if not (normalize or dbscale or norm or bels):
        return M
    else:
        X = M.copy() # don't alter the original
        if norm:
            X = X / P.tile(P.sqrt((X*X).sum(0)),(X.shape[0],1))
        if normalize:
            X = _normalize(X)
        if dbscale or bels:
            X = P.log10(P.clip(X,0.0001,X.max()))
            if dbscale:                
                X = 10*X
    return X


