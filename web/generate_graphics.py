import glob, os

# iterate through the server hashed dirs
for file in glob.glob('/Library/WebServer/Documents/actiondata/*'):
	
	# get the hash/dir name
	hashdirname = os.path.basename(file)
	
	print os.path.join('/Library/WebServer/Documents/actiondata/',hashdirname,'*.txt')
	for textfile in glob.glob(os.path.join('/Library/WebServer/Documents/actiondata/',hashdirname,'*.txt')):
		titlestr = os.path.splitext(os.path.basename(textfile))[0]

	# launch autosegmenter with the
	
	os.system("/Library/WebServer/Documents/autosegmenter_cflab.py -s {0} -f {1}".format(hashdirname, titlestr))

	os.system("/Library/WebServer/Documents/autosegmenter_mfccs.py -s {0} -f {1} -t 25".format(hashdirname, titlestr))

	os.system("/Library/WebServer/Documents/autosegmenter_combo.py -s {0} -f {1}".format(hashdirname, titlestr))
