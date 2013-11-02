# **************************************************
# Tutorial Five: Centers of Mass and Random Sampling
# **************************************************


from action import *
import bregman.segment as bseg
import numpy as np

# 5A: plot random sampling of points from one film
def ex_5A(title):
	
	ad = actiondata.ActionData()
	av = actiondata.ActionView(None)
	oflow = opticalflow.OpticalFlow(title)
	
	length = oflow.determine_movie_length() # in seconds
	length_in_frames = length * 4
	
	full_segment = bseg.Segment(0, duration=length)
	oflow_full_film = oflow.opticalflow_for_segment(full_segment)
	
	decomposed = ad.calculate_pca_and_fit(oflow_full_film, locut=100.0)

	index_array = np.arange(decomposed.shape[0])
	np.random.shuffle(index_array)
	
	# try removing the sorting step
	random_samples = decomposed[ np.sort(index_array[:500]) ]
	
	av.plot_clusters(random_samples, np.zeros(500), ttl='ex_5A dims 0-2')
	av.plot_clusters(random_samples[:,1:], np.zeros(500), ttl='ex_5A dims 1-3')


# 5B: plot random sampling of points from multiple films
def ex_5B(titles):
	
	ad = actiondata.ActionData()
	av = actiondata.ActionView(None)
	combo_oflow = np.zeros(128, dtype='float32')
	
	for title in titles:
		
		oflow = opticalflow.OpticalFlow(title)
		
		length = oflow.determine_movie_length() # in seconds
		length_in_frames = length * 4
	
		full_segment = bseg.Segment(0, duration=length)
		oflow_full_film = oflow.opticalflow_for_segment(full_segment)

		index_array = np.arange(oflow_full_film.shape[0])
		np.random.shuffle(index_array)
		random_samples = oflow_full_film[ np.sort(index_array[:500]) ]
		print combo_oflow.shape
		print random_samples.shape
		combo_oflow = np.append(np.atleast_2d(combo_oflow), random_samples, axis=0)
	
	# get rid of the empty first row
	combo_oflow = combo_oflow[1:,:]

	decomposed = ad.calculate_pca_and_fit(combo_oflow, locut=10.0)
	# 500 labels per title
	labels = np.array([i/500 for i in range(500 * len(titles))])
	av.plot_clusters(decomposed, labels, ttl='ex_5B dims 0-2')
	av.plot_clusters(decomposed[:,1:], labels, ttl='ex_5B dims 1-3')

# 5C: plot center of mass of one film
def ex_5C(title):
	
	av = actiondata.ActionView(None)
	oflow = opticalflow.OpticalFlow(title)
	
	length = oflow.determine_movie_length() # in seconds
	length_in_frames = length * 4
	
	full_segment = bseg.Segment(0, duration=length)
	oflow_full_film = oflow.opticalflow_for_segment(full_segment)

	center_of_mass = np.mean(oflow_full_film, axis=0)
	
	av.plot_clusters(np.atleast_2d(center_of_mass), np.array([0]), ttl='ex_5A')
	

# 5D: plot centers of mass of multiple films
def ex_5D(titles):
	
	av = actiondata.ActionView(None)
	combo_oflow = np.zeros(128, dtype='float32')
	
	for title in titles:
		oflow = opticalflow.OpticalFlow(title)
		
		length = oflow.determine_movie_length() # in seconds
		length_in_frames = length * 4
		
		full_segment = bseg.Segment(0, duration=length)
		oflow_full_film = oflow.opticalflow_for_segment(full_segment)
				
		oflow_COM = np.mean(oflow_full_film, axis=0)
		print combo_oflow.shape
		print oflow_COM.shape
		combo_oflow = np.append(np.atleast_2d(combo_oflow), np.atleast_2d(oflow_COM), axis=0)
	
	combo_oflow = combo_oflow[1:,:] # get rid of row of 0's
	
	# plot once
	av.plot_clusters(np.atleast_2d(combo_oflow)[:,1:], np.array([i for i in range(len(titles))]), ttl='ex_5D: multiple Hitchcock films, centroids')


if __name__ == "__main__":
	title = 'North_by_Northwest'
	titles = ['North_by_Northwest', 'Psycho', 'Rear_Window', 'Vertigo']
	
 	F5A = ex_5A(title)
 	F5B = ex_5B(titles)
	F5C = ex_5C(title)
	F5D = ex_5D(titles)
	
	try:
		choice = str(input('Press enter to exit visualization...'))
	except SyntaxError:
		pass
	

