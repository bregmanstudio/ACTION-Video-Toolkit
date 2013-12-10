import action.color_features_lab as cflab
import action.actiondata as actiondata
import action.segment as aseg
import numpy as np
from bregman.suite import *
# import bregman.audiodb as adb
from mvpa2.suite import *
import pylab as P
from matplotlib import offsetbox
from sklearn import (manifold, datasets, decomposition, ensemble, lda,
                     random_projection)

def sampleAllFilms(titles, directors, num_samples=500):
	ad = actiondata.ActionData()
	d_num = len(directors)*num_samples

	all_histograms = np.zeros(384, dtype='float32')
	
	for i, title in enumerate(titles):

		cfl = cflab.ColorFeaturesLAB(title)
		length = cfl.determine_movie_length() # in seconds
		full_segment = aseg.Segment(0, duration=length)
		print 'L: ', full_segment
		Dmb = cfl.middle_band_color_features_for_segment(full_segment)
		print Dmb.shape

		Dmb_sampled, sindex = ad.sample_n_frames(Dmb, num_samples) # sorted!
		print Dmb_sampled.shape
		all_histograms = np.append(np.atleast_2d(all_histograms), Dmb_sampled, axis=0)
		print all_histograms.shape

	all_histograms = np.reshape(all_histograms, (-1, 384))[1:,:]
	return all_histograms, titles


def plot_embedding(X, y, titles, ttls_per_dir=9, plot_title='???'):
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    X = (X - x_min) / (x_max - x_min)

    P.figure()
    ax = P.subplot(111)
    for i in range(X.shape[0]):
        P.text(X[i, 0], X[i, 1], str(titles[y[i]]),
                color=P.cm.Set1((y[i] / ttls_per_dir) / 3.),
                fontdict={'weight': 'bold', 'size': 9})

    if hasattr(offsetbox, 'AnnotationBbox'):
        # only print thumbnails with matplotlib > 1.0
        shown_images = np.array([[1., 1.]])  # just something big
        for i in range(X.shape[0]):
            dist = np.sum((X[i] - shown_images) ** 2, 1)
            if np.min(dist) < 4e-3:
                # don't show points that are too close
                continue
            shown_images = np.r_[shown_images, [X[i]]]
    P.xticks([]), P.yticks([])
    if plot_title is not None:
        P.title(plot_title)

# params for the overall analysis task
TITLES_PER_DIR = 9
NUMBER_OF_DIRECTORS = 3
SAMPLE_FRAMES_PER_TITLE = 50
TITLES = [
	'Blue_Velvet', 'Dune', 'Inland_Empire', 'Lost_Highway', 'Mulholland_Drive', 'Eraserhead', 'Twin_Peaks', 'Twin_Peaks_Ep1', 'Wild_at_Heart',
	'Rope', 'North_by_Northwest', 'Psycho', 'Rear_Window', 'Vertigo', 'The_Lady_Vanishes', 'The_Birds', 'Sullivans_Travels', 'Strangers_on_a_Train',
	'Le_Petit_Soldat', 'Detective', 'Le_Quattro_Volte', 'Made_in_USA', 'Notre_Musique', 'Pierrot_le_Fou', 'In_Praise_of_Love', 'Tout_Va_Bien', 'Weekend'
	]
DIRECTORS = [
	'DL', 'DL', 'DL', 'DL', 'DL', 'DL', 'DL', 'DL', 'DL', 
	'AH', 'AH', 'AH', 'AH', 'AH', 'AH', 'AH', 'AH', 'AH', 
	'JLG', 'JLG', 'JLG', 'JLG', 'JLG', 'JLG', 'JLG', 'JLG', 'JLG']

# params specifically for MDS
NUM_NEIGHBORS = SAMPLE_FRAMES_PER_TITLE

# Roll up all the analysis data
X, ttls = sampleAllFilms(TITLES, DIRECTORS, SAMPLE_FRAMES_PER_TITLE)
y = [i/NUM_NEIGHBORS for i in range(SAMPLE_FRAMES_PER_TITLE*TITLES_PER_DIR*NUMBER_OF_DIRECTORS)]
n_samples, n_features = X.shape


Xconcat = np.array([np.concatenate(X[(i*SAMPLE_FRAMES_PER_TITLE):((i+1)*SAMPLE_FRAMES_PER_TITLE),:]) for i in  range(TITLES_PER_DIR*NUMBER_OF_DIRECTORS)])
yconcat = range(TITLES_PER_DIR*NUMBER_OF_DIRECTORS)


ad = actiondata.ActionData()

X_stdzd = np.divide(Xconcat, np.max(Xconcat))
X_stdzd_ma = np.ma.masked_invalid(X_stdzd)
X_stdzd_ma = X_stdzd_ma.filled(np.mean(X_stdzd))

X_reduced = X_stdzd_ma #ad.calculate_pca_and_fit(X_stdzd_ma, locut=0.0001)

D = ad.calculate_self_similarity_matrix(X_reduced, X_reduced)
D = np.ma.masked_invalid(D)
D = D.filled(np.mean(D))

clf = manifold.MDS(n_components=2, n_init=1, max_iter=100)

X_mds = clf.fit_transform(D)

plot_embedding(X_mds, yconcat, titles=ttls, plot_title='Multi-dimensional Scaling (3 directors + 9 films each)')