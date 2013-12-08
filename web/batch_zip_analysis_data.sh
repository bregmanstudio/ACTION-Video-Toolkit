#!/bin/bash

ACTIONDIR=$1
echo "using:"
echo $ACTIONDIR
echo ""
cd $ACTIONDIR
mkdir ../zips
find . -mindepth 1 -maxdepth 1 -type d | while read f
do
	base=$(basename "$f")
	echo "---"
	echo "! -f ../zips/${base}.zip ??"
if [ ! -f "../zips/${base}.zip" ];
	then
		echo "zip -r ${base}.zip ${base}"
        `zip -r ${base}.zip ${base}`
		echo "mv ${base}.zip ../zips/${base}.zip"
        `mv ${base}.zip ../zips/${base}.zip`
	fi
done
