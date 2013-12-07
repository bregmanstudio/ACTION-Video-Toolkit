import action.action_filmdb as fdb
import action.color_features_lab as color_features_lab
import HTML, glob, os, md5, shutil

ACTIONDIR = os.path.expanduser('~/Movies/action')
WEBDIR = os.path.expanduser('~/Sites/actiondata')

# FILM_DB controls what films are active 
full_db = fdb.FilmDB()
actionDB = full_db.actionDB
actionDirectors = full_db.actionDirectors
titles = set(actionDB)

print len(titles)

html_filestring = os.path.expanduser('/Sites/action_db.html')
htmlfile = open(html_filestring, 'w')

htitles, clinks, alinks, dirs, years, colors, lengths, hashes = [], [], [], [], [], [], [], []

for file in glob.glob(os.path.expanduser('~/Movies/action/*/*.color_lab'):
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

		audioflag = 0
		# Copy the TITLE.*_hc_*.pkl files from ACTIONDIR to WEBDIR/hash		
		shutil.copy2((os.path.join(ACTIONDIR,str(ttl),(str(ttl)+"_cfl_hc.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_cfl_hc.pkl"))))
		shutil.copy2((os.path.join(ACTIONDIR,str(ttl),(str(ttl)+"_cfl_hc_full.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_cfl_hc_full.pkl"))))
		try:
			shutil.copy2((os.path.join(ACTIONDIR,str(ttl),(str(ttl)+"_mfccs_hc_full.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_mfccs_hc_full.pkl"))))
			audioflag = 1
		except IOError:
			pass
		
		# Create the text file for the metadata
		txtfile = os.path.join(WEBDIR, hashstr, (str(ttl) + '.txt'))
# 		print txtfile
		f = open(txtfile, 'w')
		
		# Write to text file...
		f.write(hashstr + "\n")
		f.write(str(actionDB[ttl][0]).replace("_"," ") + "\n")
		f.write(HTML.link("COLOR FEATURES", ("film_detail.php?hash=" + hashstr + "&t=30&mf=20&g=60")) + "\n")
		if audioflag == 1:
			f.write(HTML.link("AUDIO FEATURES", ("film_detail_audio.php?hash=" + hashstr + "&t=30&mf=20&g=60")) + "\n")
		else:
			f.write("n/a\n")
		print str(actionDB[ttl][1])
		f.write(str(actionDirectors[ str(actionDB[ttl][1]) ][0] ) + "\n")
		f.write(str(actionDB[ttl][3]) + "\n")
		if actionDB[ttl][2] == 1:
			cflag = "Color"
		else:
			cflag = "B/W"
		f.write(str(cflag) + "\n")
		cfl = color_features_lab.ColorFeaturesLAB(ttl)
		length = cfl.determine_movie_length()
		f.write(str(length) + "\n")
		f.close()
		
		# Record tabular data for the HTML page...
# 		print 'ttl: ', ttl
		htitles += [str(actionDB[ttl][0]).replace("_"," ")]

		clinks += [HTML.link("COLOR FEATURES", ("film_detail.php?hash=" + hashstr + "&t=30&mf=20&g=60"))]
		if audioflag == 1:
			alinks += [HTML.link("AUDIO FEATURES", ("film_detail_audio.php?hash=" + hashstr + "&t=30&mf=20&g=60"))]
		else:
			alinks += ["n/a"]
		dirs += [actionDirectors[ str(actionDB[ttl][1]) ][0] ]
		years += [str(actionDB[ttl][3])]
		colors += [cflag]
		lengths += [length]
		hashes += [hashstr]
		

print len(clinks)
print len(alinks)
full_table = [["Title", "Color Seg.", "Audio Seg.", "Director", "Year", "Color", "Length (s)", "Hash"]]

for i, t in enumerate(clinks):
	full_table += [[
		htitles[i],
		clinks[i],
		alinks[i],
		dirs[i],
		years[i],
		colors[i],
		lengths[i],
		hashes[i]]]

htmlcode = HTML.table(full_table)
# 	print htmlcode
htmlfile.write('<hr>')
htmlfile.write(htmlcode)
htmlfile.write('<hr>')
htmlfile.close()
