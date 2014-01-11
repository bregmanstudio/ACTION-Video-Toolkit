import action.action_filmdb as fdb
import action.color_features_lab as color_features_lab
import glob, os, md5, shutil
import HTML

ACTION_DIR = '/Volumes/ACTION/'
WEBDIR = os.path.expanduser('~/Sites/actiondata')

# FILM_DB controls what films are active 
full_db = fdb.FilmDB()
actionDB = full_db.actionDB
actionDirectors = full_db.actionDirectors
titles = set(actionDB)

print len(titles)

html_filestring = os.path.expanduser('~/Sites/action_db.html')
htmlfile = open(html_filestring, 'w')

htitles, clinks, alinks, calinks, dirs, years, colors, lengths, hashes = [], [], [], [], [], [], [], [], []

print os.path.join(ACTION_DIR, '*', '*.color_lab')

for file in glob.glob(os.path.join(ACTION_DIR, '*/*.color_lab')):
	# print os.path.basename( file )
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

		# Copy the TITLE.*_hc_*.pkl files from ACTION_DIR to WEBDIR/hash		
		shutil.copy2((os.path.join(ACTION_DIR,str(ttl),(str(ttl)+"_cfl_hc.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_cfl_hc.pkl"))))
		audioflag = 0
		try:
			shutil.copy2((os.path.join(ACTION_DIR,str(ttl),(str(ttl)+"_mfccs_hc.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_mfccs_hc.pkl"))))
			audioflag = 1
		except IOError:
			pass
		comboflag = 0
		try:
			shutil.copy2((os.path.join(ACTION_DIR,str(ttl),(str(ttl)+"_combo_hc.pkl"))), (os.path.join(WEBDIR,hashstr,(str(ttl)+"_combo_hc.pkl"))))
			comboflag = 1
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
		if comboflag == 1:
			f.write(HTML.link("COMBINED FEATURES", ("film_detail_combo.php?hash=" + hashstr + "&t=30&mf=20&g=60")) + "\n")
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
		cfl = color_features_lab.ColorFeaturesLAB(ttl, action_dir=ACTION_DIR)
		length = cfl.determine_movie_length()
		f.write(str(length) + "\n")
		f.close()
		
		# Record tabular data for the HTML page...
# 		print 'ttl: ', ttl
		htitles += [str(actionDB[ttl][0]).replace("_"," ")]

		clinks += [HTML.link("COLOR FEATURES", ("film_detail.php?hash=" + hashstr + "&t=30&mf=20&g=30"))]
		if audioflag == 1:
			alinks += [HTML.link("AUDIO FEATURES", ("film_detail_audio.php?hash=" + hashstr + "&t=30&mf=20&g=30"))]
		else:
			alinks += ["n/a"]
		if comboflag == 1:
			calinks += [HTML.link("COMBINED FEATURES", ("film_detail_comboo.php?hash=" + hashstr + "&t=30&mf=20&g=30"))]
		else:
			calinks += ["n/a"]
		dirs += [actionDirectors[ str(actionDB[ttl][1]) ][0] ]
		years += [str(actionDB[ttl][3])]
		colors += [cflag]
		lengths += [length]
		hashes += [hashstr]
		

print len(clinks)
print len(alinks)
print len(calinks)
full_table = [["Title", "Color Seg.", "Audio Seg.", "Combo Seg.", "Director", "Year", "Color", "Length (s)", "Hash"]]

for i, t in enumerate(clinks):
	full_table += [[
		htitles[i],
		clinks[i],
		alinks[i],
		calinks[i],
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
