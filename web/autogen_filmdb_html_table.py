import action.action_filmdb as fdb
import HTML, glob, os

full_db = fdb.FilmDB()
actionDB = full_db.actionDB
actionDirectors = full_db.actionDirectors
action_titles = set(actionDB)

# just save it to the desktop
HTMLFILE = os.path.expanduser('~/Desktop/HTML_table.html')
f = open(HTMLFILE, 'w')



titles = ["Title"] + sorted(list(action_titles))


cflabs = ["Lab Colors"]
pcorrs = ["Phase Correlation Vecs"]
cflsegs = ["Color Seg"]
chromas = ["Chroma"]
cqfts = ["CQFT"]
mfccs = ["MFCC"]
powers = ["Power"]
mfccsegs = ["MFCC Seg"]
dirs = ["Director"]
years = ["Year"]

for t in titles[1:]:
    cflabs += [(t + '.color_lab')]
    pcorrs += [(t + '.phasecorr')]
    cflsegs += [(t + '_cfl_hc.pkl')]
    chromas += [(t + '.chrom_12_a0_C2_g0_i16000')]
    cqfts += [(t + '.cqft_12_a0_C2_g0_i16000')]
    mfccs += [(t + '.mfcc_13_M2_a0_C2_g0_i16000')]
    powers += [(t + '.power_C2_i16000')]
    mfccsegs += [(t + '_mfccs_hc.pkl')]
    dirs += [actionDB[t][1]]
    years += [str(actionDB[t][3])]


full_table = [["Title", "Lab Colors", "Phase Correlation", "Color Seg", "Chromas", "CQFTs", "MFCCs", "Powers", "MFCC Seg", "Director", "Year"]]

for i, t in enumerate(titles[1:]):
	full_table += [[
		titles[i+1],
		HTML.link('.color_lab', ('actiondata/' + titles[i+1] + '/' + cflabs[i+1])),
		HTML.link('.phasecorr', ('actiondata/' + titles[i+1] + '/' + pcorrs[i+1])),
		HTML.link('_cfl_hc.pkl', ('actiondata/' + titles[i+1] + '/' + cflsegs[i+1])),
		HTML.link('.chrom', ('actiondata/' + titles[i+1] + '/' + chromas[i+1])),
		HTML.link('.cqft', ('actiondata/' + titles[i+1] + '/' + cqfts[i+1])),
		HTML.link('.mfcc', ('actiondata/' + titles[i+1] + '/' + mfccs[i+1])),
		HTML.link('.power', ('actiondata/' + titles[i+1] + '/' + powers[i+1])),
		HTML.link('_mfccs_hc.pkl', ('actiondata/' + titles[i+1] + '/' + mfccsegs[i+1])),
		dirs[i+1],
		years[i+1]]]
		
	
htmlcode = HTML.table(full_table)
print htmlcode
f.write(htmlcode)
f.write('<p>')

f.close()

# Once saved to the Desktop, the file can be opened and the table copied to whatever html document will host the download links