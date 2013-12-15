import action.action_filmdb as fdb
import HTML, glob, os

full_db = fdb.FilmDB()
actionDB = full_db.actionDB
actionDirectors = full_db.actionDirectors
action_titles = set(actionDB)

HTMLFILE = os.path.expanduser('~/Desktop/action_zipped.html')
f = open(HTMLFILE, 'w')

titles = ["Title"] + sorted(list(action_titles))
links = ["Links"]
dirs = ["Director"]
years = ["Year"]
colors = ["Color"]

for t in titles[1:]:
    links += [HTML.link(str(t), "actiondata/" + str(t) + ".zip")]
    # links += [HTML.link(str(t), ("info.php?q=" + str(t)]
    dirs += [actionDB[t][1]]
    years += [str(actionDB[t][3])]
    colors += [str(actionDB[t][2])]

full_table = [["Title", "Director", "Year"]]

for i, t in enumerate(titles[1:]):
	full_table += [[
		links[i+1],
		dirs[i+1],
		years[i+1],
		colors[i+1]]]
		

htmlcode = HTML.table(full_table)
# print htmlcode
f.write(htmlcode)
f.write('<p>')

f.close()