# import itertools
import time
import mvpa_pipeline_rand as meta_random_sampling_analysis

# 8-directors task (plus variations)

params = {
	'directors' 			: ['AH', 'AK', 'CB', 'DL', 'JF', 'JLG', 'LB', 'SS'], # these are the eight directors that we have in our database
	'numbers_of_directors'	: [8], # always use all eight directors
	'cflags' 				: [0],
	'titles_per'			: [6, 8], # we will run the task with 6 and 8 films per...
	'samples_per'			: [800,1200,1600,2000], # as well as these numbers of samples
}

# this function runs the task with all combinations of the above parameters

for cflag in params['cflags']:
	for tper in params['titles_per']:
			for samples_per in params['samples_per']:
						
				meta_random_sampling_analysis.call(
					params['directors'],
					tper,
					cflag=2, # color flag 2 = convert any color films to black/white (Lab -> L)
					samples_per=samples_per,
					classifier_num=0, # 0 = Linear Discriminant Analysis; SVM is also available 
					pklfile='/Users/kfl/actionresults/8way_rand/' + time.strftime('%Y%m%d%H%M%S') + '.pkl')
