import action.action_filmdb as fdb
import HTML, glob, os, md5, shutil

ACTIONDIR = '/Users/kfl/Movies/action'
WEBDIR = '/Users/kfl/Sites/actiondata'

# FILM_DB controls what films are active 
full_db = fdb.FilmDB()
actionDB = full_db.actionDB
titles = set(actionDB)

print len(titles)

html_filestring = '/Users/kfl/Sites/action_db.html'
htmlfile = open(html_filestring, 'w')

htitles = []
links = []
dirs = []
years = []
colors = []
hashes = []

for file in glob.glob("/Users/kfl/Movies/action/*/*.color_lab"):
	ttl = os.path.splitext(os.path.basename( file ))[0]
	print 'title: ', ttl
	# check that the title is in our master list
	if ttl in titles:

		# HASH the file[name] to a unique ID
		hash = md5.new(str(ttl + '.color_lab'))
		hashstr = str(hash.hexdigest())
		
		# Check to see if there is a folder/film with that unique ID
		if not os.path.exists(os.path.join(WEBDIR,hashstr)):
			os.makedirs(os.path.join(WEBDIR,hashstr))
		
		# Create the text file for the metadata
		txtfile = os.path.join(WEBDIR, hashstr, (str(ttl) + '.txt'))
# 		print txtfile
		f = open(txtfile, 'w')
		
		# Write to it...
		f.write(hashstr + "\n")
		f.write(str(actionDB[ttl][0]) + "\n")
		f.write(HTML.link(str(ttl), ("film_detail.php?hash=" + hashstr + "&t=30&mf=20&g=60")) + "\n")
		f.write(str(actionDB[ttl][1]) + "\n")
		f.write(str(actionDB[ttl][3]) + "\n")
		f.write(str(actionDB[ttl][2]) + "\n")
		f.close()
		
		# Record tabular data for the HTML page...
# 		print 'ttl: ', ttl
		htitles += [str(actionDB[ttl][0])]
		links += [HTML.link(str(ttl), ("film_detail.php?hash=" + hashstr + "&t=30&mf=20&g=60"))]
		dirs += [str(actionDB[ttl][1])]
		years += [str(actionDB[ttl][3])]
		colors += [str(actionDB[ttl][2])]
		hashes += [hashstr]
		
		# Copy the TITLE.color_lab from ACTIONDIR to WEBDIR/hash
		
		#shutil.copy2((os.path.join(ACTIONDIR,str(ttl),(str(ttl)+".color_lab"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+".color_lab"))))
		
		shutil.copy2((os.path.join(ACTIONDIR,str(ttl),(str(ttl)+"_cfl_hc.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_cfl_hc.pkl"))))
		shutil.copy2((os.path.join(ACTIONDIR,str(ttl),(str(ttl)+"_cfl_hc_full.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_cfl_hc_full.pkl"))))
		try:
			shutil.copy2((os.path.join(ACTIONDIR,str(ttl),(str(ttl)+"_mfccs_hc_full.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_mfccs_hc_full.pkl"))))
		except IOError:
			pass

print len(links)
full_table = [["Title", "Link", "Director", "Year", "Color", "Hash"]]

for i, t in enumerate(links):
	full_table += [[
		htitles[i],
		links[i],
		dirs[i],
		years[i],
		colors[i],
		hashes[i]]]

htmlcode = HTML.table(full_table)
# 	print htmlcode
htmlfile.write('<hr>')
htmlfile.write(htmlcode)
htmlfile.write('<hr>')
htmlfile.close()
