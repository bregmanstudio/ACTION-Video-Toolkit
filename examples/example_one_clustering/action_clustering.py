# *************************
# Example One: Clustering
# *************************


from action import *
import action.segment as aseg
import numpy as np

ACTION_DIR = '/Users/kfl/Movies/action'

# 1A: K-means Clustering of first 2400 frames (10 minutes)
def ex_1A(title):
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4
	ten_minute_segment = aseg.Segment(0, duration=length)
	cf_ten_minute_segment = cfl.center_quad_color_features_for_segment(ten_minute_segment)

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(cf_ten_minute_segment, locut=0.0001)
	sliding_averaged = ad.average_over_sliding_window(decomposed, 8, 4)

	nc = 60 # sample 300 frames from total pool of 600 or 10%.
	km_assigns, km_max_assign = ad.cluster_k_means(sliding_averaged, nc)

	av = actiondata.ActionView(None)
	av.plot_clusters(sliding_averaged, km_assigns, 'K Means - first three dimensions (0-2)')
	av.plot_hcluster_segments(km_assigns, km_max_assign) #, 'K Means - segmentation view')


# 1B: Hierarchical Clustering of full movie
def ex_1B(title):
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	length = cfl.determine_movie_length() # in seconds
	full_segment = aseg.Segment(0, duration=length)
	#cf_full_film = cfl.center_quad_color_features_for_segment(full_segment)
	cf_full_film = cfl.middle_band_color_features_for_segment(full_segment)

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(cf_full_film, locut=0.0001)

	nc = 1000 # Rouchly 5/minute for a feature-length film.
	hc_assigns = ad.cluster_hierarchically(decomposed, nc, None)

	av = actiondata.ActionView(None)
	av.plot_clusters(decomposed, hc_assigns, 'Hierarchical - first three dimensions (0-2)')
	av.plot_hcluster_segments(hc_assigns, nc) #, 'Hierarchical - segmentation view')

	av.plot_clusters(decomposed[:,1:], hc_assigns, 'Hierarchical - dimensions 1-3')



def ex_1C(title):
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	length = cfl.determine_movie_length() # in seconds
	full_segment = aseg.Segment(0, duration=length)
	#cf_full_film = cfl.center_quad_color_features_for_segment(full_segment)
	cf_full_film = cfl.middle_band_color_features_for_segment(full_segment)

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(cf_full_film, locut=0.0001)

	nc = int(length * 0.2) # Setting the density of clusters with a ratio. - don't forget the int cast!
	hc_assigns = ad.cluster_hierarchically(decomposed, nc, None)

	com = np.array([],dtype='float32')
	comd = np.array([],dtype='float32')
	for hci in range(hc_assigns.max()+1):
		seg = cf_full_film[np.argwhere(hc_assigns==hci)]
		seg = np.reshape(seg, (-1, cf_full_film.shape[1]))
		com = np.append(np.atleast_2d(com), np.mean(seg, axis=0))
		com = np.reshape(com, (-1, cf_full_film.shape[1]))
		segd = decomposed[np.argwhere(hc_assigns==hci)]
		segd = np.reshape(segd, (-1, decomposed.shape[1]))
		comd = np.append(np.atleast_2d(comd), np.mean(segd, axis=0))
		comd = np.reshape(comd, (-1, decomposed.shape[1]))


	av = actiondata.ActionView(None)
	av.plot_clusters(decomposed, hc_assigns, 'Hierarchical - first three dimensions (0-2)')
	av.plot_hcluster_segments(hc_assigns, nc) #, 'Hierarchical - segmentation view')

	labeling = np.array(range(nc))
	av.plot_clusters(com, labeling, 'HC centers of mass - first three dimensions (0-2)')
	av.plot_clusters(comd, labeling, 'HC centers of mass, decomposed - first three dimensions (0-2)')

if __name__ == "__main__":
	title = 'Vertigo'
	
	F1A = ex_1A(title)
	F1B = ex_1B(title)
	F1C = ex_1C(title)
	
	try:
		choice = str(input('Press enter to exit visualization...'))
	except SyntaxError:
		pass
