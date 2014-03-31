# *******************************************************
# ACTION Example Two: Centers of Mass and Random Sampling
# *******************************************************

from action.suite import *

# 2A: plot random sampling of points from one film
def ex_2A(title):
	pcorr = PhaseCorrelation(title)
	length = pcorr.determine_movie_length() # in seconds

	full_segment = Segment(0, duration=length)
	pcorr_full_film = pcorr.middle_band_phasecorr_features_for_segment(full_segment)

	decomposed = ad.calculate_pca_and_fit(pcorr_full_film, locut=0.001)

	index_array = np.arange(decomposed.shape[0])
	np.random.shuffle(index_array)

	random_samples = decomposed[ np.sort(index_array[:500]) ]

	av.plot_clusters(random_samples, np.zeros(500), ttl='Randomly sampled data points - first three principle components (one film)')
	av.plot_clusters(random_samples[:,3:], np.zeros(500), ttl='Randomly sampled data points - next three principle components (one film)')


# 2B: plot random sampling of points from multiple films
def ex_2B(titles):	
	combo_pcorr = np.zeros(64, dtype='float32')

	for title in titles:
	
		pcorr = PhaseCorrelation(title)
	
		length = pcorr.determine_movie_length() # in seconds

		full_segment = Segment(0, duration=length)
		pcorr_full_film = pcorr.middle_band_phasecorr_features_for_segment(full_segment)
	
		random_samples, order = ad.sample_n_frames(pcorr_full_film, 500)
		combo_pcorr = np.append(np.atleast_2d(combo_pcorr), random_samples, axis=0)

	# get rid of the empty first row
	combo_pcorr = combo_pcorr[1:,:]

	decomposed = ad.calculate_pca_and_fit(combo_pcorr, locut=0.0025)
	#decomposed = np.power(decomposed, 0.1)
	# 500 labels per title
	labels = np.array([i/500 for i in range(500 * len(titles))])
	av.plot_clusters(decomposed, labels, ttl='Randomly sampled data points - first three principle components (3 films)')
	av.plot_clusters(decomposed[:,3:], labels, ttl='Randomly sampled data points - next three principle components (3 films)')

# 2C: plot center of mass of one film
# def ex_2C(title):
# 	
# 	pcorr = PhaseCorrelation(title)
# 	length = pcorr.determine_movie_length() # in seconds
# 
# 	full_segment = Segment(0, duration=length)
# 	pcorr_full_film = pcorr.middle_band_phasecorr_features_for_segment(full_segment)
# 	decomposed = ad.calculate_pca_and_fit(pcorr_full_film, locut=0.001)
# 
# 	center_of_mass = np.mean(pcorr_full_film, axis=0)
# 
# 	av.plot_clusters(np.atleast_2d(center_of_mass), np.array([0]), ttl='ex_2C')
# 	
# 
# 2D: plot centers of mass of multiple films
# def ex_2D(titles):
# 	
# 	combo_means = np.zeros(64, dtype='float32')
# 
# 	for title in titles:
# 
# 		pcorr = PhaseCorrelation(title)
# 		length = pcorr.determine_movie_length() # in seconds
# 
# 		full_segment = Segment(0, duration=length)
# 		pcorr_full_film = pcorr.middle_band_phasecorr_features_for_segment(full_segment)
# 
# 		random_samples, order = ad.sample_n_frames(pcorr_full_film, 500)
# 	
# 		themean = np.mean(random_samples, axis=0)
# 		combo_means = np.append(np.atleast_2d(combo_means), np.atleast_2d(themean), axis=0)
# 
# 	# get rid of the empty first row
# 	combo_means = combo_means[1:,:]
# 
# 	# plot clusters
# 	av.plot_clusters(np.atleast_2d(combo_means), np.array([i for i in range(len(titles))]), ttl='Centers of mass for 3 films')


if __name__ == "__main__":
	title = 'Psycho'
	titles = ['North_by_Northwest', 'Psycho', 'A_Serious_Man']
	
 	F2A = ex_2A(title)
 	F2B = ex_2B(titles)
# 	F2C = ex_2C(title)
# 	F2D = ex_2D(titles)
	
	try:
		choice = str(input('Press enter to exit visualization...'))
	except SyntaxError:
		pass
