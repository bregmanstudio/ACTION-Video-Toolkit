####################################################
# feature extraction class for L*a*b* color features

from action.suite import *
vertigo_cfl = ColorFeaturesLAB('Vertigo')

# assuming that you have already done the analysis and the analysis is on disc
vertigo_cfl.analyze_movie()

# Play them back
vertigo_cfl.playback_movie()
vertigo_cfl.playback_movie(offset=60, duration=60)

# determine a film's duration (in seconds)
length = vertigo_cfl.determine_movie_length()

# before going on, clean up
del vertigo_cfl


##########################################
# data for the four central cells (of a 4 by 4 grid), for minute 2

from action.suite import *

vertigo_cfl = ColorFeaturesLAB('Vertigo')
myseg = Segment(60, duration=60)
full_data = vertigo_cfl.full_color_features_for_segment(myseg)

print full_data.shape
# (240, 48)

# different segment length:
myseg = Segment(120, duration=360)
# different set of regions on screen:
cq_data = vertigo_cfl.center_quad_color_features_for_segment(myseg)

# different data:
print cq_data.shape
# (1440, 192)




#####################################################
# opticalflow

from action.suite import *

oflow = OpticalFlow('Vertigo')
myseg = Segment(60, duration=60)
###!!! oflow_data = oflow.opticalflow_features_for_segment_with_stride(myseg, stride=6)

# different data:
print oflow_data.shape
# (240, 512)


#####################################################
# phase correlation

from action.suite import *

pcorr = PhaseCorrelation('Vertigo')
myseg = Segment(60, duration=60)
pcorr_data = pcorr.phasecorr_features_for_segment_with_stride(myseg, stride=6)

# different data:
print pcorr_data.shape
# (31096, 128)


