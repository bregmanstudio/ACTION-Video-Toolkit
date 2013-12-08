# *******************************
# Example Three: Similarity Plots
# *******************************


from action import *
import action.segment as aseg
import numpy as np
from bregman.suite import *
import bregman.audiodb as adb

# 3A: Similarity plots using cosine distance
def ex_3A(title):
	hist = histogram.Histogram(title)
	oflow = opticalflow.OpticalFlow(title)
	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4
	ten_minute_segment = aseg.Segment(0, duration=length)
	histogram_ten_minute_segment = hist.center_quad_histogram_for_segment(ten_minute_segment)
	oflow_ten_minute_segment = oflow.opticalflow_for_segment(ten_minute_segment)

	ad = actiondata.ActionData()
	h_decomposed = ad.calculate_pca_and_fit(histogram_ten_minute_segment, locut=0.0001)
	o_decomposed = ad.calculate_pca_and_fit(oflow_ten_minute_segment, locut=1)
	
	# av = actiondata.ActionView(None)
	imagesc(distance.cosine(h_decomposed, h_decomposed), 'Cosine: Histograms-SVD - first 10 minutes')
	imagesc(distance.cosine(o_decomposed, o_decomposed), 'Cosine: Optical flow-SVD - first 10 minutes')


# 3B: Four similarity plots of audio features (mfccs)
def ex_3B(title):

	mfccs_ten_minute_segment = adb.adb.read(os.path.expanduser('~/Movies/action/') + title + '/' + title + '.mfcc_13_M2_a0_C2_g0_i16000')[:2400,:]
	D = np.ma.masked_invalid(mfccs_ten_minute_segment)
	D = D.filled(D.mean())

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(D, locut=0.0001)

	imagesc(distance.euc2(D, D))
	imagesc(distance.euc2(decomposed, decomposed))
	imagesc(distance.cosine(D, D))
	imagesc(distance.cosine(decomposed, decomposed))
	

# 3C: Two similarity plots of combined histogram, optical flow, and audio (mfccs) features
def ex_3C(title):

	hist = histogram.Histogram(title)
	oflow = opticalflow.OpticalFlow(title)
	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4
	ten_minute_segment = aseg.Segment(0, duration=length)
	histogram_ten_minute_segment = hist.center_quad_histogram_for_segment(ten_minute_segment)
	oflow_ten_minute_segment = oflow.opticalflow_for_segment(ten_minute_segment)

	mfccs_ten_minute_segment = adb.adb.read(os.path.expanduser('~/Movies/action/') + title + '/' + title + '.mfcc_13_M2_a0_C2_g0_i16000')[:2400,:]
	audio = np.ma.masked_invalid(mfccs_ten_minute_segment)
	audio = audio.filled(audio.mean())

	full_feature = np.c_[histogram_ten_minute_segment, oflow_ten_minute_segment, audio]
	ad = actiondata.ActionData()
	full_feature_decomposed = ad.calculate_pca_and_fit(full_feature, locut=0)

	imagesc(distance.cosine(full_feature, full_feature), 'ex_3C full feature')
	imagesc(distance.cosine(full_feature_decomposed, full_feature_decomposed), 'ex_3C full feature, decomposed')

if __name__ == "__main__":
	title = 'North_by_Northwest'
	
	F3A = ex_3A(title)
	F3B = ex_3B(title)
	F3C = ex_3C(title)
	
	try:
		choice = str(input('Press enter to exit visualization...'))
	except SyntaxError:
		pass
