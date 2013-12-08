from action import *
import action.segment as aseg
import numpy as np
from bregman.suite import *

idx = np.arange(48)
width = 0.5
width2 = 0.75


cfl = color_features_lab.ColorFeaturesLAB('Rope')
fullseg = aseg.Segment(0, cfl.determine_movie_length())
data = cfl.full_color_features_for_segment(fullseg)

cfl2 = color_features_lab.ColorFeaturesLAB('North_by_Northwest')
fullseg2 = aseg.Segment(0, cfl2.determine_movie_length())
data2 = cfl2.full_color_features_for_segment(fullseg2)


ad = actiondata.ActionData()
data_col_means = np.mean(data, axis=0)
data_col_means2 = np.mean(data2, axis=0)
data_col_vars = np.var(data, axis=0)
data_col_vars2 = np.var(data2, axis=0)

p1 = plt.bar(idx, data_col_vars2, width2, color='y', bottom=data_col_means2)
p2 = plt.bar(idx, data_col_vars, width, color='g', bottom=data_col_means)
plt.legend( (p1[0], p2[0]), ('Rope', 'NbNW') )
