# *******************************************************
# ACTION Example Two: Centers of Mass and Random Sampling
# *******************************************************

from action.suite import *
import action.segment as aseg
import numpy as np

# 2A: plot random sampling of points from one film
def ex_2A(title):
	
	oflow = OpticalFlow(title)
	
	length = oflow.determine_movie_length() # in seconds
	length_in_frames = length * 4
	
	full_segment = Segment(0, duration=length)
	oflow_full_film = oflow.opticalflow_for_segment(full_segment)
	
	decomposed = ad.calculate_pca_and_fit(oflow_full_film, locut=100.0)

	index_array = np.arange(decomposed.shape[0])
	np.random.shuffle(index_array)
	
	# take the 10th root to better visualize the data
	decomposed = np.power(decomposed, 0.1)
	random_samples = decomposed[ np.sort(index_array[:500]) ]
	
	av.plot_clusters(random_samples, np.zeros(500), ttl='ex_2A dims 0-2')
	av.plot_clusters(random_samples[:,1:], np.zeros(500), ttl='ex_2A dims 1-3')


# 2B: plot random sampling of points from multiple films
def ex_2B(titles):
	
	combo_oflow = np.zeros(512, dtype='float32')
	
	for title in titles:
		
		oflow = OpticalFlow(title)
		
		length = oflow.determine_movie_length() # in seconds
		length_in_frames = length * 4
	
		full_segment = Segment(0, duration=length)
		oflow_full_film_strided = oflow.opticalflow_for_segment_with_stride(full_segment)
		
		random_samples, order = ad.sample_n_frames(oflow_full_film_strided, 500)
		print combo_oflow.shape
		print random_samples.shape
		combo_oflow = np.append(np.atleast_2d(combo_oflow), random_samples, axis=0)
	
	# get rid of the empty first row
	combo_oflow = combo_oflow[1:,:]

	decomposed = ad.calculate_pca_and_fit(combo_oflow, locut=100.0)
	decomposed = np.power(decomposed, 0.1)
	# 500 labels per title
	labels = np.array([i/500 for i in range(500 * len(titles))])
	av.plot_clusters(decomposed, labels, ttl='ex_2B dims 0-2')
	av.plot_clusters(decomposed[:,1:], labels, ttl='ex_2B dims 1-3')

# 2C: plot center of mass of one film
def ex_2C(title):
	
	oflow = OpticalFlow(title)
	
	length = oflow.determine_movie_length() # in seconds
	length_in_frames = length * 4
	
	full_segment = Segment(0, duration=length)
	oflow_full_film = oflow.opticalflow_for_segment_with_stride(full_segment)

	center_of_mass = np.mean(np.power(oflow_full_film, 0.1), axis=0)
	
	av.plot_clusters(np.atleast_2d(center_of_mass), np.array([0]), ttl='ex_2C')
	

# 2D: plot centers of mass of multiple films
def ex_2D(titles):
	
	av = actiondata.ActionView(None)
	combo_oflow = np.zeros(512, dtype='float32')
	
	for title in titles:
		oflow = OpticalFlow(title)
		
		length = oflow.determine_movie_length() # in seconds
		length_in_frames = length * 4
		
		full_segment = Segment(0, duration=length)
		oflow_full_film = oflow.opticalflow_for_segment_with_stride(full_segment)
				
		oflow_COM = np.mean(np.power(oflow_full_film, 0.1), axis=0)
		print combo_oflow.shape
		print oflow_COM.shape
		combo_oflow = np.append(np.atleast_2d(combo_oflow), np.atleast_2d(oflow_COM), axis=0)
	
	combo_oflow = combo_oflow[1:,:] # get rid of row of 0's
	
	# plot once
	av.plot_clusters(np.atleast_2d(combo_oflow)[:,1:], np.array([i for i in range(len(titles))]), ttl='ex_2D: multiple Hitchcock films, centroids')


if __name__ == "__main__":
	title = 'North_by_Northwest'
	titles = ['North_by_Northwest', 'Psycho', 'Rope', 'Vertigo']
	
 	F2A = ex_2A(title)
 	F2B = ex_2B(titles)
	F2C = ex_2C(title)
	F2D = ex_2D(titles)
	
	try:
		choice = str(input('Press enter to exit visualization...'))
	except SyntaxError:
		pass
