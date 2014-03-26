import glob, os, argparse
from action.suite import *


ACTIONDIR = '/Volumes/ACTION'

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("actiondir")
	args = parser.parse_args()

	print args
	print args.actiondir
	
	if args.actiondir is not None:
		ACTIONDIR = args.actiondir

	# if we have some args, use them

	os.chdir(ACTIONDIR)
	names = [os.path.dirname(file) for file in glob.glob('*/*.mov')]

	# Call the mainfunction that sets up threading.
	for name in names:
		cfl = ColorFeaturesLAB(name, action_dir=ACTIONDIR)
		cfl._write_metadata_to_json()
		del cfl

