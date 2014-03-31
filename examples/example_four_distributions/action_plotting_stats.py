#  Example of plotting a joint feature space of three normalized/standardized visual features.

from action.suite import *

cfl_vert = ColorFeaturesLAB('Vertigo')
cfl_nbr = ColorFeaturesLAB('No_Blood_Relation')

pcorr_vert = PhaseCorrelation('Vertigo')
pcorr_nbr = PhaseCorrelation('No_Blood_Relation')

oflow_vert = OpticalFlow('Vertigo')
oflow_nbr = OpticalFlow('No_Blood_Relation')

fullseg_vert = Segment(0, cfl_vert.determine_movie_length())
fullseg_nbr = Segment(0, cfl_nbr.determine_movie_length())

cfl_vert_X = cfl_vert.middle_band_color_features_for_segment(fullseg_vert)
cfl_nbr_X = cfl_nbr.middle_band_color_features_for_segment(fullseg_nbr)
pcorr_vert_X = pcorr_vert.middle_band_phasecorr_features_for_segment(fullseg_vert)
pcorr_nbr_X = pcorr_nbr.middle_band_phasecorr_features_for_segment(fullseg_nbr)
oflow_vert_X = oflow_vert.middle_band_opticalflow_features_for_segment(fullseg_vert)
oflow_nbr_X = oflow_nbr.middle_band_opticalflow_features_for_segment(fullseg_nbr)


cfl_vert_X = ad.normalize_data(cfl_vert_X)
cfl_nbr_X = ad.normalize_data(cfl_nbr_X)
pcorr_vert_X = ad.normalize_data(ad.standardize_data(pcorr_vert_X))
pcorr_nbr_X = ad.normalize_data(ad.standardize_data(pcorr_nbr_X))
oflow_vert_X = ad.normalize_data(np.power(oflow_vert_X, 0.2))
oflow_nbr_X = ad.normalize_data(np.power(oflow_nbr_X, 0.2))

min_time_vert = min([feat.shape[0] for feat in [cfl_vert_X, pcorr_vert_X, oflow_vert_X]])
min_time_nbr = min([feat.shape[0] for feat in [cfl_nbr_X, pcorr_nbr_X, oflow_nbr_X]])

print min_time_vert
print min_time_nbr

video_vert_X = np.c_[cfl_vert_X[:min_time_vert,:], pcorr_vert_X[:min_time_vert,:], oflow_vert_X[:min_time_vert,:]]
video_nbr_X = np.c_[cfl_nbr_X[:min_time_nbr,:], pcorr_nbr_X[:min_time_nbr,:], oflow_nbr_X[:min_time_nbr,:]]


imagesc(video_vert_X.T, ttl='Visual features: normalized, etc. for Vertigo', x_lbl='Time (1/4 seconds)', y_lbl='Frequency')
imagesc(video_nbr_X.T, ttl='Visual features: normalized, etc. for No Blood Relation', x_lbl='Time (1/4 seconds)', y_lbl='Frequency')

imagesc(video_vert_X[:1000,:].T, ttl='Visual features (normalized) for Vertigo - first 1000 frames', x_lbl='Time (1/4 seconds)', y_lbl='Frequency')
imagesc(video_nbr_X[:1000,:].T, ttl='Visual features (normalized) for No Blood Relation - first 1000 frames', x_lbl='Time (1/4 seconds)', y_lbl='Visual Features')


data_col_means = np.mean(video_vert_X, axis=0)
data_col_means2 = np.mean(video_nbr_X, axis=0)
data_col_vars = np.var(video_vert_X, axis=0)
data_col_vars2 = np.var(video_nbr_X, axis=0)

idx = np.arange(48)
barwidth = 0.5
barwidth2 = 0.75

p1 = plt.bar(np.arange(960), data_col_vars2, barwidth2, color='y', bottom=data_col_means2)
p2 = plt.bar(np.arange(960), data_col_vars, barwidth, color='g', bottom=data_col_means)
plt.title('Video features means and variances per bin')


#  Simpler example with just Color Features for two Hitchcock films:

idx = np.arange(48)
barwidth = 0.5
barwidth2 = 0.75

cfl = ColorFeaturesLAB('Rope')
fullseg = Segment(0, cfl.determine_movie_length())
data = cfl.full_color_features_for_segment(fullseg)

cfl2 = ColorFeaturesLAB('North_by_Northwest')
fullseg2 = Segment(0, cfl2.determine_movie_length())
data2 = cfl2.full_color_features_for_segment(fullseg2)


data_col_means = np.mean(data, axis=0)
data_col_means2 = np.mean(data2, axis=0)
data_col_vars = np.var(data, axis=0)
data_col_vars2 = np.var(data2, axis=0)

plt.figure()
p1 = plt.bar(idx, data_col_vars2, barwidth2, color='y', bottom=data_col_means2)
p2 = plt.bar(idx, data_col_vars, barwidth, color='g', bottom=data_col_means)
plt.legend( (p1[0], p2[0]), ('Rope', 'NbNW') )



title = 'Vertigo'

mfccs = ad.read_audio_metadata(os.path.join(ACTION_DIR,title,(title+'.mfcc')))
chromas = ad.read_audio_metadata(os.path.join(ACTION_DIR,title,(title+'.chrom')))
powers = ad.read_audio_metadata(os.path.join(ACTION_DIR,title,(title+'.power')))

mfccs = ad.meanmask_data(mfccs)
mfccs = ad.standardize_data(mfccs)
mfccs = ad.meanmask_data(mfccs)
mfccs = ad.normalize_data(mfccs)
mfccs = ad.meanmask_data(mfccs)

chromas = ad.meanmask_data(chromas)
chromas = ad.standardize_data(chromas)
chromas = ad.meanmask_data(chromas)
chromas = ad.normalize_data(chromas)
chromas = ad.meanmask_data(chromas)

powers = ad.meanmask_data(powers)
powers = ad.normalize_data(powers)
powers = ad.meanmask_data(powers)

imagesc(mfccs.T, ttl='MFCCs - normalized - '+str(title), x_lbl='Time (1/4 seconds)', y_lbl='MFCC Coefficients')
imagesc(chromas.T, ttl='Chromas - normalized - '+str(title), x_lbl='Time (1/4 seconds)', y_lbl='Chromas (12 steps)')
plt.figure()
plt.plot(np.atleast_1d(powers))
plt.title('Normalized power values for whole film - '+str(title))
plt.xlabel('Time (1/4 seconds)')
plt.ylabel('Linear Power')


audio_vert_X =  np.c_[np.atleast_1d(powers), mfccs, chromas]

imagesc(audio_vert_X.T, ttl='Power/MFCC/Chromas - normalized - '+str(title), x_lbl='Time (1/4) seconds', y_lbl='Audio feature bins')

min_length = min(audio_vert_X.shape[0], video_vert_X.shape[0])
all_vert_X = np.c_[video_vert_X[:min_length,:], audio_vert_X[:min_length,:]]

imagesc(all_vert_X.T, ttl='Video/Audio Features - normalized - '+str(title), x_lbl='Time (1/4) seconds', y_lbl='Combined feature bins')