import film_db as fdb
import HTML, glob, os

# get your list of file names
# os.chdir('/Users/kfl/Movies/action')
# names = glob.glob('*')
# names_with_proper_oflow_exts = [glob.glob(name + '.optical*')[0] for name in names]

HTMLFILE = '/Users/kfl/actionresults/HTML_tutorial_output.html'
f = open(HTMLFILE, 'w')

titles = ["Title"] + sorted(list(fdb.actionDB.keys()))
links = ["Links"]
dirs = ["Director"]
years = ["Year"]
color = ["Color"]

for t in titles[1:]:
    #links += [HTML.link(str(t), "_static/actiondata/" + str(t) + ".zip")]
    links += [HTML.link(str(t), ("info.php?q=" + str(t)]
    dirs += [fdb.actionDB[t][1]]
    years += [str(fdb.actionDB[t][3])]
    color += [str(fdb.actionDB[t][2])]

full_table = [["Title", "Director", "Year"]]

for i, t in enumerate(titles[1:]):
	full_table += [[
		links[i+1],
		dirs[i+1],
		years[i+1]]]
		

htmlcode = HTML.table(full_table)
print htmlcode
f.write(htmlcode)
f.write('<p>')

f.close()