import films_db as fdb
import HTML, glob, os

# get your list of file names
# os.chdir('/Users/kfl/Movies/action')
# names = glob.glob('*')
# names_with_proper_oflow_exts = [glob.glob(name + '.optical*')[0] for name in names]

HTMLFILE = '/Users/kfl/actionresults/HTML_tutorial_output.html'
f = open(HTMLFILE, 'w')

titles = ["Title"] + sorted(list(fdb.actionDB.keys()))


histograms = ["Histograms"]
mvecs = ["Motion Vectors"]
oflows = ["Optical Flow"]
chromas = ["Chroma"]
cqfts = ["CQFT"]
mfccs = ["MFCC"]
powers = ["Power"]
dirs = ["Director"]
years = ["Year"]

for t in titles[1:]:
    histograms += [(t + '.hist')]
    mvecs += [(t + '.opticalflow3')]
    oflows += [(t + '.opticalflow24')]
    chromas += [(t + '.chrom_12_a0_C2_g0_i16000')]
    cqfts += [(t + '.cqft_12_a0_C2_g0_i16000')]
    mfccs += [(t + '.mfcc_13_M2_a0_C2_g0_i16000')]
    powers += [(t + '.power_C2_i16000')]
    dirs += [fdb.actionDB[t][1]]
    years += [str(fdb.actionDB[t][3])]


full_table = [["Title", "Histograms", "Motion Vectors", "Chromas", "CQFTs", "MFCCs", "Powers", "Director", "Year"]]

for i, t in enumerate(titles[1:]):
	full_table += [[
		titles[i+1],
		HTML.link('.hist', ('action/' + titles[i+1] + '/' + histograms[i+1])),
		HTML.link('.opticalflow3', ('action/' + titles[i+1] + '/' + mvecs[i+1])),
		HTML.link('.opticalflow24', ('action/' + titles[i+1] + '/' + oflows[i+1])),
		HTML.link('.chrom', ('action/' + titles[i+1] + '/' + chromas[i+1])),
		HTML.link('.cqft', ('action/' + titles[i+1] + '/' + cqfts[i+1])),
		HTML.link('.mfcc', ('action/' + titles[i+1] + '/' + mfccs[i+1])),
		HTML.link('.power', ('action/' + titles[i+1] + '/' + powers[i+1])),
		dirs[i+1],
		years[i+1]]]
		
	
htmlcode = HTML.table(full_table)
print htmlcode
f.write(htmlcode)
f.write('<p>')

f.close()