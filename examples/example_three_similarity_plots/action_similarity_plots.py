# *******************************
# Example Three: Dissimilarity Plots
# *******************************


import numpy as np
from bregman.suite import *
from action import *
import action.segment as aseg
from action.actiondata import adb

ACTION_DIR = '~/Movies/action/'

# 3A: Dissimilarity plots using cosine distance
def ex_3A(title):
	cfl = color_features_lab.ColorFeaturesLAB(title, action_dir=ACTION_DIR)
	pcorr = phase_correlation.PhaseCorrelation(title, action_dir=ACTION_DIR)
	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4
	ten_minute_segment = aseg.Segment(0, duration=length)
	cfl_ten_minute_segment = cfl.center_quad_color_features_for_segment(ten_minute_segment)
	pcorr_ten_minute_segment = pcorr.center_quad_phasecorr_features_for_segment(ten_minute_segment, access_stride=6)

	ad = actiondata.ActionData()
	c_decomposed = ad.calculate_pca_and_fit(cfl_ten_minute_segment, locut=0.0001)
	p_decomposed = ad.calculate_pca_and_fit(pcorr_ten_minute_segment, locut=0.01)

	imagesc(distance.euc2(c_decomposed, c_decomposed), title_string='EUC: Color features-PCA - first 10 minutes')
	imagesc(distance.euc2(p_decomposed, p_decomposed), title_string='EUC: Phase corr.-PCA - first 10 minutes')

	imagesc(distance.cosine(c_decomposed, c_decomposed), title_string='Cosine: Color features-PCA - first 10 minutes')
	imagesc(distance.cosine(p_decomposed, p_decomposed), title_string='Cosine: Phase corr.-PCA - first 10 minutes')

	combo_decomposed = np.c_[c_decomposed, p_decomposed]

	imagesc(distance.euc2(combo_decomposed, combo_decomposed), title_string='EUC: Combo-PCA - first 10 minutes')
	imagesc(distance.cosine(combo_decomposed, combo_decomposed), title_string='Cosine: Combo-PCA - first 10 minutes')


# 3B: Four dissimilarity plots of audio features (mfccs)
def ex_3B(title):

	mfccs_ten_minute_segment = adb.read(os.path.expanduser(ACTION_DIR) + title + '/' + title + '.mfcc')[:2400,:]
	D = np.ma.masked_invalid(mfccs_ten_minute_segment)
	D = D.filled(D.mean())

	ad = actiondata.ActionData()
	decomposed = ad.calculate_pca_and_fit(D, locut=0.2)

	imagesc(distance.euc2(D, D), title_string='EUC: MFCC - first 10 minutes')
	imagesc(distance.euc2(decomposed, decomposed), title_string='EUC: MFCC-PCA - first 10 minutes')
	imagesc(distance.cosine(D, D), title_string='Cosine: MFCC - first 10 minutes')
	imagesc(distance.cosine(decomposed, decomposed), title_string='Cosine: MFCC-PCA - first 10 minutes')
	

# 3C: Two dissimilarity plots of combined histogram, phase correlation, and audio (mfccs) features
def ex_3C(title):

	cfl = color_features_lab.ColorFeaturesLAB(title)
	pcorr = phase_correlation.PhaseCorrelation(title)
	length = 600 # 600 seconds = 10 minutes
	length_in_frames = length * 4
	ten_minute_segment = aseg.Segment(0, duration=length)
	cfl_ten_minute_segment = cfl.center_quad_color_features_for_segment(ten_minute_segment)
	pcorr_ten_minute_segment = pcorr.center_quad_phasecorr_features_for_segment(ten_minute_segment) # default stride is 6!

	mfccs_ten_minute_segment = adb.read(os.path.expanduser(ACTION_DIR) + title + '/' + title + '.mfcc')[:2400,:]
	audio = np.ma.masked_invalid(mfccs_ten_minute_segment)
	audio = audio.filled(audio.mean())

	cfl_normed		= cfl_ten_minute_segment
	pcorr_normed	= ad.normalize_data(pcorr_ten_minute_segment)
	mfccs_normed	= ad.normalize_data(audio)

	full_feature = np.c_[cfl_normed, pcorr_normed, mfccs_normed]
	ad = actiondata.ActionData()
	full_feature_decomposed = ad.calculate_pca_and_fit(full_feature, locut=0.01)

	imagesc(distance.cosine(full_feature, full_feature), title_string='Cosine: full feature - first 10 minutes')
	imagesc(distance.cosine(full_feature_decomposed, full_feature_decomposed), title_string='Cosine: PCA - full feature - first 10 minutes')

	imagesc(distance.euc2(full_feature, full_feature), title_string='EUC: full feature - first 10 minutes')
	imagesc(distance.euc2(full_feature_decomposed, full_feature_decomposed), title_string='EUC: PCA - full feature - first 10 minutes')

if __name__ == "__main__":
	title = 'North_by_Northwest'
	
	F3A = ex_3A(title)
	F3B = ex_3B(title)
	F3C = ex_3C(title)
	
	try:
		choice = str(input('Press enter to exit visualization...'))
	except SyntaxError:
		pass
